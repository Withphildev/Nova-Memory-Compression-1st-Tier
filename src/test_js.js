const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { compress, detectMode, splitPunctuation } = require("../tester/app.js");

function parseCsv(text) {
    const rows = [];
    let row = [];
    let field = "";
    let quoted = false;

    for (let index = 0; index < text.length; index += 1) {
        const character = text[index];
        if (quoted) {
            if (character === '"' && text[index + 1] === '"') {
                field += '"';
                index += 1;
            } else if (character === '"') {
                quoted = false;
            } else {
                field += character;
            }
        } else if (character === '"') {
            quoted = true;
        } else if (character === ",") {
            row.push(field);
            field = "";
        } else if (character === "\n") {
            row.push(field.replace(/\r$/, ""));
            rows.push(row);
            row = [];
            field = "";
        } else {
            field += character;
        }
    }

    if (field || row.length) {
        row.push(field.replace(/\r$/, ""));
        rows.push(row);
    }
    return rows;
}

assert.equal(
    compress("the red car was driving down the road", "compact"),
    "red car driving down road"
);
assert.equal(
    compress("Nova smiled as the data flowed in.", "expressive"),
    "Nova smiled as data flowed in"
);
assert.equal(detectMode('{"status":"active"}'), "compact");
assert.equal(detectMode("ERROR: database unavailable"), "compact");
assert.equal(detectMode("This information matters."), "expressive");
assert.deepEqual(splitPunctuation("“answer?”"), {
    leading: "“",
    cleanedWord: "answer",
    trailing: "?”"
});

const fixturePath = path.join(__dirname, "..", "data", "memory_compression_comparison_v1.csv");
const fixtureRows = parseCsv(fs.readFileSync(fixturePath, "utf8").replace(/^\uFEFF/, ""));
const [header, ...benchmarks] = fixtureRows;
const originalIndex = header.indexOf("Original");
const compactIndex = header.indexOf("Compressed");
const expressiveIndex = header.indexOf("Restored Compression");

assert.notEqual(originalIndex, -1);
assert.notEqual(compactIndex, -1);
assert.notEqual(expressiveIndex, -1);
assert.equal(benchmarks.length, 100);

for (const [index, row] of benchmarks.entries()) {
    const label = `historical CSV row ${index + 2}`;
    assert.equal(compress(row[originalIndex], "compact"), row[compactIndex], `${label} compact`);
    assert.equal(compress(row[originalIndex], "expressive"), row[expressiveIndex], `${label} expressive`);
}

console.log(`JavaScript compression tests passed (${benchmarks.length} historical rows).`);
