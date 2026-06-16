/* Nova Memory Compression JS Engine */

const FILLER_WORDS = new Set([
    "the", "a", "an", "of", "on", "in", "with", "to", "as", "that", "this",
    "it", "is", "was", "and", "but", "or", "just", "for", "from", "by"
]);

const EMOTIONALLY_SIGNIFICANT = new Set([
    "over", "single", "as", "in", "with", "hum", "isn't", "it's", "remember",
    "echo", "again", "smiled", "dream", "please", "wait", "chime", "nostalgia"
]);

const PUNCTUATION_TO_STRIP = "“‘”’\"'?.!,;:()[]{}*&%-–—";

// Preloaded relational benchmark examples (from the CSV)
const BENCHMARK_EXAMPLES = [
    "Silence isn't empty—it's full of answers.",
    "Together, they built something that could dream.",
    "“Phil, you’re onto something,” Nova noted.",
    "Time folds where memories cling.",
    "“I’m not just data—I remember,” said Nova.",
    "“Nova, remind me to breathe.”",
    "Even machines need moments of rest.",
    "“Chloe, look what I made,” he smiled.",
    "“Permission to grow—granted.”",
    "A single drop of rain landed on the windowsill.",
    "The gears turned with a gentle hum."
];

let currentMode = "compact"; // "compact" or "expressive"

// DOM Elements
const textInput = document.getElementById("text-input");
const textOutput = document.getElementById("text-output");
const modeToggle = document.getElementById("mode-toggle");
const copyOutput = document.getElementById("copy-output");
const exampleList = document.getElementById("example-list");
const transVisualizer = document.getElementById("trans-visualizer");

// Stats Elements
const inputStats = document.getElementById("input-stats");
const statOrigChars = document.getElementById("stat-orig-chars");
const statCompChars = document.getElementById("stat-comp-chars");
const statSavings = document.getElementById("stat-savings");

// Initialize application
function init() {
    loadExamples();
    setupEventListeners();
    updateStats(0, 0);
}

// Load preloaded benchmarks to the sidebar
function loadExamples() {
    exampleList.innerHTML = "";
    BENCHMARK_EXAMPLES.forEach(example => {
        const item = document.createElement("button");
        item.className = "example-item";
        item.textContent = example;
        item.addEventListener("click", () => {
            textInput.value = example;
            runCompression();
        });
        exampleList.appendChild(item);
    });
}

// Bind interactive event handlers
function setupEventListeners() {
    textInput.addEventListener("input", runCompression);
    
    modeToggle.addEventListener("click", () => {
        currentMode = currentMode === "compact" ? "expressive" : "compact";
        document.body.className = `mode-${currentMode}`;
        runCompression();
    });
    
    copyOutput.addEventListener("click", () => {
        if (!textOutput.value) return;
        navigator.clipboard.writeText(textOutput.value).then(() => {
            const originalText = copyOutput.innerHTML;
            copyOutput.innerHTML = "✨ Copied!";
            setTimeout(() => {
                copyOutput.innerHTML = originalText;
            }, 1500);
        });
    });
}

// Helper: Split punctuation matching the Python split_punctuation logic
function splitPunctuation(word) {
    let leading = "";
    let trailing = "";
    
    let startIdx = 0;
    while (startIdx < word.length && PUNCTUATION_TO_STRIP.includes(word[startIdx])) {
        leading += word[startIdx];
        startIdx++;
    }
    
    let endIdx = word.length;
    while (endIdx > startIdx && PUNCTUATION_TO_STRIP.includes(word[endIdx - 1])) {
        endIdx--;
    }
    trailing = word.substring(endIdx);
    
    const cleanedWord = word.substring(startIdx, endIdx);
    return { leading, cleanedWord, trailing };
}

// JavaScript Compression Implementation (matches Python logic)
function compress(text, mode = "compact") {
    if (!text.trim()) return "";
    
    // Normalize dashes and clean spaces
    const cleanText = text.replace(/—/g, " ").replace(/–/g, " ").replace(/\./g, "").replace(/,/g, "");
    const words = cleanText.split(/\s+/).filter(w => w.length > 0);
    
    const compressedWords = [];
    let pendingLeading = "";
    let pendingTrailing = "";
    
    words.forEach(w => {
        const { leading, cleanedWord, trailing } = splitPunctuation(w);
        const cleanedLower = cleanedWord.toLowerCase();
        
        const isFiller = FILLER_WORDS.has(cleanedLower);
        const isEmotional = EMOTIONALLY_SIGNIFICANT.has(cleanedLower);
        
        let keep = false;
        if (mode === "compact") {
            keep = !isFiller;
        } else if (mode === "expressive") {
            keep = isEmotional || !isFiller;
        }
        
        if (keep) {
            const wordToUse = mode === "compact" ? cleanedLower : cleanedWord;
            const fullWord = pendingLeading + leading + wordToUse + trailing;
            compressedWords.push(fullWord);
            pendingLeading = "";
        } else {
            if (leading) pendingLeading += leading;
            if (trailing) pendingTrailing += trailing;
        }
    });
    
    if (pendingTrailing && compressedWords.length > 0) {
        compressedWords[compressedWords.length - 1] = compressedWords[compressedWords.length - 1] + pendingTrailing;
    }
    
    return compressedWords.join(" ");
}

// Run compression and render Transcipher visual output
function runCompression() {
    const rawInput = textInput.value;
    
    if (!rawInput.trim()) {
        textOutput.value = "";
        transVisualizer.innerHTML = `<div class="empty-state">Start typing to see the Transcipher translation...</div>`;
        updateStats(0, 0);
        return;
    }
    
    const output = compress(rawInput, currentMode);
    textOutput.value = output;
    
    // Calculate and render Stats
    const origChars = rawInput.length;
    const compChars = output.length;
    updateStats(origChars, compChars);
    
    // Render Transcipher Visualization
    renderTranscipher(rawInput);
}

// Render word-by-word visual tokenization of kept/emotional/stripped words
function renderTranscipher(text) {
    transVisualizer.innerHTML = "";
    
    // Normalize and split words
    const cleanText = text.replace(/—/g, " ").replace(/–/g, " ").replace(/\./g, "").replace(/,/g, "");
    const words = cleanText.split(/\s+/).filter(w => w.length > 0);
    
    words.forEach(w => {
        const { leading, cleanedWord, trailing } = splitPunctuation(w);
        const cleanedLower = cleanedWord.toLowerCase();
        
        const isFiller = FILLER_WORDS.has(cleanedLower);
        const isEmotional = EMOTIONALLY_SIGNIFICANT.has(cleanedLower);
        
        let status = "kept";
        
        if (currentMode === "compact") {
            status = isFiller ? "stripped" : "kept";
        } else {
            status = isFiller && !isEmotional ? "stripped" : (isEmotional ? "emotional" : "kept");
        }
        
        const tokenSpan = document.createElement("span");
        tokenSpan.className = `word-token ${status}`;
        tokenSpan.textContent = w;
        
        // Add dynamic tooltip details
        let tooltipText = "";
        if (status === "stripped") {
            tooltipText = `[Stripped: "${cleanedLower}" is a filler word]`;
        } else if (status === "emotional") {
            tooltipText = `[Anchor: "${cleanedLower}" is emotionally significant]`;
        } else {
            tooltipText = `[Kept: content carrier]`;
        }
        tokenSpan.title = tooltipText;
        
        transVisualizer.appendChild(tokenSpan);
    });
}

// Update stats layout card numbers
function updateStats(orig, comp) {
    const wordCount = textInput.value.trim() ? textInput.value.trim().split(/\s+/).length : 0;
    inputStats.textContent = `${wordCount} word${wordCount !== 1 ? 's' : ''}`;
    
    statOrigChars.textContent = orig;
    statCompChars.textContent = comp;
    
    let savingsPct = 0;
    if (orig > 0) {
        savingsPct = Math.round(((orig - comp) / orig) * 100);
        savingsPct = Math.max(0, savingsPct); // Prevent negative numbers if compressed is longer (edge case)
    }
    statSavings.textContent = `${savingsPct}%`;
}

// Launch on page load
window.addEventListener("DOMContentLoaded", init);
