// DOM Elements
const scanBtn = document.getElementById("scanBtn");
const messageInput = document.getElementById("messageInput");
const chatWindow = document.getElementById("chatWindow");
const progressBar = document.getElementById("progressBar");
const historyList = document.getElementById("historyList");
const totalScansEl = document.getElementById("totalScans");
const phishingScansEl = document.getElementById("phishingScans");
const safeScansEl = document.getElementById("safeScans");
const statusIndicator = document.getElementById("statusIndicator");
const statusText = document.getElementById("statusText");

// State variables
let totalScans = 0;
let phishingScans = 0;
let safeScans = 0;
let apiUrl = "https://your-huggingface-space-url.hf.space"; // Will be updated

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    setupEventListeners();
    loadStats();
});

// Setup event listeners
function setupEventListeners() {
    // Scan button click
    scanBtn.addEventListener("click", scanMessage);
    
    // Enter key to scan
    messageInput.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
            e.preventDefault();
            scanMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = messageInput.scrollHeight + "px";
    });
}

// Check API status
async function checkApiStatus() {
    try {
        statusIndicator.className = "status-indicator checking";
        statusText.textContent = "Checking...";
        
        const response = await fetch(`${apiUrl}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            statusIndicator.className = "status-indicator online";
            statusText.textContent = "Online";
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        console.error('API Status Check Error:', error);
        statusIndicator.className = "status-indicator offline";
        statusText.textContent = "Offline";
    }
}

// Append message to chat
function appendMessage(content, sender = "user", isTyping = false) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${sender}`;
    
    const bubbleContent = document.createElement("div");
    bubbleContent.className = "bubble-content";
    
    if (isTyping) {
        bubbleContent.innerHTML = `
            <div class="typing-indicator">
                AI is analyzing...
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
    } else {
        bubbleContent.innerHTML = `
            <div class="bubble-text">${content}</div>
            <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        `;
    }
    
    bubble.appendChild(bubbleContent);
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    appendMessage("", "ai", true);
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = chatWindow.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.closest('.message-bubble').remove();
    }
}

// Animate progress bar
function animateProgressBar() {
    progressBar.classList.remove("hidden");
    const progressFill = progressBar.querySelector('.progress-fill');
    progressFill.style.width = "0%";
    
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
        } else {
            width += 10;
            progressFill.style.width = width + "%";
        }
    }, 100);
}

// Hide progress bar
function hideProgressBar() {
    progressBar.classList.add("hidden");
}

// Scan message function
async function scanMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input and add user message
    messageInput.value = "";
    messageInput.style.height = "auto";
    appendMessage(message, "user");
    
    // Show loading states
    showTypingIndicator();
    animateProgressBar();
    
    try {
        const response = await fetch(`${apiUrl}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove loading states
        removeTypingIndicator();
        hideProgressBar();
        
        // Format the response
        const resultText = formatResult(data);
        appendMessage(resultText, "ai");
        
        // Update stats and history
        saveToHistory(message, data.result);
        updateStats(data.result);
        
    } catch (error) {
        console.error("Scan Error:", error);
        removeTypingIndicator();
        hideProgressBar();
        
        const errorMessage = `
            ❌ Connection Error<br>
            <small>Unable to connect to the AI service. Please check your internet connection and try again.</small>
        `;
        appendMessage(errorMessage, "ai");
    }
}

// Format the result for display
function formatResult(data) {
    const { result, confidence } = data;
    const isPhishing = result.toLowerCase().includes("phishing");
    
    const icon = isPhishing ? "🚨" : "✅";
    const color = isPhishing ? "#dc3545" : "#28a745";
    
    return `
        <div style="color: ${color}; font-weight: 600;">
            ${icon} <strong>${result}</strong>
        </div>
        <div style="margin-top: 8px; font-size: 0.9rem; opacity: 0.8;">
            Confidence: <strong>${confidence}</strong>
        </div>
        <div style="margin-top: 12px; font-size: 0.85rem; color: #666;">
            ${isPhishing ? 
                "⚠️ This message appears to be a phishing attempt. Be cautious and do not click on suspicious links." :
                "✅ This message appears to be safe. However, always remain vigilant with personal information."
            }
        </div>
    `;
}

// Save to history
function saveToHistory(message, result) {
    const isPhishing = result.toLowerCase().includes("phishing");
    const historyItem = document.createElement("div");
    historyItem.className = `history-item ${isPhishing ? 'phishing' : 'safe'}`;
    
    const truncatedMessage = message.length > 50 ? message.substring(0, 50) + "..." : message;
    historyItem.innerHTML = `
        <div style="font-weight: 500; margin-bottom: 4px;">
            ${isPhishing ? "🚨 Phishing" : "✅ Safe"}
        </div>
        <div style="font-size: 0.85rem; color: #666;">
            ${truncatedMessage}
        </div>
        <div style="font-size: 0.75rem; color: #999; margin-top: 4px;">
            ${new Date().toLocaleTimeString()}
        </div>
    `;
    
    // Remove empty history message if it exists
    const emptyHistory = historyList.querySelector('.empty-history');
    if (emptyHistory) {
        emptyHistory.remove();
    }
    
    // Add to top of history
    historyList.insertBefore(historyItem, historyList.firstChild);
    
    // Keep only last 10 items
    const items = historyList.querySelectorAll('.history-item');
    if (items.length > 10) {
        items[items.length - 1].remove();
    }
}

// Update statistics
function updateStats(result) {
    totalScans++;
    
    if (result.toLowerCase().includes("phishing")) {
        phishingScans++;
    } else {
        safeScans++;
    }
    
    totalScansEl.textContent = totalScans;
    phishingScansEl.textContent = phishingScans;
    safeScansEl.textContent = safeScans;
    
    // Save to localStorage
    saveStats();
}

// Save stats to localStorage
function saveStats() {
    const stats = {
        totalScans,
        phishingScans,
        safeScans
    };
    localStorage.setItem('surLinkStats', JSON.stringify(stats));
}

// Load stats from localStorage
function loadStats() {
    const savedStats = localStorage.getItem('surLinkStats');
    if (savedStats) {
        const stats = JSON.parse(savedStats);
        totalScans = stats.totalScans || 0;
        phishingScans = stats.phishingScans || 0;
        safeScans = stats.safeScans || 0;
        
        totalScansEl.textContent = totalScans;
        phishingScansEl.textContent = phishingScans;
        safeScansEl.textContent = safeScans;
    }
}

// Update API URL (this will be set when you deploy to Hugging Face Spaces)
function updateApiUrl(url) {
    apiUrl = url;
    checkApiStatus();
}

// Example usage for local development
// updateApiUrl("http://localhost:7860");

// Example usage for Hugging Face Spaces
// updateApiUrl("https://your-username-your-space-name.hf.space");

// Auto-check API status every 30 seconds
setInterval(checkApiStatus, 30000); 