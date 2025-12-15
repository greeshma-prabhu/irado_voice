class IradoChatFullscreen {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.isLoading = false;
        
        this.apiConfig = this.getApiConfig();
        
        this.initializeElements();
        this.bindEvents();
        this.loadChatHistory();
    }
    
    getOrCreateSessionId() {
        const storageKey = 'irado_chat_session_id';
        
        // Check URL parameters first (for transfer from widget)
        const urlParams = new URLSearchParams(window.location.search);
        const sessionIdFromUrl = urlParams.get('sessionId');
        
        if (sessionIdFromUrl) {
            sessionStorage.setItem(storageKey, sessionIdFromUrl);
            return sessionIdFromUrl;
        }
        
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
    
    getApiConfig() {
        const endpoint = 'https://irado.mainfact.ai/api/chat';
        const authToken = 'aXJhZG86MjBJcmFkbzI1IQ==';
        
        return {
            url: endpoint + '?v=' + Date.now(),
            auth: authToken
        };
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');
    }
    
    bindEvents() {
        this.chatSend.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    async loadChatHistory() {
        // Check if we have chat history in URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const chatHistory = urlParams.get('chatHistory');
        
        if (chatHistory) {
            try {
                const messages = JSON.parse(decodeURIComponent(chatHistory));
                this.displayChatHistory(messages);
                return;
            } catch (error) {
                console.error('Error parsing chat history:', error);
            }
        }
        
        // If no history, send automatic greeting
        this.sendAutomaticGreeting();
    }
    
    displayChatHistory(messages) {
        this.chatMessages.innerHTML = '';
        
        messages.forEach(message => {
            const messageElement = this.createMessage(message.content, message.type);
            this.chatMessages.appendChild(messageElement);
        });
        
        this.scrollToBottom();
    }
    
    async sendAutomaticGreeting() {
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
        this.chatSend.classList.add('loading');
        
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
            this.chatSend.classList.remove('loading');
            this.scrollToBottom();
        }
    }
    
    async sendToApi(message) {
        const requestData = {
            sessionId: this.sessionId,
            action: 'sendMessage',
            chatInput: message,
            timestamp: Date.now(),
            source: 'fullscreen'
        };
        
        const headers = new Headers();
        headers.set('Content-Type', 'application/json');
        headers.set('Accept', 'application/json');
        headers.set('Authorization', `Basic ${this.apiConfig.auth}`);
        headers.set('X-Requested-With', 'XMLHttpRequest');
        headers.set('User-Agent', 'IradoChatFullscreen/1.0');
        
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
    
    getSessionId() {
        return this.sessionId;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.iradoChatFullscreen = new IradoChatFullscreen();
    
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Irado Chat Fullscreen initialized with session:', window.iradoChatFullscreen.getSessionId());
    }
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = IradoChatFullscreen;
}

