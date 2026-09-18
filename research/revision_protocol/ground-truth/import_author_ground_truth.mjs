import fs from "node:fs/promises";
import crypto from "node:crypto";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const sourcePath = process.argv[2];
const raterId = process.argv[3] && !process.argv[3].startsWith("--") ? process.argv[3] : "AUTHOR";
const raterFiles = {
  AUTHOR: {
    slug: "author",
    archiveExtension: "tsv",
  },
  "PRACTITIONER-01": {
    slug: "practitioner-01",
    archiveExtension: "md",
  },
  "PRACTITIONER-02": {
    slug: "practitioner-02",
    archiveExtension: "md",
  },
};
if (!raterFiles[raterId]) throw new Error(`Unsupported rater ID: ${raterId}`);
const { slug, archiveExtension } = raterFiles[raterId];
const templatePath = `outputs/b3-evaluation-kit/${slug}-ground-truth.xlsx`;
const outputPath = `outputs/b3-evaluation-kit/${slug}-ground-truth-completed.xlsx`;
const archivePath = `research/revision_protocol/ground-truth/submissions/${slug}-ground-truth-2026-09-14.${archiveExtension}`;
const previewDir = ".codex-tmp/b3-xlsx/previews";
const inspectOnly = process.argv.includes("--inspect-only");

if (!sourcePath || sourcePath === "--inspect-only") {
  throw new Error("Usage: node import_author_ground_truth.mjs <submission> [AUTHOR|PRACTITIONER-01|PRACTITIONER-02] [--inspect-only]");
}

const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const templateBytes = await fs.readFile(templatePath);
const sourceBytes = await fs.readFile(sourcePath);
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(templatePath));

const before = await workbook.inspect({
  kind: "table",
  range: "Ground Truth!A4:M22",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 13,
  tableMaxCellChars: 100,
});
console.log(before.ndjson);

await fs.mkdir(previewDir, { recursive: true });
const beforePreview = await workbook.render({
  sheetName: "Ground Truth",
  range: "A1:M22",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${previewDir}/${slug}-ground-truth-before.png`, new Uint8Array(await beforePreview.arrayBuffer()));

if (inspectOnly) process.exit(0);

const sourceText = sourceBytes.toString("utf8").replace(/^\uFEFF/, "");
const sourceLines = sourceText.split(/\r?\n/).filter((line) => line.trim());
let rows;
if (sourceLines.every((line) => line.trim().startsWith("|") && line.trim().endsWith("|"))) {
  rows = sourceLines.map((line) => line.trim().slice(1, -1).split("|").map((cell) => cell.trim()));
  if (rows[1]?.every((cell) => /^:?-{3,}:?$/.test(cell))) rows.splice(1, 1);
  rows = rows.map((row, rowIndex) => row.map((cell, colIndex) => {
    if (rowIndex > 0 && colIndex === 0) return cell.replace(/^\*\*(.+)\*\*$/, "$1");
    return cell.replace(/`([^`]+)`/g, "$1");
  }));
} else {
  rows = sourceLines.map((line) => line.split("\t"));
}
const expectedHeader = [
  "Spec ID",
  "Coverage depth",
  "Essential functional scope",
  "Essential smoke scope",
  "Essential regression scope",
  "Essential integration scope",
  "Essential exploratory scope",
  "Essential clarification needs",
  "Depth rationale",
  "Implicit domain knowledge",
  "Notes / assumptions",
];
if (JSON.stringify(rows[0]) !== JSON.stringify(expectedHeader)) {
  throw new Error(`Unexpected header: ${JSON.stringify(rows[0])}`);
}
if (rows.length !== 19) throw new Error(`Expected header plus 18 records; found ${rows.length} rows`);
for (const [index, row] of rows.slice(1).entries()) {
  if (row.length !== 11) throw new Error(`Row ${index + 2} has ${row.length} fields; expected 11`);
  if (row.some((value) => !value.trim())) throw new Error(`Row ${index + 2} contains a blank required field`);
  if (!new Set(["LOW", "MEDIUM", "HIGH"]).has(row[1])) throw new Error(`Invalid depth in row ${index + 2}: ${row[1]}`);
}

const sheet = workbook.worksheets.getItem("Ground Truth");
const workbookRaterId = workbook.worksheets.getItem("Read First").getRange("B6").values[0][0];
if (workbookRaterId !== raterId) {
  throw new Error(`Rater ID mismatch. Workbook=${workbookRaterId} Requested=${raterId}`);
}
const workbookSpecIds = sheet.getRange("A5:A22").values.flat();
const submittedSpecIds = rows.slice(1).map((row) => row[0]);
if (JSON.stringify(workbookSpecIds) !== JSON.stringify(submittedSpecIds)) {
  throw new Error(`Spec ID/order mismatch. Workbook=${workbookSpecIds.join(",")} Submission=${submittedSpecIds.join(",")}`);
}

sheet.getRange("C5:L22").values = rows.slice(1).map((row) => row.slice(1));
workbook.recalculate();

const after = await workbook.inspect({
  kind: "table",
  range: "Ground Truth!A4:M22",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 13,
  tableMaxCellChars: 100,
});
const summary = await workbook.inspect({
  kind: "table",
  range: "Read First!A5:B10",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 2,
});
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: `${raterId} completed workbook formula error scan`,
});
console.log(after.ndjson);
console.log(summary.ndjson);
console.log(errors.ndjson);

const afterPreview = await workbook.render({
  sheetName: "Ground Truth",
  range: "A1:M22",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${previewDir}/${slug}-ground-truth-completed.png`, new Uint8Array(await afterPreview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
await fs.mkdir("research/revision_protocol/ground-truth/submissions", { recursive: true });
await fs.writeFile(archivePath, sourceBytes);

const savedWorkbook = await SpreadsheetFile.importXlsx(await FileBlob.load(outputPath));
const savedSheet = savedWorkbook.worksheets.getItem("Ground Truth");
const savedValues = savedSheet.getRange("C5:L22").values;
const expectedValues = rows.slice(1).map((row) => row.slice(1));
if (JSON.stringify(savedValues) !== JSON.stringify(expectedValues)) {
  throw new Error(`Saved workbook values do not exactly match the normalized ${raterId} judgments`);
}
savedWorkbook.recalculate();
const savedStatus = savedSheet.getRange("M5:M22").values.flat();
if (savedStatus.some((value) => value !== "Complete")) {
  throw new Error(`Saved workbook has incomplete rows: ${JSON.stringify(savedStatus)}`);
}
const savedSummary = await savedWorkbook.inspect({
  kind: "table",
  range: "Read First!A5:B10",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 2,
});
const savedErrors = await savedWorkbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: `saved ${raterId} completed workbook formula error scan`,
});
console.log(savedSummary.ndjson);
console.log(savedErrors.ndjson);

const outputBytes = await fs.readFile(outputPath);
console.log(JSON.stringify({
  sourcePath,
  sourceSha256: sha256(sourceBytes),
  templateSha256: sha256(templateBytes),
  outputPath,
  outputSha256: sha256(outputBytes),
  archivePath,
  archiveSha256: sha256(await fs.readFile(archivePath)),
  raterId,
}, null, 2));
