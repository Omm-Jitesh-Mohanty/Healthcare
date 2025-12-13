const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const languageSelect = document.getElementById('language');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const statusIndicator = document.getElementById('status');

// CSRF Token function
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add message to chat window
function addMessage(content, type = 'bot') {
    const msgElem = document.createElement('div');
    msgElem.classList.add('message', type);
    
    // Add typing indicator for bot messages
    if (type === 'bot') {
        msgElem.innerHTML = `<div class="typing-indicator">...</div>`;
        chatWindow.appendChild(msgElem);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        // Simulate typing delay
        setTimeout(() => {
            msgElem.innerHTML = content;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }, 500);
    } else {
        msgElem.textContent = content;
        chatWindow.appendChild(msgElem);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

// Update status indicator
function updateStatus(online) {
    if (online) {
        statusIndicator.textContent = 'Online';
        statusIndicator.className = 'status-online';
    } else {
        statusIndicator.textContent = 'Offline';
        statusIndicator.className = 'status-offline';
    }
}

// Welcome messages in different languages
function getWelcomeMessages(lang) {
    const messages = {
        en: [
            "👋 Hello! Welcome to your AI Health Assistant.",
            "I'm here to provide vaccination schedules, disease info, health tips and more.",
            "You can type or use voice input below to start!"
        ],
        hi: [
            "👋 नमस्ते! आपका AI स्वास्थ्य सहायक में स्वागत है।",
            "मैं टीकाकरण, बीमारी की जानकारी, स्वास्थ्य सुझाव और अन्य के लिए यहाँ हूँ।",
            "शुरू करने के लिए नीचे टाइप करें या आवाज का उपयोग करें!"
        ],
        or: [
            "👋 ନମସ୍କାର! ଆପଣଙ୍କର AI ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକକୁ ସ୍ୱାଗତ।",
            "ଟିକାକରଣ, ରୋଗ ସୂଚନା, ସ୍ୱାସ୍ଥ୍ୟ ଟିପ୍ସ ଏବଂ ଅଧିକ ପାଇଁ ମୁଁ ଏଠାରେ ଅଛି।",
            "ଆରମ୍ଭ କରିବା ପାଇଁ ତଳେ ଟାଇପ୍ କରନ୍ତୁ କିମ୍ବା ଭଏସ୍ ବ୍ୟବହାର କରନ୍ତୁ!"
        ]
    };
    return messages[lang] || messages.en;
}

// Show welcome messages
function showWelcomeMessages(lang) {
    chatWindow.innerHTML = '';
    getWelcomeMessages(lang).forEach(text => addMessage(text, 'bot'));
}

// Test server connection
function testConnection() {
    return fetch('/api/chatbot/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ message: 'test', language: 'en' }),
    })
    .then(response => response.ok)
    .catch(() => false);
}

// Initialize chatbot
async function initializeChatbot() {
    const isConnected = await testConnection();
    updateStatus(isConnected);
    
    if (!isConnected) {
        addMessage('⚠️ Warning: Cannot connect to chatbot server. Please make sure Rasa is running.', 'alert');
    }
    
    showWelcomeMessages(languageSelect.value);
}

// Handle user input form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    userInput.value = '';
    userInput.disabled = true;
    chatForm.querySelector('button[type="submit"]').disabled = true;

    try {
        const response = await fetch('/api/chatbot/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message, language: languageSelect.value }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.replies && data.replies.length > 0) {
            data.replies.forEach(reply => addMessage(reply, 'bot'));
        } else if (data.message) {
            addMessage(data.message, 'bot');
        } else if (data.error) {
            addMessage(`Error: ${data.error}`, 'alert');
        } else {
            addMessage("I understand you're looking for health information. How can I assist you today?", 'bot');
        }
        
        updateStatus(true);
        
    } catch (error) {
        console.error('Chat error:', error);
        addMessage('⚠️ Error: Could not reach chatbot server. Please make sure Rasa is running on port 5005.', 'alert');
        updateStatus(false);
    } finally {
        userInput.disabled = false;
        chatForm.querySelector('button[type="submit"]').disabled = false;
        userInput.focus();
    }
});

// Voice recognition setup
let recognition = null;

function initializeSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'none';
        return false;
    }
    return true;
}

recordBtn.addEventListener('click', () => {
    if (!recognition && initializeSpeechRecognition()) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        // Set language based on selection
        const langMap = {
            'hi': 'hi-IN',
            'or': 'or-IN', 
            'en': 'en-US'
        };
        recognition.lang = langMap[languageSelect.value] || 'en-US';

        recognition.onstart = () => {
            recordBtn.disabled = true;
            stopBtn.disabled = false;
            addMessage('🎤 Listening... Speak now', 'alert');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            
            // Auto-submit the voice input
            chatForm.dispatchEvent(new Event('submit'));
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            addMessage('❌ Speech recognition error. Please try again.', 'alert');
            recordBtn.disabled = false;
            stopBtn.disabled = true;
        };

        recognition.onend = () => {
            recordBtn.disabled = false;
            stopBtn.disabled = true;
        };
    }

    if (recognition) {
        recognition.start();
    }
});

stopBtn.addEventListener('click', () => {
    if (recognition) {
        recognition.stop();
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    }
});

// Language change handler
languageSelect.addEventListener('change', () => {
    showWelcomeMessages(languageSelect.value);
});

// Handle Enter key in input field
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Auto-focus input field
userInput.focus();

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeSpeechRecognition();
    initializeChatbot();
});

// Add some CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        color: #666;
        font-style: italic;
    }
    
    .message.bot .typing-indicator {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    input:disabled, button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;
document.head.appendChild(style);