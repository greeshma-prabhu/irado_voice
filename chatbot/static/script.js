class IradoChat {
    constructor() {
        this.sessionId = this.getOrCreateSessionId();
        this.voiceSessionId = this.getOrCreateVoiceSessionId();
        this.isOpen = false;
        this.isLoading = false;
        this.isVoiceListening = false;
        this.voiceRecognition = null;
        // Keep track of the active language; default is Dutch.
        this.currentLanguage = 'nl';
        // Voice session greeting state
        this.hasGreeted = sessionStorage.getItem('irado_voice_has_greeted') === '1';
        // URL for the afvalplaats image served by the chatbot backend.
        // This image shows clearly where residents should place bulky waste.
        this.apiBaseUrl = this.getApiBaseUrl();
        this.afvalplaatsImageUrl = `${this.apiBaseUrl}/media/afvalplaats.png`;
        // Voice-only mode: do not render text buttons in voice modal
        this.voiceOnlyResponses = true;
        
        this.apiConfig = this.getApiConfig();
        // Bind methods used as event handlers
        this.updateChatHeight = this.updateChatHeight.bind(this);
        
        this.initializeElements();
        this.bindEvents();
    }
    
    getOrCreateSessionId() {
        const storageKey = 'irado_chat_session_id';
        const languageKey = 'irado_chat_language';
        
        let sessionId = sessionStorage.getItem(storageKey);
        let savedLanguage = sessionStorage.getItem(languageKey);
        const greetingKey = 'irado_voice_has_greeted';
        
        if (!sessionId) {
            sessionId = this.generateSessionId();
            sessionStorage.setItem(storageKey, sessionId);
            // Clear saved language for new session
            sessionStorage.removeItem(languageKey);
            sessionStorage.removeItem(greetingKey);
        } else if (savedLanguage) {
            // Restore language for existing session
            this.currentLanguage = savedLanguage;
        }
        
        return sessionId;
    }

    getOrCreateVoiceSessionId() {
        const storageKey = 'irado_voice_session_id';
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
        sessionStorage.removeItem('irado_voice_has_greeted');
        this.sessionId = this.getOrCreateSessionId();
        // Also reset voice session to avoid mixed-language history
        sessionStorage.removeItem('irado_voice_session_id');
        this.voiceSessionId = this.getOrCreateVoiceSessionId();
        
        this.chatMessages.innerHTML = '';
        this.currentLanguage = 'nl';
        this.hasGreeted = false;
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

        // If running locally (localhost or 127.0.0.1), use same origin
        if (host === 'localhost' || host === '127.0.0.1' || host.startsWith('127.')) {
            return window.location.origin;
        }

        // Default: production chatbot API
        return 'https://irado-chatbot-app.azurewebsites.net';
    }
    
    initializeElements() {
        // Action buttons (CALL and VOICE only)
        this.callBtn = document.getElementById('callBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        
        // Chat widget (original - DO NOT BREAK - Armin's code)
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
        // Action buttons (CALL and VOICE only)
        if (this.callBtn) {
            this.callBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.initiateCall();
            });
        }
        if (this.voiceBtn) {
            this.voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openVoiceInput();
            });
        }
        
        // Original chat widget (DO NOT BREAK - Armin's code)
        if (this.chatToggle) {
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        }
        if (this.chatClose) {
        this.chatClose.addEventListener('click', () => this.closeChat());
        }
        if (this.chatExpand) {
        this.chatExpand.addEventListener('click', () => this.expandChat());
        }
        if (this.chatSend) {
        this.chatSend.addEventListener('click', () => this.sendMessage());
        }
        if (this.chatInput) {
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        }
        
        document.addEventListener('click', (e) => {
            // Do not close when clicking inside the chat window (including language/buttons)
            // Also don't close when clicking action buttons
            const actionButtons = document.querySelector('.action-buttons');
            const isActionButton = actionButtons && actionButtons.contains(e.target);
            const isChatToggle = this.chatToggle && this.chatToggle.contains(e.target);
            const isChatWindow = this.chatWindow && this.chatWindow.contains(e.target);
            
            if (this.isOpen && !isChatWindow && !isChatToggle && !isActionButton) {
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
        // Close voice interface if open
        this.closeVoiceInterface();
        
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

        // Always show language selector on fresh open (unless there are active messages)
        const hasMessages = this.chatMessages.querySelectorAll('.message').length > 0;
        
        if (!hasMessages) {
            // Clear chat and show language selector
        this.chatMessages.innerHTML = '';
            // Clear saved language to force fresh selection
            sessionStorage.removeItem('irado_chat_language');
            this.currentLanguage = 'nl';
        this.renderLanguageSelector();
        }
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
    
    closeVoiceInterface() {
        // Close voice modal if it exists and is open
        const voiceModal = document.getElementById('voice-modal');
        if (voiceModal) {
            this.closeVoiceModal();
        }
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
        
        // Save language choice to session storage
        sessionStorage.setItem('irado_chat_language', langCode);

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

        // In voice-only mode, lock language to the user's selection
        if (this.voiceOnlyResponses && this.currentLanguage) {
            payload.language = this.currentLanguage;
        } else {
            this.currentLanguage = payload.language;
        }

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
    
    async sendToApi(message, language = null, allowGreeting = null, isVoice = false) {
        const storedLanguage = sessionStorage.getItem('irado_chat_language');
        const requestData = {
            sessionId: isVoice ? (this.voiceSessionId || this.sessionId) : this.sessionId,
            action: 'sendMessage',
            chatInput: message,
            timestamp: Date.now(),
            source: 'website'
        };
        requestData.language = language || storedLanguage || this.currentLanguage || 'dutch';
        if (allowGreeting !== null && allowGreeting !== undefined) {
            requestData.allowGreeting = !!allowGreeting;
        }
        if (isVoice) {
            requestData.is_voice = true;
            requestData.debug = true;
        }
        
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
        if (data.debug) {
            console.log('DEBUG: Chat response info:', data.debug);
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
    
    closeVoiceInterface() {
        // Close voice modal if it exists and is open
        const voiceModal = document.getElementById('voice-modal');
        if (voiceModal) {
            if (window.voiceInterface && typeof window.voiceInterface.close === 'function') {
                window.voiceInterface.close();
            } else {
                voiceModal.remove();
            }
        }
    }
    
    initiateCall() {
        // Show phone number and initiate call
        const phoneNumber = '+31XXXXXXXXX'; // Get from config
        const message = `Bel ons op ${phoneNumber} voor spraakondersteuning.\n\nKlik hier om direct te bellen:`;
        
        // Open chat to show message
        if (!this.isOpen) {
            this.toggleChat();
        }
        
        this.addMessage('bot', message);
        this.addMessage('bot', `📞 <a href="tel:${phoneNumber}" style="color: #10b981; font-weight: 600; text-decoration: none;">${phoneNumber}</a>`, true);
        
        // In production, this would initiate a call via Azure Communication Services
        console.log('Call initiated - would connect to Azure Communication Services');
    }
    
    openVoiceInput() {
        // Close chat widget if open
        if (this.isOpen) {
            this.closeChat();
        }
        
        // Open voice interface modal
        this.openVoiceModal();
    }
    
    openVoiceModal() {
        // Close chat if open
        if (this.chatWindow && this.chatWindow.style.display === 'flex') {
            this.closeChat();
        }
        
        // Reset any recording state - CLEAN STATE
        this.isRecording = false;
        this.audioChunks = [];
        this.recordingStartTime = null;
        
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        if (this.currentAudioStream) {
            this.currentAudioStream.getTracks().forEach(track => track.stop());
            this.currentAudioStream = null;
        }
        
        // Create voice modal if it doesn't exist
        let voiceModal = document.getElementById('voice-modal');
        
        if (voiceModal) {
            // Already exists, just show it and re-attach listeners
            voiceModal.style.display = 'flex';
            this.attachVoiceEventListeners();
            this.loadVoiceHistory();
            return;
        }
        
        // Create new modal with WhatsApp-style interface
        voiceModal = document.createElement('div');
        voiceModal.id = 'voice-modal';
        voiceModal.innerHTML = `
            <div class="voice-container">
                <div class="voice-header">
                    <h3>Voice Assistant</h3>
                    <button class="close-btn" id="voice-close-btn">×</button>
                </div>
                <div class="voice-message-container" id="voice-message-container">
                    <!-- Voice message bubbles will be shown here -->
                </div>
                <div class="voice-controls">
                    <button class="mic-button" id="voice-record-btn">
                        <span class="mic-icon">🎤</span>
                        <span class="mic-text">Hold to Record</span>
                    </button>
                <div class="recording-status" id="recording-status" style="display: none;">
                    <span class="recording-indicator">🔴</span>
                    <span class="recording-timer" id="recording-timer">00:00</span>
                    <span class="recording-text">Recording...</span>
                    <button class="stop-btn" id="stop-recording-btn">Stop & Send</button>
                    <button class="cancel-btn" id="cancel-recording-btn">Cancel</button>
                </div>
                </div>
            </div>
        `;
        document.body.appendChild(voiceModal);
        
        // Bind close button
        document.getElementById('voice-close-btn').addEventListener('click', () => {
            this.closeVoiceModal();
        });
        
        // Attach event listeners
        this.attachVoiceEventListeners();
    }
    
    attachVoiceEventListeners() {
        // Bind recording button - HOLD TO RECORD (WhatsApp style)
        const recordBtn = document.getElementById('voice-record-btn');
        const recordingStatus = document.getElementById('recording-status');
        
        // Initialize recording state - CLEAN STATE
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingTimer = null;
        this.recordingStartTime = null;
        this.currentAudioStream = null;
        
        // Remove any existing listeners by cloning the button
        if (recordBtn) {
            const newBtn = recordBtn.cloneNode(true);
            recordBtn.parentNode.replaceChild(newBtn, recordBtn);
        }
        
        // Get fresh reference after clone
        const freshBtn = document.getElementById('voice-record-btn');
        if (!freshBtn) return;
        
        // DESKTOP: Mouse events
        freshBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('mousedown - starting recording');
            this.startVoiceRecording();
        });
        
        freshBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('mouseup - stopping recording, isRecording:', this.isRecording);
            if (this.isRecording) {
                this.stopAndSendVoiceMessage();
            }
        });
        
        // No mouseleave handler: recording should not cancel when cursor drifts.
        
        // MOBILE: Touch events
        freshBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('touchstart - starting recording');
            this.startVoiceRecording();
        });
        
        freshBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('touchend - stopping recording, isRecording:', this.isRecording);
            if (this.isRecording) {
                this.stopAndSendVoiceMessage();
            }
        });
        
        freshBtn.addEventListener('touchcancel', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (this.isRecording) {
                console.log('touchcancel - canceling recording');
                this.cancelRecording();
            }
        });
        
        // Add stop button handler
        const stopBtn = document.getElementById('stop-recording-btn');
        if (stopBtn) {
            stopBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.isRecording) {
                    this.stopAndSendVoiceMessage();
                }
            });
        }

        // Add cancel button handler
        const cancelBtn = document.getElementById('cancel-recording-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (this.isRecording) {
                    this.cancelRecording();
                }
            });
        }
        
        // Check if language is selected, if not show language selector
        const hasLanguage = sessionStorage.getItem('irado_chat_language');
        if (!hasLanguage) {
            this.renderVoiceLanguageSelector();
        } else {
            this.currentLanguage = hasLanguage;
            this.loadVoiceHistory();
        }
    }
    
    renderVoiceLanguageSelector() {
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        const intro = document.createElement('div');
        intro.className = 'voice-message bot';
        intro.innerHTML = '<p style="padding: 1rem; text-align: center; color: #666;">Kies een taal om het gesprek te starten:</p>';
        container.appendChild(intro);
        
        const wrapper = document.createElement('div');
        wrapper.className = 'voice-language-selector';
        wrapper.style.cssText = 'display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; padding: 1rem;';
        
        const languages = [
            { code: 'nl', label: 'Nederlands', trigger: 'start chat - language: dutch' },
            { code: 'en', label: 'English', trigger: 'start chat - language: english' },
            { code: 'tr', label: 'Türkçe', trigger: 'start chat - language: turkish' },
            { code: 'ar', label: 'العربية', trigger: 'start chat - language: arabic' },
        ];
        
        languages.forEach(lang => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'voice-language-button';
            btn.style.cssText = 'flex: 1 1 45%; padding: 0.5rem 0.75rem; border-radius: 999px; border: 2px solid #0084ff; background: white; color: #0084ff; cursor: pointer; font-size: 0.9rem; transition: all 0.2s;';
            btn.textContent = lang.label;
            btn.addEventListener('click', () => {
                this.handleVoiceLanguageSelection(lang.code, lang.trigger);
            });
            wrapper.appendChild(btn);
        });
        
        container.appendChild(wrapper);
    }
    
    async handleVoiceLanguageSelection(langCode, triggerMessage) {
        // Map short codes to full language names that backend expects
        const langMap = {
            'nl': 'dutch',
            'en': 'english',
            'tr': 'turkish',
            'ar': 'arabic'
        };
        
        this.currentLanguage = langMap[langCode] || 'dutch';
        sessionStorage.setItem('irado_chat_language', this.currentLanguage);
        // Start a fresh voice session per language selection
        sessionStorage.removeItem('irado_voice_session_id');
        this.voiceSessionId = this.getOrCreateVoiceSessionId();
        this.hasGreeted = false;
        sessionStorage.removeItem('irado_voice_has_greeted');
        
        const container = document.getElementById('voice-message-container');
        if (container) {
            container.innerHTML = '';
        }
        
        const status = document.getElementById('voice-status');
        if (status) {
            status.textContent = 'Initializing...';
        }
        
        const greetings = {
            nl: '👋 Hallo, ik ben de virtuele assistent van Irado. Fijn dat je er bent! Waarmee kan ik je vandaag helpen?',
            en: '👋 Hello, I am Irado’s virtual assistant. Nice to meet you! How can I help you today?',
            tr: '👋 Merhaba, ben Irado’nun sanal asistanıyım. Tanıştığımıza memnun oldum! Size bugün nasıl yardımcı olabilirim?',
            ar: '👋 مرحباً، أنا المساعد الافتراضي لِـ Irado. سعيد بلقائك! كيف يمكنني مساعدتك اليوم؟'
        };
        
        // Speak fixed greeting first (voice-only)
        try {
            this.showVoiceTypingIndicator();
            const greetingText = greetings[langCode] || greetings.nl;
            const botAudioBlob = await this.getTextToSpeechAudio(greetingText, this.currentLanguage);
            const botDuration = await this.calculateAudioDuration(botAudioBlob);
            await this.addVoiceMessage('bot', botAudioBlob, botDuration);
            this.hasGreeted = true;
            sessionStorage.setItem('irado_voice_has_greeted', '1');
            setTimeout(() => {
                const lastBotMessage = document.querySelector('.voice-message.bot:last-child .play-btn');
                if (lastBotMessage) {
                    this.playVoiceMessage(lastBotMessage);
                }
            }, 200);
            this.hideVoiceTypingIndicator();
        } catch (error) {
            console.error('Voice greeting error:', error);
            this.hideVoiceTypingIndicator();
        }
        
        // Send trigger message to initialize conversation (same as text chat)
        try {
            this.showVoiceTypingIndicator();
            await this.sendToApi(triggerMessage, this.currentLanguage, !this.hasGreeted, true);
            this.hideVoiceTypingIndicator();
            
            const status = document.getElementById('voice-status');
            if (status) {
                status.textContent = 'Click microphone to speak';
            }
        } catch (error) {
            console.error('Voice language start error:', error);
            this.hideVoiceTypingIndicator();
            if (status) {
                status.textContent = 'Error: ' + error.message;
            }
        }
    }
    
    loadVoiceHistory() {
        // Voice modal should start fresh - don't load chat history
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        // Always start fresh - clear any previous messages
        container.innerHTML = '';
    }
    
    showVoiceTypingIndicator() {
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        const typing = document.createElement('div');
        typing.className = 'voice-message bot typing-indicator';
        typing.id = 'voice-typing-indicator';
        typing.innerHTML = `
            <span class="icon">🔊</span>
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        container.appendChild(typing);
        container.scrollTop = container.scrollHeight;
    }
    
    hideVoiceTypingIndicator() {
        const typing = document.getElementById('voice-typing-indicator');
        if (typing) {
            typing.remove();
        }
    }
    
    async addVoiceMessage(type, audioBlob, duration = null) {
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        // Get duration if not provided
        if (!duration) {
            duration = await this.calculateAudioDuration(audioBlob);
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `voice-message ${type}`;
        
        const audioUrl = URL.createObjectURL(audioBlob);
        messageDiv.dataset.audioUrl = audioUrl;
        
        const icon = type === 'user' ? '🎤' : '🔊';
        const playIcon = '▶';
        
        messageDiv.innerHTML = `
            ${type === 'user' ? `
                <button class="play-btn" onclick="window.iradoChat.playVoiceMessage(this)">${playIcon}</button>
                <div class="waveform">
                    <div class="waveform-bars">
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                    </div>
                </div>
                <span class="duration">${duration}</span>
                <span class="icon">${icon}</span>
            ` : `
                <span class="icon">${icon}</span>
                <div class="waveform">
                    <div class="waveform-bars">
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                        <span class="wave-bar"></span>
                    </div>
                </div>
                <span class="duration">${duration}</span>
                <button class="play-btn" onclick="window.iradoChat.playVoiceMessage(this)">${playIcon}</button>
            `}
        `;
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
        
        // Auto-play bot messages
        if (type === 'bot') {
            setTimeout(() => {
                this.playVoiceMessage(messageDiv.querySelector('.play-btn'));
            }, 300);
        }
    }
    
    updateMessageDuration(messageElement, duration) {
        if (messageElement) {
            const durationSpan = messageElement.querySelector('.duration');
            if (durationSpan) {
                durationSpan.textContent = duration;
            }
        }
    }
    
    playVoiceMessage(playBtn) {
        const messageDiv = playBtn.closest('.voice-message');
        if (!messageDiv) return;
        
        const audioUrl = messageDiv.dataset.audioUrl;
        if (!audioUrl) return;
        
        const sameMessage = this.currentAudioMessage === messageDiv;
        const audio = sameMessage && this.currentAudio ? this.currentAudio : new Audio(audioUrl);
        
        if (!sameMessage && this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
        
        this.currentAudio = audio;
        this.currentAudioMessage = messageDiv;
        
        // Reset all play buttons except the active one
        document.querySelectorAll('.play-btn').forEach(btn => {
            if (btn !== playBtn) {
                btn.textContent = '▶';
            }
        });
        
        playBtn.textContent = audio.paused ? '⏸' : '▶';
        
        if (!audio._iradoBound) {
            audio._iradoBound = true;
            audio.addEventListener('ended', () => {
                if (this.currentAudioMessage === messageDiv) {
                    playBtn.textContent = '▶';
                    this.currentAudio = null;
                    this.currentAudioMessage = null;
                }
            });
            audio.addEventListener('pause', () => {
                if (this.currentAudioMessage === messageDiv) {
                    playBtn.textContent = '▶';
                }
            });
            audio.addEventListener('play', () => {
                if (this.currentAudioMessage === messageDiv) {
                    playBtn.textContent = '⏸';
                }
            });
        }
        
        // Toggle play/pause without restarting
        if (audio.paused) {
            const playPromise = audio.play();
            if (playPromise && typeof playPromise.catch === 'function') {
                // Autoplay can be blocked; ignore and let user click play
                playPromise.catch((error) => {
                    console.warn('Audio play blocked:', error);
                });
            }
        } else {
            audio.pause();
        }
    }
    
    closeVoiceModal() {
        const voiceModal = document.getElementById('voice-modal');
        if (voiceModal) {
            // Cancel any active recording
            if (this.isRecording) {
                this.cancelRecording();
            }
            voiceModal.style.display = 'none';
        }
    }
    
    // Removed - using new recording system
    
    startVoiceInput() {
        // Check if browser supports speech recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            const status = document.getElementById('voice-status');
            if (status) {
                status.textContent = 'Spraakherkenning wordt niet ondersteund in uw browser.';
            }
            return;
        }
        
        // Check if language is selected
        const hasLanguage = sessionStorage.getItem('irado_chat_language');
        if (!hasLanguage) {
            this.renderVoiceLanguageSelector();
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.voiceRecognition = new SpeechRecognition();
        
        // Map language codes to speech recognition languages
        const langMap = {
            'nl': 'nl-NL',
            'en': 'en-US',
            'ar': 'ar-SA',
            'tr': 'tr-TR',
            'dutch': 'nl-NL',
            'english': 'en-US',
            'arabic': 'ar-SA',
            'turkish': 'tr-TR'
        };
        this.voiceRecognition.lang = langMap[this.currentLanguage] || 'nl-NL';
        this.voiceRecognition.continuous = false;
        this.voiceRecognition.interimResults = false;
        
        const status = document.getElementById('voice-status');
        const micIcon = document.getElementById('mic-icon');
        
        this.voiceRecognition.onstart = () => {
            this.isVoiceListening = true;
            if (micIcon) {
                micIcon.classList.add('listening');
            }
            if (status) {
                status.textContent = '🎤 Luisteren... Spreek nu uw vraag in.';
            }
        };
        
        this.voiceRecognition.onresult = async (event) => {
            const userTranscript = event.results[0][0].transcript;
            this.isVoiceListening = false;
            
            if (micIcon) {
                micIcon.classList.remove('listening');
            }
            if (status) {
                status.textContent = 'Verwerken...';
            }
            
            // Show user message in voice modal
            this.addVoiceMessage('user', userTranscript);
            
            // Send to chatbot API using SAME method as text chat
            try {
                this.showVoiceTypingIndicator();
                
                // Use the EXACT same API call as text chatbot
            const rawOutput = await this.sendToApi(userTranscript, this.currentLanguage);
                const payload = this.normalizePayload(rawOutput);
                
                this.hideVoiceTypingIndicator();
                
                // Don't show bot text - only speak the response
                // Use Azure TTS via backend endpoint
                const status = document.getElementById('voice-status');
                if (status) {
                    status.textContent = 'Speaking...';
                }
                await this.speakTextAzure(payload.text, this.currentLanguage);
                if (status) {
                    status.textContent = 'Klik op de microfoon om opnieuw te spreken';
                }
                
                // Handle buttons if present (same as text chat) - show these
                if (!this.voiceOnlyResponses && Array.isArray(payload.buttons) && payload.buttons.length > 0) {
                    this.renderVoiceButtons(payload.buttons);
                }
                
                // Handle image if present (same as text chat) - show this
                if (payload.showAfvalplaatsImage) {
                    this.showVoiceImage();
                }
                
                if (status) {
                    status.textContent = 'Klik op de microfoon om opnieuw te spreken';
                }
            } catch (error) {
                console.error('Voice API error:', error);
                this.hideVoiceTypingIndicator();
                // Don't show error text - speak it instead
                const errorMsg = 'Sorry, er is een fout opgetreden. Probeer het later opnieuw.';
                await this.speakTextAzure(errorMsg, this.currentLanguage);
                if (status) {
                    status.textContent = 'Fout: ' + error.message;
                }
            }
        };
        
        this.voiceRecognition.onerror = (event) => {
            this.isVoiceListening = false;
            if (micIcon) {
                micIcon.classList.remove('listening');
            }
            if (status) {
                status.textContent = 'Er is een fout opgetreden. Probeer het opnieuw.';
            }
        };
        
        this.voiceRecognition.onend = () => {
            this.isVoiceListening = false;
            if (micIcon) {
                micIcon.classList.remove('listening');
            }
        };
        
        this.voiceRecognition.start();
    }
    
    async speakTextAzure(text, language) {
        // Use Azure TTS via backend endpoint
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${this.apiConfig.auth}`
                },
                body: JSON.stringify({
                    text: text,
                    language: language
                })
            });
            
            if (!response.ok) {
                throw new Error(`TTS API error: ${response.status}`);
            }
            
            // Get audio blob
            const audioBlob = await response.blob();
            
            // Play audio
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            return new Promise((resolve, reject) => {
                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    resolve();
                };
                audio.onerror = (e) => {
                    URL.revokeObjectURL(audioUrl);
                    reject(e);
                };
                audio.play().catch(reject);
            });
        } catch (error) {
            console.error('Azure TTS error:', error);
            throw error;
        }
    }
    
    async speakTextBrowser(text) {
        // Fallback: Use browser's built-in SpeechSynthesis API
        if (!('speechSynthesis' in window)) {
            console.warn('Text-to-speech not supported in this browser');
            return;
        }
        
        return new Promise((resolve, reject) => {
            // Map language codes to speech synthesis languages
            const langMap = {
                'nl': 'nl-NL',
                'en': 'en-US',
                'ar': 'ar-SA',
                'tr': 'tr-TR',
                'dutch': 'nl-NL',
                'english': 'en-US',
                'arabic': 'ar-SA',
                'turkish': 'tr-TR'
            };
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = langMap[this.currentLanguage] || 'nl-NL';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            utterance.onend = () => resolve();
            utterance.onerror = (e) => reject(e);
            
            window.speechSynthesis.speak(utterance);
        });
    }
    
    // showVoiceTypingIndicator is already defined above with new structure
    
    hideVoiceTypingIndicator() {
        const typing = document.getElementById('voice-typing-indicator');
        if (typing) {
            typing.remove();
        }
    }
    
    renderVoiceButtons(buttons) {
        if (this.voiceOnlyResponses) return;
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        const buttonsWrapper = document.createElement('div');
        buttonsWrapper.className = 'voice-buttons';
        buttonsWrapper.style.cssText = 'display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; padding: 1rem;';
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'voice-button';
            button.style.cssText = 'padding: 0.5rem 1rem; border-radius: 0.5rem; border: none; background: #0084ff; color: white; cursor: pointer; font-size: 0.9rem; transition: all 0.2s;';
            button.textContent = btn.label || btn.value || '';
            
            button.addEventListener('click', async () => {
                const value = btn.value || btn.label || '';
                if (!value) return;
                
                // Send to API (same as text chat)
                try {
                    this.showVoiceTypingIndicator();
                    const rawOutput = await this.sendToApi(value, this.currentLanguage);
                    const payload = this.normalizePayload(rawOutput);
                    this.hideVoiceTypingIndicator();
                    
                    // Get bot response as audio
                    const botAudioBlob = await this.getTextToSpeechAudio(payload.text, this.currentLanguage);
                    const botDuration = await this.calculateAudioDuration(botAudioBlob);
                    await this.addVoiceMessage('bot', botAudioBlob, botDuration);
                    
                    // Auto-play bot response
                    setTimeout(() => {
                        const lastBotMessage = document.querySelector('.voice-message.bot:last-child .play-btn');
                        if (lastBotMessage) {
                            this.playVoiceMessage(lastBotMessage);
                        }
                    }, 300);
                } catch (error) {
                    console.error('Voice button error:', error);
                    this.hideVoiceTypingIndicator();
                }
            });
            
            buttonsWrapper.appendChild(button);
        });
        
        container.appendChild(buttonsWrapper);
        container.scrollTop = container.scrollHeight;
    }
    
    showVoiceImage() {
        const container = document.getElementById('voice-message-container');
        if (!container) return;
        
        const imageWrapper = document.createElement('div');
        imageWrapper.className = 'voice-image-wrapper';
        imageWrapper.style.cssText = 'margin-top: 0.5rem; padding: 1rem;';
        
        const img = document.createElement('img');
        img.src = this.afvalplaatsImageUrl;
        img.alt = 'Voorbeeld van waar u het grofvuil neer mag zetten.';
        img.className = 'voice-image';
        img.style.cssText = 'max-width: 100%; border-radius: 0.5rem;';
        
        imageWrapper.appendChild(img);
        container.appendChild(imageWrapper);
        container.scrollTop = container.scrollHeight;
    }
    
    // WhatsApp-style Hold-to-Record Functions
    async startVoiceRecording() {
        console.log('startVoiceRecording called, isRecording:', this.isRecording);
        
        if (this.isRecording) {
            console.log('Already recording, returning');
            return;
        }
        
        try {
            console.log('Requesting microphone...');
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });
            
            console.log('Microphone access granted');
            
            this.currentAudioStream = stream;
            this.audioChunks = [];
            
            // Create MediaRecorder with best supported Opus container
            const preferredTypes = [
                'audio/ogg;codecs=opus',
                'audio/webm;codecs=opus',
                'audio/webm'
            ];
            let selectedType = '';
            for (const type of preferredTypes) {
                if (MediaRecorder.isTypeSupported(type)) {
                    selectedType = type;
                    break;
                }
            }
            this.recordingMimeType = selectedType || 'audio/webm';
            this.mediaRecorder = selectedType
                ? new MediaRecorder(stream, { mimeType: selectedType })
                : new MediaRecorder(stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            // Start recording
            this.mediaRecorder.start(100); // Collect data every 100ms
            
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            console.log('Recording started, isRecording:', this.isRecording);
            
            // Update UI
            const recordBtn = document.getElementById('voice-record-btn');
            const recordingStatus = document.getElementById('recording-status');
            
            if (recordBtn) {
                recordBtn.style.display = 'none';
            }
            if (recordingStatus) {
                recordingStatus.style.display = 'flex';
            }
            
            // Start timer
            this.recordingTimer = setInterval(() => {
                this.updateRecordingTimer();
            }, 100);
            
        } catch (error) {
            console.error('Microphone access error:', error);
            alert('Cannot access microphone: ' + error.message);
            this.isRecording = false;
        }
    }
    
    updateRecordingTimer() {
        if (!this.recordingStartTime) return;
        
        const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
        const mins = Math.floor(elapsed / 60);
        const secs = elapsed % 60;
        
        const timerEl = document.getElementById('recording-timer');
        if (timerEl) {
            timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        // Auto-stop at 60 seconds (WhatsApp limit)
        if (elapsed >= 60) {
            this.stopAndSendVoiceMessage();
        }
    }
    
    cancelRecording() {
        if (!this.isRecording) return;
        
        // Stop recording
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        // Stop stream
        if (this.currentAudioStream) {
            this.currentAudioStream.getTracks().forEach(track => track.stop());
            this.currentAudioStream = null;
        }
        
        // Clear timer
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        // Reset state
        this.isRecording = false;
        this.audioChunks = [];
        this.recordingStartTime = null;
        
        // Reset UI
        const recordBtn = document.getElementById('voice-record-btn');
        const recordingStatus = document.getElementById('recording-status');
        
        if (recordBtn) {
            recordBtn.style.display = 'flex';
        }
        if (recordingStatus) {
            recordingStatus.style.display = 'none';
        }
    }
    
    async stopAndSendVoiceMessage() {
        if (!this.isRecording) return;
        
        // Stop recording
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        // Stop timer
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        // Wait for audio data
        await new Promise((resolve) => {
            if (this.mediaRecorder) {
                this.mediaRecorder.onstop = () => {
                    resolve();
                };
            } else {
                resolve();
            }
        });
        
        // Stop stream
        if (this.currentAudioStream) {
            this.currentAudioStream.getTracks().forEach(track => track.stop());
            this.currentAudioStream = null;
        }
        
        // Reset UI
        const recordBtn = document.getElementById('voice-record-btn');
        const recordingStatus = document.getElementById('recording-status');
        
        if (recordBtn) {
            recordBtn.style.display = 'flex';
        }
        if (recordingStatus) {
            recordingStatus.style.display = 'none';
        }
        
        // Check if we have audio
        if (this.audioChunks.length === 0) {
            this.isRecording = false;
            return;
        }
        
        // Create audio blob
        const blobType = this.recordingMimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: blobType });
        
        // Reset state
        this.isRecording = false;
        const audioChunks = [...this.audioChunks];
        this.audioChunks = [];
        this.recordingStartTime = null;
        
        // Process the message
        await this.processVoiceMessage(audioBlob);
    }
    
    async processVoiceMessage(audioBlob) {
        try {
            // 1. Show user's voice bubble
            const userDuration = await this.calculateAudioDuration(audioBlob);
            await this.addVoiceMessage('user', audioBlob, userDuration);
            
            // 2. Convert speech to text
            this.showVoiceTypingIndicator();
            
            const voiceLanguage = this.currentLanguage || sessionStorage.getItem('irado_chat_language') || 'dutch';
            if (this.currentLanguage !== voiceLanguage) {
                this.currentLanguage = voiceLanguage;
            }
            console.log('DEBUG: Voice language:', voiceLanguage);
            
            console.log('DEBUG: Audio blob size:', audioBlob.size, 'bytes');
            console.log('DEBUG: Audio blob type:', audioBlob.type);
            if (audioBlob.size === 0) {
                alert('Recording is empty - no audio captured');
                this.hideVoiceTypingIndicator();
                return;
            }
            if (audioBlob.size < 1000) {
                console.warn('WARNING: Audio blob very small, may not contain speech');
            }

            const formData = new FormData();
            const mimeType = this.recordingMimeType || 'audio/webm';
            const fileExt = mimeType.includes('ogg') ? 'ogg' : 'webm';
            console.log('DEBUG: File extension:', fileExt);
            formData.append('audio', audioBlob, `recording.${fileExt}`);
            formData.append('language', voiceLanguage);
            
            const sttResponse = await fetch(`${this.apiBaseUrl}/api/speech-to-text`, {
                method: 'POST',
                headers: {
                    'Authorization': `Basic ${this.apiConfig.auth}`
                },
                body: formData
            });
            
            if (!sttResponse.ok) {
                let details = '';
                try {
                    const errJson = await sttResponse.json();
                    details = errJson.error || errJson.message || JSON.stringify(errJson);
                } catch (e) {
                    try {
                        details = await sttResponse.text();
                    } catch (e2) {
                        details = '';
                    }
                }
                throw new Error(`Speech-to-text failed: ${sttResponse.status}${details ? ` - ${details}` : ''}`);
            }
            
            const sttData = await sttResponse.json();
            const userText = sttData.text || '';
            console.log('Voice STT text:', userText);
            console.log('Voice STT response:', sttData);
            
            if (!userText) {
                this.hideVoiceTypingIndicator();
                alert('Could not understand your voice. Please try again.');
                return;
            }
            
            // 3. Send to chatbot API (same as text chat)
            const rawOutput = await this.sendToApi(userText, voiceLanguage, !this.hasGreeted, true);
            const payload = this.normalizePayload(rawOutput);
            
            this.hideVoiceTypingIndicator();
            
            // 4. Convert bot response to speech
            const botText = payload.text || '';
            if (!botText) {
                return;
            }
            
            // Get bot audio
            const ttsResponse = await fetch(`${this.apiBaseUrl}/api/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${this.apiConfig.auth}`
                },
                body: JSON.stringify({
                    text: botText,
                    language: voiceLanguage
                })
            });
            
            if (!ttsResponse.ok) {
                throw new Error(`Text-to-speech failed: ${ttsResponse.status}`);
            }
            
            const botAudioBlob = await ttsResponse.blob();
            const botDuration = await this.calculateAudioDuration(botAudioBlob);
            
            // 5. Show bot's voice bubble
            await this.addVoiceMessage('bot', botAudioBlob, botDuration);
            if (!this.hasGreeted) {
                this.hasGreeted = true;
                sessionStorage.setItem('irado_voice_has_greeted', '1');
            }
            
            // 6. Auto-play bot response
            setTimeout(() => {
                const lastBotMessage = document.querySelector('.voice-message.bot:last-child .play-btn');
                if (lastBotMessage) {
                    this.playVoiceMessage(lastBotMessage);
                }
            }, 300);
            
            // Handle buttons if present
            if (!this.voiceOnlyResponses && Array.isArray(payload.buttons) && payload.buttons.length > 0) {
                this.renderVoiceButtons(payload.buttons);
            }
            
            // Handle image if present
            if (payload.showAfvalplaatsImage) {
                this.showVoiceImage();
            }
            
        } catch (error) {
            console.error('Voice message processing error:', error);
            this.hideVoiceTypingIndicator();
            alert('Error processing voice message: ' + error.message);
        }
    }
    
    async calculateAudioDuration(audioBlob) {
        return new Promise((resolve) => {
            // Estimate duration based on blob size (WebM/Opus is variable bitrate)
            const estimatedSeconds = audioBlob.size / 16000;
            
            if (estimatedSeconds > 0 && isFinite(estimatedSeconds)) {
                resolve(this.formatDuration(estimatedSeconds));
            } else {
                resolve('00:01');
            }
        });
    }
    
    formatDuration(seconds) {
        if (!seconds || isNaN(seconds) || !isFinite(seconds)) {
            return '00:01';
        }
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    async getTextToSpeechAudio(text, language) {
        const response = await fetch(`${this.apiBaseUrl}/api/text-to-speech`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Basic ${this.apiConfig.auth}`
            },
            body: JSON.stringify({
                text: text,
                language: language
            })
        });
        
        if (!response.ok) {
            throw new Error(`TTS failed: ${response.status}`);
        }
        
        return await response.blob();
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
