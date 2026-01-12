class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.conversationHistory = [];
        this.isTyping = false;
<<<<<<< HEAD
        this.API_URL = "http://127.0.0.1:8081/api/chat"; // ✅ Backend URL
=======
        this.API_URL = "http://127.0.0.1:8080/api/chat"; // ✅ Backend URL
>>>>>>> 9ce856a3b07268dd31a699b2dc2f080368e608f4
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
    }

    createWidget() {
        const widget = document.createElement('div');
        widget.className = 'chatbot-widget';
        widget.innerHTML = `
            <button class="chatbot-toggle" id="chatbot-toggle">💬</button>
            <div class="chatbot-container" id="chatbot-container">
                <div class="chatbot-header">
                    <img src="assets/chatbot-mascot.png" alt="FoodSnap Assistant" class="chatbot-mascot">
                    <div class="chatbot-info">
                        <h3>FoodSnap Assistant</h3>
                        <p>Your nutrition companion</p>
                    </div>
                    <button class="chatbot-close" id="chatbot-close">×</button>
                </div>

                <div class="chatbot-messages" id="chatbot-messages">
                    <div class="welcome-message">
                        👋 Hi! I'm your FoodSnap nutrition assistant. Ask me about calories, healthy eating, or upload a food photo for analysis!
                    </div>
                </div>

                <div class="typing-indicator" id="typing-indicator" style="display:none;">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>

                <div class="chatbot-input">
                    <div class="input-container">
                        <textarea id="chatbot-textarea"
                                  placeholder="Ask about nutrition, calories, or healthy eating..."
                                  rows="1"></textarea>
                        <button class="send-button" id="send-button">➤</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
    }

    attachEventListeners() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chatbot-close');
        const textarea = document.getElementById('chatbot-textarea');
        const sendButton = document.getElementById('send-button');

        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.closeChat());
        sendButton.addEventListener('click', () => this.sendMessage());

        textarea.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        textarea.addEventListener('input', () => this.autoResize(textarea));
    }

    toggleChat() {
        const container = document.getElementById('chatbot-container');
        const toggle = document.getElementById('chatbot-toggle');

        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            container.classList.add('open');
            toggle.innerHTML = '×';
            this.scrollToBottom();
        } else {
            container.classList.remove('open');
            toggle.innerHTML = '💬';
        }
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('chatbot-container').classList.remove('open');
        document.getElementById('chatbot-toggle').innerHTML = '💬';
    }

    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 80) + 'px';
    }

    async sendMessage() {
        const textarea = document.getElementById('chatbot-textarea');
        const message = textarea.value.trim();

        if (!message || this.isTyping) return;

        this.addMessage(message, 'user');
        textarea.value = '';
        textarea.style.height = 'auto';

        this.showTyping();

        try {
            console.log("Sending to:", this.API_URL);

            const response = await fetch(this.API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory
                })
            });

            console.log("Status:", response.status);

            if (!response.ok) {
                throw new Error(`Server error ${response.status}`);
            }

            const data = await response.json();

            this.hideTyping();
            this.addMessage(data.response || "No response from assistant.", 'assistant');

        } catch (error) {
            console.error('Chat error:', error);
            this.hideTyping();
            this.addMessage('⚠️ Server is not reachable. Please make sure backend is running.', 'assistant');
        }
    }

    addMessage(content, role) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');

        messageDiv.className = `message ${role}`;
        messageDiv.textContent = content;
        messagesContainer.appendChild(messageDiv);

        this.conversationHistory.push({ role, content });

        if (this.conversationHistory.length > 10) {
            this.conversationHistory = this.conversationHistory.slice(-10);
        }

        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        document.getElementById('typing-indicator').style.display = 'block';
        document.getElementById('send-button').disabled = true;
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        document.getElementById('typing-indicator').style.display = 'none';
        document.getElementById('send-button').disabled = false;
    }

    scrollToBottom() {
        setTimeout(() => {
            const messagesContainer = document.getElementById('chatbot-messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatbotWidget();
});
