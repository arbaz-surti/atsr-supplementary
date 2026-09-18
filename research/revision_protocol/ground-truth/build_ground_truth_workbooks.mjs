import fs from "node:fs/promises";
import crypto from "node:crypto";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const protocolId = "ATSR-SREP-R2-v1.0";
const expectedDatasetHash = "48d94cce163cf21efa712939bd4334b0a89260434aafe0d83a00cbd2dd3856f0";
const datasetPath = "supplementary/data/specifications.json";
const outputDir = "outputs/b3-evaluation-kit";
const previewDir = ".codex-tmp/b3-xlsx/previews";
const font = "Arial";

const datasetBytes = await fs.readFile(datasetPath);
const datasetHash = crypto.createHash("sha256").update(datasetBytes).digest("hex");
if (datasetHash !== expectedDatasetHash) {
  throw new Error(`Dataset hash mismatch: ${datasetHash}`);
}
const specs = JSON.parse(datasetBytes.toString("utf8"));
if (!Array.isArray(specs) || specs.length !== 18) {
  throw new Error(`Expected 18 specifications; found ${specs.length}`);
}

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const colors = {
  navy: "#17365D",
  blue: "#D9EAF7",
  paleBlue: "#EAF2F8",
  amber: "#FFF2CC",
  green: "#E2F0D9",
  red: "#FCE4D6",
  gray: "#E7E6E6",
  darkGray: "#595959",
  white: "#FFFFFF",
  text: "#222222",
};

function styleTitle(sheet, range, title) {
  sheet.getRange(range.split(":")[0]).values = [[title]];
  sheet.getRange(range).format.font = { name: font, size: 14, bold: true, color: colors.navy };
}

function styleHeader(range) {
  range.format = {
    fill: colors.navy,
    font: { name: font, size: 10, bold: true, color: colors.white },
    verticalAlignment: "center",
    horizontalAlignment: "center",
    wrapText: true,
    borders: { preset: "inside", style: "thin", color: colors.white },
  };
}

function styleBody(range) {
  range.format.font = { name: font, size: 10, color: colors.text };
  range.format.verticalAlignment = "top";
  range.format.wrapText = true;
  range.format.borders = {
    insideHorizontal: { style: "thin", color: "#D9E1F2" },
    bottom: { style: "thin", color: "#D9E1F2" },
  };
}

function writeReadFirst(workbook, raterId) {
  const sheet = workbook.worksheets.add("Read First");
  sheet.showGridLines = false;
  sheet.tabColor = colors.navy;
  styleTitle(sheet, "A2:H2", "B3 independent ground-truth worksheet");
  sheet.getRange("A3:H3").format.borders = { bottom: { style: "thin", color: colors.navy } };
  sheet.getRange("A5:B10").values = [
    ["Protocol", protocolId],
    ["Rater ID", raterId],
    ["Specifications", 18],
    ["Rows complete", null],
    ["Rows remaining", null],
    ["Dataset SHA-256", datasetHash],
  ];
  sheet.getRange("A5:A10").format.font = { name: font, size: 10, bold: true, color: colors.darkGray };
  sheet.getRange("B5:B10").format.font = { name: font, size: 10, color: colors.text };
  sheet.getRange("B8").formulas = [["=COUNTIFS('Ground Truth'!M5:M22,\"Complete\")"]];
  sheet.getRange("B9").formulas = [["=18-B8"]];
  sheet.getRange("B8:B9").format.numberFormat = "0";

  sheet.getRange("A12").values = [["Instructions"]];
  sheet.getRange("A12:H12").format = {
    fill: colors.blue,
    font: { name: font, size: 10, bold: true, color: colors.navy },
    borders: { bottom: { style: "thin", color: colors.navy } },
  };
  const instructions = [
    "Work independently and review all 18 specifications before discussing judgments.",
    "Do not view AI outputs, historical scores, historical author ground truth, or another rater's worksheet.",
    "Enter one LOW, MEDIUM, or HIGH depth judgment and a short rationale for each specification.",
    "Enter semicolon-separated essential elements for functional, smoke, regression, integration, exploratory, and clarification scope.",
    "Use NONE when a category is genuinely irrelevant. Do not leave required fields blank.",
    "If an essential element depends on professional knowledge not explicit in the specification, record the inferential link under Implicit domain knowledge.",
    "Use Notes for assumptions or uncertainty. The Status column calculates automatically.",
    "Return the completed workbook to the researcher without renaming worksheets or changing Spec IDs.",
  ];
  sheet.getRange("A13:H20").values = instructions.map((x, i) => [`${i + 1}. ${x}`, null, null, null, null, null, null, null]);
  sheet.getRange("A13:H20").format.font = { name: font, size: 10, color: colors.text };
  sheet.getRange("A13:H20").format.wrapText = true;
  sheet.getRange("A13:H20").format.rowHeight = 52;
  sheet.getRange("A22").values = [["Stop after completing this workbook. Model-output rating begins only after consensus and rubric freeze."]];
  sheet.getRange("A22:H22").format = {
    fill: colors.amber,
    font: { name: font, size: 10, bold: true, color: "#7F6000" },
    wrapText: true,
  };
  sheet.getRange("A22:H22").format.rowHeight = 34;
  sheet.getRange("A1:H25").format.font.name = font;
  sheet.getRange("A:A").format.columnWidth = 42;
  sheet.getRange("B:B").format.columnWidth = 72;
  sheet.getRange("C:H").format.columnWidth = 12;
  return sheet;
}

function writeGroundTruth(workbook) {
  const sheet = workbook.worksheets.add("Ground Truth");
  sheet.showGridLines = false;
  sheet.tabColor = "#5B9BD5";
  styleTitle(sheet, "A2:M2", "Independent judgments for 18 specifications");
  sheet.getRange("C3").values = [["Yellow cells require participant input. Use semicolons between atomic elements; enter NONE when a category is irrelevant."]];
  sheet.getRange("A3:M3").format = { font: { name: font, size: 10, italic: true, color: colors.darkGray }, wrapText: false };
  const headers = [
    "Spec ID", "Title", "Coverage depth", "Essential functional scope",
    "Essential smoke scope", "Essential regression scope", "Essential integration scope",
    "Essential exploratory scope", "Essential clarification needs", "Depth rationale",
    "Implicit domain knowledge", "Notes or assumptions", "Status",
  ];
  sheet.getRange("A4:M4").values = [headers];
  styleHeader(sheet.getRange("A4:M4"));
  sheet.getRange("A5:M22").values = specs.map((s) => [
    s.spec_id, s.title, null, null, null, null, null, null, null, null, null, null, null,
  ]);
  for (let row = 5; row <= 22; row += 1) {
    sheet.getRange(`M${row}`).formulas = [[`=IF(COUNTA(C${row}:K${row})=9,"Complete","Missing fields")`]];
  }
  styleBody(sheet.getRange("A5:M22"));
  sheet.getRange("A5:B22").format.fill = colors.paleBlue;
  sheet.getRange("C5:L22").format.fill = colors.amber;
  sheet.getRange("M5:M22").format.fill = colors.gray;
  sheet.getRange("C5:C22").dataValidation = { rule: { type: "list", values: ["LOW", "MEDIUM", "HIGH"] } };
  sheet.getRange("M5:M22").conditionalFormats.add("containsText", {
    text: "Missing fields",
    format: { fill: colors.red, font: { bold: true, color: "#9C0006" } },
  });
  sheet.getRange("M5:M22").conditionalFormats.add("containsText", {
    text: "Complete",
    format: { fill: colors.green, font: { bold: true, color: "#375623" } },
  });
  sheet.getRange("A5:A22").format.horizontalAlignment = "center";
  sheet.getRange("C5:C22").format.horizontalAlignment = "center";
  sheet.getRange("M5:M22").format.horizontalAlignment = "center";
  sheet.getRange("A4:M4").format.rowHeight = 45;
  sheet.getRange("A5:M22").format.rowHeight = 78;
  const widths = [12, 34, 16, 34, 30, 34, 34, 32, 34, 32, 34, 30, 16];
  widths.forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, 23, 1).format.columnWidth = width;
  });
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(2);
  return sheet;
}

function writeSpecifications(workbook) {
  const sheet = workbook.worksheets.add("Specifications");
  sheet.showGridLines = false;
  styleTitle(sheet, "A2:F2", "Evaluation specifications");
  sheet.getRange("B3").values = [[`Frozen source hash: ${datasetHash}. Historical ground-truth fields are deliberately excluded.`]];
  sheet.getRange("A3:F3").format = { font: { name: font, size: 10, italic: true, color: colors.darkGray }, wrapText: false };
  sheet.getRange("A4:F4").values = [["Spec ID", "Title", "Change type", "System area", "Description", "Acceptance criteria"]];
  styleHeader(sheet.getRange("A4:F4"));
  sheet.getRange("A5:F22").values = specs.map((s) => [
    s.spec_id,
    s.title,
    s.change_type,
    s.system_area,
    s.description,
    Array.isArray(s.acceptance_criteria) && s.acceptance_criteria.length
      ? s.acceptance_criteria.map((x, i) => `${i + 1}. ${x}`).join("\n")
      : "None supplied",
  ]);
  styleBody(sheet.getRange("A5:F22"));
  sheet.getRange("A5:A22").format.horizontalAlignment = "center";
  sheet.getRange("A4:F4").format.rowHeight = 32;
  sheet.getRange("A5:F22").format.rowHeight = 112;
  [12, 35, 27, 35, 72, 65].forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, 23, 1).format.columnWidth = width;
  });
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(1);
  return sheet;
}

async function createRaterWorkbook(raterId, fileName) {
  const workbook = Workbook.create();
  writeReadFirst(workbook, raterId);
  writeGroundTruth(workbook);
  writeSpecifications(workbook);
  workbook.recalculate();

  const readCheck = await workbook.inspect({
    kind: "table",
    range: "Read First!A2:B10",
    include: "values,formulas",
    tableMaxRows: 12,
    tableMaxCols: 4,
  });
  const gtCheck = await workbook.inspect({
    kind: "table",
    range: "Ground Truth!A4:M7",
    include: "values,formulas",
    tableMaxRows: 6,
    tableMaxCols: 13,
  });
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 100 },
    summary: `${raterId} formula error scan`,
  });
  console.log(readCheck.ndjson);
  console.log(gtCheck.ndjson);
  console.log(errors.ndjson);

  for (const sheetName of ["Read First", "Ground Truth", "Specifications"]) {
    const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
    const safeName = `${raterId.toLowerCase()}-${sheetName.toLowerCase().replaceAll(" ", "-")}.png`;
    await fs.writeFile(`${previewDir}/${safeName}`, new Uint8Array(await preview.arrayBuffer()));
  }
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(`${outputDir}/${fileName}`);
}

function writeAdjudicationReadFirst(workbook) {
  const sheet = workbook.worksheets.add("Read First");
  sheet.showGridLines = false;
  sheet.tabColor = colors.navy;
  styleTitle(sheet, "A2:H2", "B3 consensus adjudication workbook");
  sheet.getRange("A3:H3").format.borders = { bottom: { style: "thin", color: colors.navy } };
  sheet.getRange("A5:B11").values = [
    ["Protocol", protocolId],
    ["Dataset SHA-256", datasetHash],
    ["Independent workbooks", 3],
    ["Depth rows complete", null],
    ["Scope rows complete", null],
    ["Expected depth rows", 18],
    ["Expected scope rows", 108],
  ];
  sheet.getRange("B8").formulas = [["=COUNTIFS(Depth!J5:J22,\"Complete\")"]];
  sheet.getRange("B9").formulas = [["=COUNTIFS(Scope!L5:L112,\"Complete\")"]];
  sheet.getRange("A5:A11").format.font = { name: font, size: 10, bold: true, color: colors.darkGray };
  sheet.getRange("B5:B11").format.font = { name: font, size: 10, color: colors.text };
  sheet.getRange("A13").values = [["Adjudication sequence"]];
  sheet.getRange("A13:H13").format = { fill: colors.blue, font: { name: font, size: 10, bold: true, color: colors.navy } };
  const steps = [
    "Import the three de-identified independent judgments without altering their wording.",
    "Review disagreements only after every independent workbook is locked and copied.",
    "Agree one consensus depth for each specification and one atomic list for each scope category.",
    "Record why a disagreement was resolved and whether consensus content is explicit, implicit, or mixed.",
    "Do not force unanimity. Preserve dissent in the decision-reason field where it matters.",
    "Complete all rows, export the consensus reference, and hash it together with the final rubric.",
    "Only then generate blinded model-output rating packets.",
  ];
  sheet.getRange("A14:H20").values = steps.map((x, i) => [`${i + 1}. ${x}`, null, null, null, null, null, null, null]);
  sheet.getRange("A14:H20").format = { font: { name: font, size: 10, color: colors.text }, wrapText: true, rowHeight: 52 };
  sheet.getRange("A22").values = [["Do not copy model outputs or ratings into this workbook."]];
  sheet.getRange("A22:H22").format = { fill: colors.amber, font: { name: font, size: 10, bold: true, color: "#7F6000" } };
  sheet.getRange("A:A").format.columnWidth = 31;
  sheet.getRange("B:B").format.columnWidth = 72;
  sheet.getRange("C:H").format.columnWidth = 12;
}

function writeDepthAdjudication(workbook) {
  const sheet = workbook.worksheets.add("Depth");
  sheet.showGridLines = false;
  styleTitle(sheet, "A2:J2", "Coverage-depth adjudication");
  sheet.getRange("C3").values = [["Copy independent judgments exactly. Yellow cells are adjudication inputs; Status calculates automatically."]];
  sheet.getRange("A3:J3").format = { font: { name: font, size: 10, italic: true, color: colors.darkGray } };
  sheet.getRange("A4:J4").values = [[
    "Spec ID", "Title", "AUTHOR depth", "PRACTITIONER-01 depth", "PRACTITIONER-02 depth",
    "Consensus depth", "Decision reason", "Adjudicator initials", "Decision date", "Status",
  ]];
  styleHeader(sheet.getRange("A4:J4"));
  sheet.getRange("A5:J22").values = specs.map((s) => [s.spec_id, s.title, null, null, null, null, null, null, null, null]);
  for (let row = 5; row <= 22; row += 1) {
    sheet.getRange(`J${row}`).formulas = [[`=IF(COUNTA(C${row}:I${row})=7,"Complete","Missing fields")`]];
  }
  styleBody(sheet.getRange("A5:J22"));
  sheet.getRange("A5:B22").format.fill = colors.paleBlue;
  sheet.getRange("C5:E22").format.fill = "#F2F2F2";
  sheet.getRange("F5:I22").format.fill = colors.amber;
  sheet.getRange("J5:J22").format.fill = colors.gray;
  for (const range of ["C5:C22", "D5:D22", "E5:E22", "F5:F22"]) {
    sheet.getRange(range).dataValidation = { rule: { type: "list", values: ["LOW", "MEDIUM", "HIGH"] } };
  }
  sheet.getRange("I5:I22").setNumberFormat("yyyy-mm-dd");
  sheet.getRange("J5:J22").conditionalFormats.add("containsText", { text: "Missing fields", format: { fill: colors.red, font: { bold: true, color: "#9C0006" } } });
  sheet.getRange("J5:J22").conditionalFormats.add("containsText", { text: "Complete", format: { fill: colors.green, font: { bold: true, color: "#375623" } } });
  [12, 36, 17, 21, 21, 18, 45, 20, 16, 16].forEach((width, index) => sheet.getRangeByIndexes(0, index, 23, 1).format.columnWidth = width);
  sheet.getRange("A4:J4").format.rowHeight = 43;
  sheet.getRange("A5:J22").format.rowHeight = 58;
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(2);
}

function writeScopeAdjudication(workbook) {
  const sheet = workbook.worksheets.add("Scope");
  sheet.showGridLines = false;
  styleTitle(sheet, "A2:L2", "Essential-scope adjudication");
  sheet.getRange("C3").values = [["One row represents one specification and scope category. Keep semicolon-separated elements atomic."]];
  sheet.getRange("A3:L3").format = { font: { name: font, size: 10, italic: true, color: colors.darkGray } };
  sheet.getRange("A4:L4").values = [[
    "Spec ID", "Title", "Scope category", "AUTHOR judgment", "PRACTITIONER-01 judgment",
    "PRACTITIONER-02 judgment", "Consensus essential elements", "Evidence basis",
    "Implicit inferential link", "Decision reason", "Adjudicator initials", "Status",
  ]];
  styleHeader(sheet.getRange("A4:L4"));
  const categories = ["Functional", "Smoke", "Regression", "Integration", "Exploratory", "Clarification"];
  const rows = [];
  for (const spec of specs) {
    for (const category of categories) {
      rows.push([spec.spec_id, spec.title, category, null, null, null, null, null, null, null, null, null]);
    }
  }
  sheet.getRange("A5:L112").values = rows;
  for (let row = 5; row <= 112; row += 1) {
    sheet.getRange(`L${row}`).formulas = [[`=IF(COUNTA(D${row}:K${row})=8,"Complete","Missing fields")`]];
  }
  styleBody(sheet.getRange("A5:L112"));
  sheet.getRange("A5:C112").format.fill = colors.paleBlue;
  sheet.getRange("D5:F112").format.fill = "#F2F2F2";
  sheet.getRange("G5:K112").format.fill = colors.amber;
  sheet.getRange("L5:L112").format.fill = colors.gray;
  sheet.getRange("H5:H112").dataValidation = { rule: { type: "list", values: ["Explicit", "Implicit", "Mixed", "Not applicable"] } };
  sheet.getRange("L5:L112").conditionalFormats.add("containsText", { text: "Missing fields", format: { fill: colors.red, font: { bold: true, color: "#9C0006" } } });
  sheet.getRange("L5:L112").conditionalFormats.add("containsText", { text: "Complete", format: { fill: colors.green, font: { bold: true, color: "#375623" } } });
  [12, 34, 16, 34, 34, 34, 40, 18, 34, 36, 20, 16].forEach((width, index) => sheet.getRangeByIndexes(0, index, 113, 1).format.columnWidth = width);
  sheet.getRange("A4:L4").format.rowHeight = 43;
  sheet.getRange("A5:L112").format.rowHeight = 68;
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(3);
}

function writeSpecReference(workbook) {
  writeSpecifications(workbook);
}

async function createAdjudicationWorkbook() {
  const workbook = Workbook.create();
  writeAdjudicationReadFirst(workbook);
  writeDepthAdjudication(workbook);
  writeScopeAdjudication(workbook);
  writeSpecReference(workbook);
  workbook.recalculate();
  const checks = await workbook.inspect({
    kind: "table",
    range: "Depth!A4:J7",
    include: "values,formulas",
    tableMaxRows: 6,
    tableMaxCols: 10,
  });
  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 100 },
    summary: "adjudication formula error scan",
  });
  console.log(checks.ndjson);
  console.log(errors.ndjson);
  for (const sheetName of ["Read First", "Depth", "Scope", "Specifications"]) {
    const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
    const safeName = `adjudication-${sheetName.toLowerCase().replaceAll(" ", "-")}.png`;
    await fs.writeFile(`${previewDir}/${safeName}`, new Uint8Array(await preview.arrayBuffer()));
  }
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(`${outputDir}/consensus-adjudication.xlsx`);
}

await createRaterWorkbook("AUTHOR", "author-ground-truth.xlsx");
await createRaterWorkbook("PRACTITIONER-01", "practitioner-01-ground-truth.xlsx");
await createRaterWorkbook("PRACTITIONER-02", "practitioner-02-ground-truth.xlsx");
await createAdjudicationWorkbook();

console.log(`Created 4 workbooks in ${outputDir}`);
