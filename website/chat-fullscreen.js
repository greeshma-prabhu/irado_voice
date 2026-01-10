class IradoChatFullscreen {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.isLoading = false;
        this.currentLanguage = 'nl';
        this.apiBaseUrl = this.getApiBaseUrl();
        this.afvalplaatsImageUrl = `${this.apiBaseUrl}/media/afvalplaats.png`;
        
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
        const endpoint = `${this.apiBaseUrl}/api/chat`;
        const authToken = 'aXJhZG86MjBJcmFkbzI1IQ==';
        
        return {
            url: endpoint + '?v=' + Date.now(),
            auth: authToken
        };
    }

    getApiBaseUrl() {
        // Optional override from embedding page:
        // window.IRADO_CHATBOT_API_BASE = 'https://irado-chatbot-app.azurewebsites.net'
        if (window.IRADO_CHATBOT_API_BASE) {
            return String(window.IRADO_CHATBOT_API_BASE).replace(/\/+$/, '');
        }

        // If served from an Azure chatbot app, use same-origin (dev/prod).
        const host = window.location.hostname || '';
        if (host.endsWith('.azurewebsites.net')) {
            return window.location.origin;
        }

        // Default: production chatbot API base.
        return 'https://irado-chatbot-app.azurewebsites.net';
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
        
        // If no history was passed in, start with a language selector so the
        // user can immediately choose their preferred language (mobile & desktop).
        this.chatMessages.innerHTML = '';
        this.renderLanguageSelector();
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
        // Kept for backwards-compatibility; not used when chatHistory is absent,
        // because we now show a language selector in that case.
        this.showTypingIndicator();
        
        try {
            const rawOutput = await this.sendToApi('hoi');
            const payload = this.normalizePayload(rawOutput);
            
            this.hideTypingIndicator();
            
            const welcomeMessage = this.createBotMessageFromPayload(payload);
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

    renderLanguageSelector() {
        // Introductiebericht voor taalkeuze
        const intro = document.createElement('div');
        intro.className = 'message bot-message';
        const introContent = document.createElement('div');
        introContent.className = 'message-content';
        introContent.textContent = 'Kies een taal om het gesprek te starten:';
        intro.appendChild(introContent);

        const wrapper = document.createElement('div');
        wrapper.className = 'language-selector';

        const languages = [
            { code: 'nl', label: 'Nederlands', trigger: 'start chat - language: dutch' },
            { code: 'en', label: 'English', trigger: 'start chat - language: english' },
            { code: 'tr', label: 'Türkçe', trigger: 'start chat - language: turkish' },
            { code: 'ar', label: 'العربية', trigger: 'start chat - language: arabic' },
        ];

        languages.forEach(lang => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'language-button';
            btn.textContent = lang.label;
            btn.addEventListener('click', () => {
                this.handleLanguageSelection(lang.code, lang.trigger);
            });
            wrapper.appendChild(btn);
        });

        this.chatMessages.appendChild(intro);
        this.chatMessages.appendChild(wrapper);
        this.scrollToBottom();
    }

    handleLanguageSelection(langCode, triggerMessage) {
        this.currentLanguage = langCode;

        // Verwijder taalkeuze na selectie
        const selector = this.chatMessages.querySelector('.language-selector');
        if (selector) {
            selector.remove();
        }

        this.showTypingIndicator();
        this.isLoading = true;
        this.chatSend.disabled = true;
        this.chatSend.classList.add('loading');

        this.sendToApi(triggerMessage)
            .then(rawOutput => {
                const payload = this.normalizePayload(rawOutput);
                this.hideTypingIndicator();
                const botMessage = this.createBotMessageFromPayload(payload);
                this.chatMessages.appendChild(botMessage);
            })
            .catch(error => {
                console.error('Language start error (fullscreen):', error);
                this.hideTypingIndicator();
                const fallback = this.createMessage(
                    'Sorry, er is een fout opgetreden bij het starten van de chat.',
                    'bot'
                );
                this.chatMessages.appendChild(fallback);
            })
            .finally(() => {
                this.isLoading = false;
                this.chatSend.disabled = false;
                this.chatSend.classList.remove('loading');
                this.scrollToBottom();
            });
    }

    normalizePayload(rawOutput) {
        let payload = rawOutput;
        if (typeof payload === 'string') {
            try {
                payload = JSON.parse(payload);
            } catch (e) {
                payload = {
                    text: payload,
                    language: this.currentLanguage || 'nl',
                    buttons: [],
                    showAfvalplaatsImage: false
                };
            }
        }

        if (!payload || typeof payload !== 'object') {
            payload = {
                text: '',
                language: this.currentLanguage || 'nl',
                buttons: [],
                showAfvalplaatsImage: false
            };
        }

        if (!payload.text) {
            payload.text = '';
        }
        if (!payload.language) {
            payload.language = this.currentLanguage || 'nl';
        }
        if (!Array.isArray(payload.buttons)) {
            payload.buttons = [];
        }
        payload.showAfvalplaatsImage = Boolean(payload.showAfvalplaatsImage);

        this.currentLanguage = payload.language;

        return payload;
    }

    createBotMessageFromPayload(payload) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = payload.text || '';
        messageDiv.appendChild(contentDiv);

        if (payload.showAfvalplaatsImage) {
            const imageWrapper = document.createElement('div');
            imageWrapper.className = 'afvalplaats-wrapper';

            const img = document.createElement('img');
            img.src = this.afvalplaatsImageUrl;
            img.alt = 'Voorbeeld van waar u het grofvuil neer mag zetten.';
            img.className = 'afvalplaats-image';

            imageWrapper.appendChild(img);
            messageDiv.appendChild(imageWrapper);
        }

        if (Array.isArray(payload.buttons) && payload.buttons.length > 0) {
            const buttonsWrapper = document.createElement('div');
            buttonsWrapper.className = 'bot-buttons';

            payload.buttons.forEach(btn => {
                const button = document.createElement('button');
                button.type = 'button';
                const variant = btn.variant === 'secondary' ? 'secondary' : 'primary';
                button.className = `bot-button ${variant}`;
                button.textContent = btn.label || btn.value || '';

                button.addEventListener('click', () => {
                    const value = btn.value || btn.label || '';
                    if (!value) {
                        return;
                    }
                    const userMessage = this.createMessage(value, 'user');
                    this.chatMessages.appendChild(userMessage);
                    this.scrollToBottom();
                    this.sendMessageWithContent(value);
                });

                buttonsWrapper.appendChild(button);
            });

            messageDiv.appendChild(buttonsWrapper);
        }

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
        
        await this.sendMessageWithContent(message);
    }

    async sendMessageWithContent(message) {
        if (!message || this.isLoading) return;

        this.showTypingIndicator();
        this.isLoading = true;
        this.chatSend.disabled = true;
        this.chatSend.classList.add('loading');

        try {
            const rawOutput = await this.sendToApi(message);
            const payload = this.normalizePayload(rawOutput);

            this.hideTypingIndicator();

            const botMessage = this.createBotMessageFromPayload(payload);
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
        
        return data.output;
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

