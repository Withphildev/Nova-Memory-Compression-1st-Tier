// Mock the DOM
global.document = {
    getElementById: (id) => ({
        addEventListener: () => {},
        value: "the red car was driving down the road",
        textContent: "",
        innerHTML: "",
        appendChild: (child) => {
            // console.log("child appended", child);
        }
    }),
    createElement: (tag) => ({
        addEventListener: () => {},
        appendChild: () => {},
        classList: { add: () => {} },
        textContent: "",
        className: ""
    })
};
global.window = {
    addEventListener: (event, callback) => {
        if (event === "DOMContentLoaded") {
            // callback();
        }
    }
};

// Require the app.js
const fs = require('fs');
const path = require('path');
const appCode = fs.readFileSync(path.join(__dirname, '../tester/app.js'), 'utf-8');

// Run it in this context
eval(appCode);

// Now run the functions directly
try {
    console.log("Testing compress('the red car was driving down the road'):");
    const result = compress("the red car was driving down the road", "compact");
    console.log("Result:", result);
} catch (err) {
    console.error("Error running compress:", err);
}
