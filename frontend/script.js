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
const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const mobileOverlay = document.getElementById("mobileOverlay");
const sidebar = document.getElementById("sidebar");

// State variables
let totalScans = 0;
let phishingScans = 0;
let safeScans = 0;
let apiUrl = "https://adAStra144-Anti-Phishing-Scanner-0.hf.space";
let isScanning = false;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    setupEventListeners();
    loadStats();
    setupAccessibility();
    addParticleEffect();
    loadTheme();
    setupMobileMenu();
});

// Add subtle particle effect to background
function addParticleEffect() {
    const particles = document.createElement('div');
    particles.className = 'particles';
    particles.innerHTML = Array.from({length: 20}, () => '<div class="particle"></div>').join('');
    document.body.appendChild(particles);
}

// Setup accessibility features
function setupAccessibility() {
    // Add keyboard navigation for example messages
    const exampleItems = document.querySelectorAll('.example-messages li');
    exampleItems.forEach((item, index) => {
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'button');
        item.setAttribute('aria-label', `Example ${index + 1}: ${item.textContent}`);
        
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                messageInput.value = item.textContent;
                messageInput.focus();
                addRippleEffect(e.target);
            }
        });
        
        item.addEventListener('click', (e) => {
            messageInput.value = item.textContent;
            messageInput.focus();
            addRippleEffect(e.target);
        });
    });
}

// Add ripple effect to buttons
function addRippleEffect(element) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Setup event listeners
function setupEventListeners() {
    // Scan button click
    scanBtn.addEventListener("click", (e) => {
        addRippleEffect(e.target);
        scanMessage();
    });
    
    // Enter key to scan (Ctrl+Enter or Cmd+Enter)
    messageInput.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            scanMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + "px";
    });
    
    // Clear welcome message on first interaction
    messageInput.addEventListener("focus", () => {
        const welcomeMessage = chatWindow.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.opacity = '0.7';
        }
    });
}

// Show section function
function showSection(sectionName) {
    // Hide all content sections
    const contentSections = document.querySelectorAll('.content-section');
    contentSections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Hide all sidebar sections
    const sidebarSections = document.querySelectorAll('.sidebar-section');
    sidebarSections.forEach(section => {
        section.classList.add('hidden');
    });
    
    // Remove active class from all nav buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    switch(sectionName) {
        case 'chat':
            document.getElementById('chatSection').classList.add('active');
            document.querySelector('[onclick="showSection(\'chat\')"]').classList.add('active');
            break;
        case 'history':
            document.getElementById('historySection').classList.remove('hidden');
            document.querySelector('[onclick="showSection(\'history\')"]').classList.add('active');
            break;
        case 'stats':
            document.getElementById('statsSection').classList.remove('hidden');
            document.querySelector('[onclick="showSection(\'stats\')"]').classList.add('active');
            break;
        case 'status':
            document.getElementById('statusSection').classList.remove('hidden');
            document.querySelector('[onclick="showSection(\'status\')"]').classList.add('active');
            break;
    }
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
    
    // Remove welcome message after first user message
    const welcomeMessage = chatWindow.querySelector('.welcome-message');
    if (welcomeMessage && sender === "user") {
        welcomeMessage.style.display = 'none';
    }
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
    if (!message || isScanning) return;

    isScanning = true;
    scanBtn.disabled = true;
    scanBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Scanning...</span>';

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
    } finally {
        isScanning = false;
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<span class="btn-icon">🔍</span><span class="btn-text">Scan Message</span>';
    }
}

// Format the result for display
function formatResult(data) {
    const { result, confidence } = data;
    const isPhishing = result.toLowerCase().includes("phishing");
    
    const icon = isPhishing ? "🚨" : "✅";
    const color = isPhishing ? "#ef4444" : "#10b981";
    
    return `
        <div style="color: ${color}; font-weight: 600;">
            ${icon} <strong>${result}</strong>
        </div>
        <div style="margin-top: 8px; font-size: 0.9rem; opacity: 0.8;">
            Confidence: <strong>${confidence}</strong>
        </div>
        <div style="margin-top: 12px; font-size: 0.85rem; color: #cbd5e1;">
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
    historyItem.setAttribute('role', 'listitem');
    
    const truncatedMessage = message.length > 50 ? message.substring(0, 50) + "..." : message;
    historyItem.innerHTML = `
        <div style="font-weight: 500; margin-bottom: 4px;">
            ${isPhishing ? "🚨 Phishing" : "✅ Safe"}
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1;">
            ${truncatedMessage}
        </div>
        <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">
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

// Auto-check API status every 30 seconds
setInterval(checkApiStatus, 30000); 

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');
    const isDark = body.classList.contains('light-theme');
    
    if (isDark) {
        // Switch to dark theme
        body.classList.remove('light-theme');
        localStorage.setItem('surLinkTheme', 'dark');
        themeToggle.checked = false;
    } else {
        // Switch to light theme
        body.classList.add('light-theme');
        localStorage.setItem('surLinkTheme', 'light');
        themeToggle.checked = true;
    }
}

// Load saved theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('surLinkTheme');
    const themeToggle = document.getElementById('themeToggle');
    
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        if (themeToggle) {
            themeToggle.checked = true;
        }
    }
}

// Mobile Menu Functionality
function setupMobileMenu() {
    if (!mobileMenuBtn || !mobileOverlay || !sidebar) return;
    
    // Toggle mobile menu
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    
    // Close menu when clicking overlay
    mobileOverlay.addEventListener('click', closeMobileMenu);
    
    // Close menu when clicking nav buttons
    const navButtons = sidebar.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Small delay to allow section change to complete
            setTimeout(closeMobileMenu, 100);
        });
    });
    
    // Handle escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
            closeMobileMenu();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar.classList.contains('mobile-open')) {
            closeMobileMenu();
        }
    });
}

function toggleMobileMenu() {
    const isOpen = sidebar.classList.contains('mobile-open');
    
    if (isOpen) {
        closeMobileMenu();
    } else {
        openMobileMenu();
    }
}

function openMobileMenu() {
    sidebar.classList.add('mobile-open');
    mobileOverlay.classList.add('active');
    mobileMenuBtn.classList.add('active');
    
    // Prevent body scroll when menu is open
    document.body.style.overflow = 'hidden';
    
    // Focus trap for accessibility
    const firstFocusable = sidebar.querySelector('.nav-btn');
    if (firstFocusable) {
        firstFocusable.focus();
    }
}

function closeMobileMenu() {
    sidebar.classList.remove('mobile-open');
    mobileOverlay.classList.remove('active');
    mobileMenuBtn.classList.remove('active');
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Return focus to menu button
    mobileMenuBtn.focus();
} 