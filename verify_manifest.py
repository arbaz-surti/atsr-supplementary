#!/usr/bin/env python3
"""Verify the integrity of the ATSR reproducibility archive.

Two checks, both from the archive root:

1. Every path listed in MANIFEST-SHA256.txt exists and hashes to the recorded value,
   and no archived file is missing from the manifest.
2. Every hash that the study's own records committed to before or during the study
   (protocol lock, generation audit, kit manifest, extraction manifest, analysis
   manifest) still matches the corresponding archived file.

Run with --write to regenerate MANIFEST-SHA256.txt (maintainer use only).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "MANIFEST-SHA256.txt"
EXCLUDE_DIRS = {".git", ".venv", "__pycache__"}
EXCLUDE_FILES = {".DS_Store", ".env", "MANIFEST-SHA256.txt"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archived_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or rel.name in EXCLUDE_FILES:
            continue
        if rel.suffix in {".pyc", ".pyo"}:
            continue
        files.append(rel)
    return sorted(files, key=lambda p: p.as_posix())


def write_manifest() -> None:
    lines = [f"{sha256(ROOT / rel)}  {rel.as_posix()}" for rel in archived_files()]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST.name}: {len(lines)} files")


def check_manifest(errors: list[str]) -> int:
    if not MANIFEST.exists():
        errors.append("MANIFEST-SHA256.txt is missing")
        return 0
    listed: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, rel = line.partition("  ")
        listed[rel] = digest
    present = {rel.as_posix() for rel in archived_files()}
    for rel, digest in listed.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"manifest lists a missing file: {rel}")
        elif sha256(path) != digest:
            errors.append(f"hash mismatch: {rel}")
    for rel in sorted(present - set(listed)):
        errors.append(f"archived file not in manifest: {rel}")
    return len(listed)


def expect(errors: list[str], rel: str, digest: str, source: str) -> int:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"{source}: file missing: {rel}")
    elif sha256(path) != digest:
        errors.append(f"{source}: recorded hash does not match archived file: {rel}")
    return 1


def check_recorded_hashes(errors: list[str]) -> int:
    n = 0
    lock = json.loads((ROOT / "research/revision_protocol/protocol-lock.json").read_text())
    for rel, digest in lock["files"].items():
        n += expect(errors, rel, digest, "protocol-lock.json")

    gen_dir = "research/revision_outputs/ATSR-SREP-R2-v1.0"
    audit = json.loads((ROOT / gen_dir / "generation-audit.json").read_text())
    for name, digest in audit["artifact_sha256"].items():
        n += expect(errors, f"{gen_dir}/{name}", digest, "generation-audit.json")

    ext_dir = "research/revision_analysis/ATSR-SREP-R2-v1.0-renewed-ratings-2026-09-17"
    ext = json.loads((ROOT / ext_dir / "extraction-manifest.json").read_text())
    n += expect(errors, f"{ext_dir}/{ext['ratings_file']}", ext["ratings_sha256"], "extraction-manifest.json")

    op_dir = "research/revision_analysis/ATSR-SREP-R2-v1.0-operative-ratings-2026-09-18"
    op = json.loads((ROOT / op_dir / "analysis-manifest.json").read_text())
    for name, digest in op["output_hashes"].items():
        n += expect(errors, f"{op_dir}/{name}", digest, "analysis-manifest.json")
    n += expect(errors, f"{ext_dir}/ratings-extracted.csv", op["input_hashes"]["ratings_extracted"], "analysis-manifest.json")
    n += expect(errors, "research/analyze_operative_ratings.py", op["input_hashes"]["analysis_script"], "analysis-manifest.json")

    kit = (ROOT / "research/revision_protocol/ground-truth/kit-manifest.md").read_text(encoding="utf-8")
    row = re.compile(r"^\| `([^`]+)` \|[^|]*\| `([0-9a-f]{64})`", re.MULTILINE)
    for rel, digest in row.findall(kit):
        n += expect(errors, rel, digest, "kit-manifest.md")
    return n


def main() -> int:
    if "--write" in sys.argv:
        write_manifest()
        return 0
    errors: list[str] = []
    listed = check_manifest(errors)
    recorded = check_recorded_hashes(errors)
    if errors:
        print("ARCHIVE VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS manifest: {listed} files match MANIFEST-SHA256.txt")
    print(f"PASS recorded hashes: {recorded} study-record hashes match archived files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
