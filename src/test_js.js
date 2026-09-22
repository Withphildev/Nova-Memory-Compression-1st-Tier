const assert = require("node:assert/strict");
const { compress, detectMode, splitPunctuation } = require("../tester/app.js");

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

console.log("JavaScript compression tests passed.");
