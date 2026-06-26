const personaSelect = document.getElementById('persona');
const chatHistory = document.getElementById('chat-history');
const chatForm = document.getElementById('chat-form');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');
const personaTitle = document.getElementById('current-persona-title');
const personaDesc = document.getElementById('current-persona-desc');

const API_URL = "http://localhost:8000/v1/chat/completions";

const personaData = {
    "chat": {
        title: "Tyrion Lannister",
        desc: "I drink and I know things. (General Chat)",
        icon: "fa-wine-glass"
    },
    "math": {
        title: "Euclid",
        desc: "The father of geometry. (Mathematics)",
        icon: "fa-square-root-variable"
    },
    "reasoning": {
        title: "Socrates",
        desc: "I know that I know nothing. (Deep Reasoning)",
        icon: "fa-brain"
    },
    "summarization": {
        title: "TL;DR",
        desc: "Get straight to the point. (Summarization)",
        icon: "fa-compress-alt"
    }
};

// Auto-resize textarea
promptInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.value === '') {
        this.style.height = 'auto';
    }
});

// Handle enter to submit
promptInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Change Persona UI
personaSelect.addEventListener('change', (e) => {
    const capability = e.target.value;
    const data = personaData[capability];
    personaTitle.innerHTML = `<i class="fas ${data.icon}"></i> ${data.title}`;
    personaDesc.textContent = data.desc;
    
    // Optional: clear chat when switching persona
    // chatHistory.innerHTML = '';
});

// Create Message Element
function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message fade-in`;
    
    const icon = role === 'user' ? 'fa-user' : 'fa-robot';
    
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fas ${icon}"></i></div>
        <div class="message-content">${escapeHTML(content)}</div>
    `;
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Create Typing Indicator
function appendTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message system-message fade-in`;
    msgDiv.id = 'typing-indicator';
    
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Escape HTML to prevent XSS
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag])
    );
}

// Handle Form Submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const prompt = promptInput.value.trim();
    if (!prompt) return;
    
    const capability = personaSelect.value;
    
    // Add User Message
    appendMessage('user', prompt);
    
    // Reset Input
    promptInput.value = '';
    promptInput.style.height = 'auto';
    sendBtn.disabled = true;
    
    // Add Typing Indicator
    appendTypingIndicator();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                capability: capability,
                messages: [{ role: 'user', content: prompt }]
            })
        });
        
        removeTypingIndicator();
        
        if (!response.ok) {
            appendMessage('system', `Error: ${response.status} ${response.statusText}`);
            return;
        }
        
        const data = await response.json();
        
        if (data.choices && data.choices.length > 0) {
            appendMessage('system', data.choices[0].message.content);
        } else {
            appendMessage('system', "Error: No response generated.");
        }
        
    } catch (error) {
        removeTypingIndicator();
        appendMessage('system', `Connection Error: Make sure Uvicorn is running on port 8000.\n\nDetails: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        promptInput.focus();
    }
});

// Initialize UI
personaSelect.dispatchEvent(new Event('change'));
