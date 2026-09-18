#!/usr/bin/env python3
"""Extract visible rating values from the three renewed Ratings.html files.

The extractor deliberately retains the blinded identifiers and does not join model,
condition, run, or work identifiers. It validates the visible score/status fields,
writes one combined CSV, and records hashes and aggregate checks in a JSON manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path


DIMENSIONS = (
    "completeness",
    "specificity",
    "risk_calibration",
    "integration_awareness",
    "clarification_flag_quality",
)

VISIBLE_HEADERS = (
    "Blind item ID",
    "Spec ID",
    "Specification",
    "Candidate recommendation",
    "Observation status",
    "Completeness",
    "Specificity",
    "Risk Calibration",
    "Integration Awareness",
    "Clarification Flag Quality",
    "Total",
    "Rating status",
)

CSV_HEADERS = (
    "rater_id",
    "packet_position",
    "blind_item_id",
    "spec_id",
    "observation_status",
    *DIMENSIONS,
    "total_score",
    "rating_status",
)


class RatingsTableParser(HTMLParser):
    """Minimal parser for Google Sheets-style exported HTML tables."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_td = False
        self._cell_parts: list[str] = []
        self._row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "tr":
            self._row = []
        elif tag == "td":
            self._in_td = True
            self._cell_parts = []
        elif tag == "br" and self._in_td:
            self._cell_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td":
            value = " ".join("".join(self._cell_parts).split())
            self._row.append(value)
            self._in_td = False
        elif tag == "tr" and self._row:
            self.rows.append(self._row)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_packet(rater_id: str, path: Path) -> list[dict[str, object]]:
    parser = RatingsTableParser()
    parser.feed(path.read_text(encoding="utf-8"))

    if list(VISIBLE_HEADERS) not in parser.rows:
        raise ValueError(f"{path}: expected visible Ratings headers were not found")

    source_rows = [row for row in parser.rows if row and row[0].startswith("RATE-")]
    records: list[dict[str, object]] = []

    for position, row in enumerate(source_rows, start=1):
        if len(row) != len(VISIBLE_HEADERS):
            raise ValueError(
                f"{path}: packet row {position} has {len(row)} visible cells; expected 12"
            )

        scores_text = row[5:10]
        total_text = row[10]
        scorable = row[4] == "Scorable"

        if scorable:
            if not all(scores_text) or not total_text:
                raise ValueError(f"{path}: scorable row {position} has a blank score or total")
            scores = [int(value) for value in scores_text]
            total = int(total_text)
            if any(score < 1 or score > 5 for score in scores):
                raise ValueError(f"{path}: row {position} has a score outside 1-5")
            if total != sum(scores):
                raise ValueError(f"{path}: row {position} total does not equal its five scores")
            if row[11] != "Complete":
                raise ValueError(f"{path}: completed scorable row {position} is not Complete")
        else:
            if any(scores_text) or total_text:
                raise ValueError(f"{path}: non-scorable row {position} contains a score")
            scores = [None] * 5
            total = None
            if row[11] != "Not scorable":
                raise ValueError(f"{path}: non-scorable row {position} has an unexpected status")

        record: dict[str, object] = {
            "rater_id": rater_id,
            "packet_position": position,
            "blind_item_id": row[0],
            "spec_id": row[1],
            "observation_status": row[4],
            "total_score": total,
            "rating_status": row[11],
        }
        record.update(dict(zip(DIMENSIONS, scores, strict=True)))
        records.append(record)

    return records


def load_baseline(path: Path) -> dict[tuple[str, str], dict[str, object]]:
    baseline: dict[tuple[str, str], dict[str, object]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            scores = record["scores"]
            baseline[(record["rater_id"], record["blind_item_id"])] = {
                "spec_id": record["spec_id"],
                "scores": None
                if scores is None
                else tuple(scores[dimension] for dimension in DIMENSIONS),
                "total_score": record["total_score"],
            }
    return baseline


def summarize_packet(records: list[dict[str, object]]) -> dict[str, object]:
    scorable = [record for record in records if record["observation_status"] == "Scorable"]
    failures = [record for record in records if record["observation_status"] != "Scorable"]
    return {
        "observations": len(records),
        "scorable": len(scorable),
        "structural_failures": len(failures),
        "rating_statuses": dict(Counter(str(record["rating_status"]) for record in records)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author", required=True, type=Path)
    parser.add_argument("--practitioner-01", required=True, type=Path)
    parser.add_argument("--practitioner-02", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()

    sources = {
        "AUTHOR": args.author,
        "PRACTITIONER-01": args.practitioner_01,
        "PRACTITIONER-02": args.practitioner_02,
    }

    by_rater = {rater_id: parse_packet(rater_id, path) for rater_id, path in sources.items()}
    records = [record for rater_id in sources for record in by_rater[rater_id]]

    keys = [(str(record["rater_id"]), str(record["blind_item_id"])) for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate (rater_id, blind_item_id) keys found")

    comparison: dict[str, object] | None = None
    if args.baseline:
        baseline = load_baseline(args.baseline)
        if set(keys) != set(baseline):
            raise ValueError("Renewed and baseline rating key sets do not match")
        if any(
            record["spec_id"] != baseline[(str(record["rater_id"]), str(record["blind_item_id"]))]["spec_id"]
            for record in records
        ):
            raise ValueError("A renewed record has a different specification assignment")

        by_rater_comparison: dict[str, object] = {}
        for rater_id, packet_records in by_rater.items():
            scored = [record for record in packet_records if record["observation_status"] == "Scorable"]
            changed_rows = 0
            total_matches = 0
            dimension_changes = Counter({dimension: 0 for dimension in DIMENSIONS})
            for record in scored:
                old = baseline[(rater_id, str(record["blind_item_id"]))]
                renewed_scores = tuple(record[dimension] for dimension in DIMENSIONS)
                old_scores = old["scores"]
                if renewed_scores != old_scores:
                    changed_rows += 1
                if record["total_score"] == old["total_score"]:
                    total_matches += 1
                if old_scores is not None:
                    for index, dimension in enumerate(DIMENSIONS):
                        if renewed_scores[index] != old_scores[index]:
                            dimension_changes[dimension] += 1
            by_rater_comparison[rater_id] = {
                "scorable_rows": len(scored),
                "score_rows_changed": changed_rows,
                "score_rows_unchanged": len(scored) - changed_rows,
                "total_score_matches": total_matches,
                "dimension_score_changes": dict(dimension_changes),
            }
        comparison = {
            "baseline_file": str(args.baseline),
            "same_rater_blind_id_set": True,
            "same_specification_assignments": True,
            "by_rater": by_rater_comparison,
        }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    ratings_path = args.output_dir / "ratings-extracted.csv"
    with ratings_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(records)

    manifest = {
        "extraction_date": date.today().isoformat(),
        "dataset_label": "renewed-ratings-2026-09-17",
        "status": "staged extraction; original locked ratings and analysis unchanged",
        "source_files": {
            rater_id: {
                "source_folder": path.parent.name,
                "file_name": path.name,
                "sha256": sha256(path),
                **summarize_packet(by_rater[rater_id]),
            }
            for rater_id, path in sources.items()
        },
        "combined_checks": {
            "records": len(records),
            "scorable_rating_records": sum(
                record["observation_status"] == "Scorable" for record in records
            ),
            "structural_failure_assignments": sum(
                record["observation_status"] != "Scorable" for record in records
            ),
            "unique_rater_blind_item_keys": len(set(keys)),
            "score_range": [1, 5],
            "all_scorable_totals_reconciled": True,
            "all_structural_failure_scores_blank": True,
        },
        "visible_html_limit": (
            "Ratings.html exposes columns A-K and M; hidden rationale column L is not present "
            "and was not extracted."
        ),
        "baseline_comparison": comparison,
        "ratings_file": ratings_path.name,
        "ratings_sha256": sha256(ratings_path),
    }
    manifest_path = args.output_dir / "extraction-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"ratings": str(ratings_path), "manifest": str(manifest_path), **manifest["combined_checks"]}, indent=2))


if __name__ == "__main__":
    main()
