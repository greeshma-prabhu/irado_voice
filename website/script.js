class IradoChat {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.isOpen = false;
        this.isLoading = false;
        // Keep track of the active language; default is Dutch.
        this.currentLanguage = 'nl';
        // URL for the afvalplaats image served by the chatbot backend.
        // This image shows clearly where residents should place bulky waste.
        this.apiBaseUrl = this.getApiBaseUrl();
        this.afvalplaatsImageUrl = `${this.apiBaseUrl}/media/afvalplaats.png`;
        
        this.apiConfig = this.getApiConfig();
        // Bind methods used as event handlers
        this.updateChatHeight = this.updateChatHeight.bind(this);
        
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
        this.currentLanguage = 'nl';
        this.renderLanguageSelector();
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
        // Allow override via global var (e.g. on irado.nl embed):
        // window.IRADO_CHATBOT_API_BASE = 'https://irado-chatbot-app.azurewebsites.net'
        if (window.IRADO_CHATBOT_API_BASE) {
            return String(window.IRADO_CHATBOT_API_BASE).replace(/\/+$/, '');
        }

        // If the widget is served from an Azure chatbot app, use same-origin.
        const host = window.location.hostname || '';
        if (host.endsWith('.azurewebsites.net')) {
            return window.location.origin;
        }

        // Default: production chatbot API
        return 'https://irado-chatbot-app.azurewebsites.net';
    }
    
    initializeElements() {
        this.chatToggle = document.getElementById('chatToggle');
        this.chatWindow = document.getElementById('chatWindow');
        this.chatClose = document.getElementById('chatClose');
        this.chatExpand = document.getElementById('chatExpand');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');

        // Keep chat height responsive, especially on mobile when the keyboard opens/closes.
        window.addEventListener('resize', this.updateChatHeight);
        if (window.visualViewport && typeof window.visualViewport.addEventListener === 'function') {
            window.visualViewport.addEventListener('resize', this.updateChatHeight);
        }
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
            // Do not close when clicking inside the chat window (including language/buttons)
            if (this.isOpen && !this.chatWindow.contains(e.target) && !this.chatToggle.contains(e.target)) {
                this.closeChat();
            }
        });
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            const isMobile = window.innerWidth <= 768;
            if (isMobile) {
                // On mobile we go directly to the fullscreen chat page instead of
                // using the small popup widget, for a better experience.
                const sessionId = this.sessionId;
                window.location.href = `chat.html?sessionId=${encodeURIComponent(sessionId)}`;
            } else {
                this.openChat();
            }
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
            // Adjust height after animation start so it uses the current viewport height.
            this.updateChatHeight();
        });

        // Start with a clean chat and let the user choose a language.
        this.chatMessages.innerHTML = '';
        this.renderLanguageSelector();
    }
    
    closeChat() {
        this.chatWindow.style.transition = 'all 0.3s ease';
        this.chatWindow.style.transform = 'translateY(20px)';
        this.chatWindow.style.opacity = '0';
        
        setTimeout(() => {
            this.chatWindow.classList.remove('open');
            this.isOpen = false;
            // Reset inline height so CSS default applies next time.
            this.chatWindow.style.height = '';
        }, 300);
    }
    
    expandChat() {
        const sessionId = this.sessionId;
        // Only pass the sessionId to avoid very long URLs that can cause
        // "Request Line is too large" errors on some proxies/servers.
        const fullscreenUrl = `chat.html?sessionId=${encodeURIComponent(sessionId)}`;
        
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

    updateChatHeight() {
        if (!this.chatWindow) return;

        const isMobile = window.innerWidth <= 768;

        if (isMobile && this.isOpen) {
            // Reserve some space for header and margins.
            const OFFSET = 140;
            const availableHeight = window.innerHeight - OFFSET;
            const minHeight = 320;
            const newHeight = Math.max(minHeight, availableHeight);
            this.chatWindow.style.height = `${newHeight}px`;
        } else if (!isMobile) {
            // On desktop, let CSS control the height (fixed 625px).
            this.chatWindow.style.height = '';
        }
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
            btn.addEventListener('click', (event) => {
                // Prevent outside-click handler from closing the chat when choosing a language
                event.stopPropagation();
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

        // Start het gesprek in de gekozen taal zonder het technische bericht te tonen.
        this.showTypingIndicator();
        this.isLoading = true;
        this.chatSend.disabled = true;

        this.sendToApi(triggerMessage)
            .then(rawOutput => {
                const payload = this.normalizePayload(rawOutput);
                this.hideTypingIndicator();
                const botMessage = this.createBotMessageFromPayload(payload);
                this.chatMessages.appendChild(botMessage);
            })
            .catch(error => {
                console.error('Language start error:', error);
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
                this.scrollToBottom();
            });
    }
    
    parseMarkdown(text) {
        // Convert Markdown to HTML
        return text
            // Bold: **text** or __text__
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/__(.+?)__/g, '<strong>$1</strong>')
            // Italic: *text* or _text_
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/_(.+?)_/g, '<em>$1</em>')
            // Links: [text](url)
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            // Line breaks: double newline = paragraph
            .replace(/\n\n/g, '</p><p>')
            // Single newline = br
            .replace(/\n/g, '<br>')
            // Bullet lists: • or - or *
            .replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>')
            // Numbered lists: 1. 2. etc
            .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
            // Wrap consecutive <li> in <ul>
            .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')
            .replace(/<\/ul>\s*<ul>/g, ''); // Merge adjacent <ul>
    }

    normalizePayload(rawOutput) {
        // Backend returns output as either an object or a JSON string.
        let payload = rawOutput;
        if (typeof payload === 'string') {
            try {
                payload = JSON.parse(payload);
            } catch (e) {
                // Wrap plain text in a minimal payload
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

        // Remember last language used by the bot
        this.currentLanguage = payload.language;

        return payload;
    }
    
    createMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'bot') {
            // Parse Markdown for bot messages
            const parsed = this.parseMarkdown(content);
            contentDiv.innerHTML = `<p>${parsed}</p>`;
        } else {
            // Plain text for user messages
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }

    createBotMessageFromPayload(payload) {
        // Main bot message with markdown text
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        const parsed = this.parseMarkdown(payload.text || '');
        contentDiv.innerHTML = `<p>${parsed}</p>`;
        messageDiv.appendChild(contentDiv);

        // Optional afvalplaats image
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

        // Dynamic buttons (bijvoorbeeld Ja/Nee)
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
                    // Toon wat de gebruiker gekozen heeft
                    const userMessage = this.createMessage(value, 'user');
                    this.chatMessages.appendChild(userMessage);
                    this.scrollToBottom();

                    // Stuur de waarde als volgende bericht naar de backend
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
        
        if (!data.output && !data.error) {
            throw new Error('Invalid response format');
        }
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Backend returns the structured UI payload under "output"
        return data.output;
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