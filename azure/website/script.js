class IradoChat {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.isOpen = false;
        this.isLoading = false;
        
        this.apiConfig = this.getApiConfig();
        
        this.initializeElements();
        this.bindEvents();
    }
    
    getOrCreateSessionId() {
        const storageKey = 'irado_chat_session_id';
        
        let sessionId = sessionStorage.getItem(storageKey);
        
        if (!sessionId) {
            sessionId = this.generateSessionId();
            sessionStorage.setItem(storageKey, sessionId);
        }
        
        return sessionId;
    }
    
    generateSessionId() {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2, 15);
        return `irado_${timestamp}_${random}`;
    }
    
    resetSession() {
        const storageKey = 'irado_chat_session_id';
        sessionStorage.removeItem(storageKey);
        this.sessionId = this.getOrCreateSessionId();
        
        this.chatMessages.innerHTML = '';
        
        this.sendAutomaticGreeting();
    }
    
    getApiConfig() {
        const endpoint = 'https://irado-chatbot-app.azurewebsites.net/api/chat';
        const authToken = 'aXJhZG86MjBJcmFkbzI1IQ==';
        
        return {
            url: endpoint + '?v=' + Date.now(),
            auth: authToken
        };
    }
    
    initializeElements() {
        this.chatToggle = document.getElementById('chatToggle');
        this.chatWindow = document.getElementById('chatWindow');
        this.chatClose = document.getElementById('chatClose');
        this.chatExpand = document.getElementById('chatExpand');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');
    }
    
    
    bindEvents() {
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        this.chatClose.addEventListener('click', () => this.closeChat());
        this.chatExpand.addEventListener('click', () => this.expandChat());
        this.chatSend.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.chatWindow.contains(e.target) && !this.chatToggle.contains(e.target)) {
                this.closeChat();
            }
        });
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        this.chatWindow.classList.add('open');
        this.isOpen = true;
        this.chatInput.focus();
        
        this.chatWindow.style.transform = 'translateY(20px)';
        this.chatWindow.style.opacity = '0';
        
        requestAnimationFrame(() => {
            this.chatWindow.style.transition = 'all 0.3s ease';
            this.chatWindow.style.transform = 'translateY(0)';
            this.chatWindow.style.opacity = '1';
        });
        
        this.sendAutomaticGreeting();
    }
    
    closeChat() {
        this.chatWindow.style.transition = 'all 0.3s ease';
        this.chatWindow.style.transform = 'translateY(20px)';
        this.chatWindow.style.opacity = '0';
        
        setTimeout(() => {
            this.chatWindow.classList.remove('open');
            this.isOpen = false;
        }, 300);
    }
    
    expandChat() {
        // Collect current chat messages
        const messages = this.getCurrentChatMessages();
        
        // Create URL parameters for the fullscreen chat
        const chatHistory = encodeURIComponent(JSON.stringify(messages));
        const sessionId = this.sessionId;
        
        // Navigate to fullscreen chat page with session and history
        const fullscreenUrl = `chat.html?sessionId=${sessionId}&chatHistory=${chatHistory}`;
        
        // Open in new window/tab
        window.open(fullscreenUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    }
    
    getCurrentChatMessages() {
        const messages = [];
        const messageElements = this.chatMessages.querySelectorAll('.message');
        
        messageElements.forEach(element => {
            const content = element.querySelector('.message-content').textContent;
            const type = element.classList.contains('user-message') ? 'user' : 'bot';
            
            messages.push({
                content: content,
                type: type
            });
        });
        
        return messages;
    }
    
    async sendAutomaticGreeting() {
        this.chatMessages.innerHTML = '';
        
        this.showTypingIndicator();
        
        try {
            const response = await this.sendToApi('hoi');
            
            this.hideTypingIndicator();
            
            const welcomeMessage = this.createMessage(response.output, 'bot');
            this.chatMessages.appendChild(welcomeMessage);
            
        } catch (error) {
            console.error('Auto greeting error:', error);
            this.hideTypingIndicator();
            
            const fallbackMessage = this.createMessage(
                'Hallo, ik ben de virtuele assistent van Irado. Waarmee kan ik je vandaag helpen?',
                'bot'
            );
            this.chatMessages.appendChild(fallbackMessage);
        }
        
        this.scrollToBottom();
    }
    
    createMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }
    
    createTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const dots = document.createElement('div');
        dots.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        
        typingDiv.appendChild(dots);
        return typingDiv;
    }
    
    showTypingIndicator() {
        const existing = document.getElementById('typing-indicator');
        if (existing) return;
        
        const typing = this.createTypingIndicator();
        this.chatMessages.appendChild(typing);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) {
            typing.remove();
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isLoading) return;
        
        const userMessage = this.createMessage(message, 'user');
        this.chatMessages.appendChild(userMessage);
        this.chatInput.value = '';
        this.scrollToBottom();
        
        this.showTypingIndicator();
        this.isLoading = true;
        this.chatSend.disabled = true;
        
        try {
            const response = await this.sendToApi(message);
            
            this.hideTypingIndicator();
            
            const botMessage = this.createMessage(response.output, 'bot');
            this.chatMessages.appendChild(botMessage);
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            
            const errorMessage = this.createMessage(
                'Sorry, er is een fout opgetreden. Probeer het later opnieuw.',
                'bot'
            );
            this.chatMessages.appendChild(errorMessage);
        } finally {
            this.isLoading = false;
            this.chatSend.disabled = false;
            this.scrollToBottom();
        }
    }
    
    async sendToApi(message) {
        const requestData = {
            sessionId: this.sessionId,
            action: 'sendMessage',
            chatInput: message,
            timestamp: Date.now(),
            source: 'website'
        };
        
        const headers = new Headers();
        headers.set('Content-Type', 'application/json');
        headers.set('Accept', 'application/json');
        headers.set('Authorization', `Basic ${this.apiConfig.auth}`);
        
        const response = await fetch(this.apiConfig.url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(requestData),
            credentials: 'omit',
            mode: 'cors'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.output) {
            throw new Error('Invalid response format');
        }
        
        return data;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    clearChat() {
        this.chatMessages.innerHTML = '';
        this.addWelcomeMessage();
    }
    
    getSessionId() {
        return this.sessionId;
    }
    
    
    
    
    
    
    
    
}

document.addEventListener('DOMContentLoaded', () => {
    window.iradoChat = new IradoChat();
    
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Irado Chat initialized with session:', window.iradoChat.getSessionId());
    }
});

document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.iradoChat && window.iradoChat.isOpen) {
    }
});

window.addEventListener('beforeunload', () => {
    if (window.iradoChat && window.iradoChat.isOpen) {
    }
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = IradoChat;
}