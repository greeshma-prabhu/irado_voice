# Irado Chatbot API - Cloudflare Integration

Dieses Repository enthält OpenAPI-Schemas und Cloudflare-Konfigurationen für den Irado Chatbot.

## 📁 Dateien

- `openapi.yaml` - Standard OpenAPI 3.0 Schema
- `cloudflare-openapi.yaml` - Cloudflare-optimiertes OpenAPI Schema
- `cloudflare-worker.js` - Cloudflare Worker Implementation
- `cloudflare-pages-function.js` - Cloudflare Pages Function
- `wrangler.toml` - Cloudflare Workers Konfiguration

## 🚀 Cloudflare Workers Setup

### 1. Installation

```bash
npm install -g wrangler
wrangler login
```

### 2. Deployment

```bash
# Development
wrangler dev

# Production
wrangler deploy
```

### 3. Environment Variables

```bash
wrangler secret put BACKEND_URL
# Wert: http://localhost:5000/webhook/chat
```

## 🌐 Cloudflare Pages Functions

### 1. Pages Function Setup

Erstellen Sie eine `functions/api/chat.js` Datei in Ihrem Pages-Projekt:

```javascript
// functions/api/chat.js
export { onRequest } from './cloudflare-pages-function.js';
```

### 2. Environment Variables

In der Cloudflare Pages Dashboard:
- `BACKEND_URL`: `http://localhost:5000/webhook/chat`

## 📊 API Endpoints

### Chat API
```
POST /api/chat
Content-Type: application/json
Authorization: Basic <base64-encoded-credentials>

{
  "sessionId": "user_123_session",
  "action": "sendMessage", 
  "chatInput": "Wann wird mein Grofvuil abgeholt?"
}
```

### Health Check
```
GET /api/health
```

## 🔧 CORS Konfiguration

Die API unterstützt CORS für alle Origins:

```javascript
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
  'Access-Control-Max-Age': '86400',
};
```

## 🛡️ Rate Limiting

Implementiert mit Cloudflare KV:

```javascript
const rateLimitKey = `rate_limit_${sessionId}`;
const rateLimit = await env.CHATBOT_KV?.get(rateLimitKey);
if (rateLimit && parseInt(rateLimit) > 10) {
  return new Response(JSON.stringify({ 
    error: 'Rate limit exceeded' 
  }), { status: 429 });
}
```

## 📈 Monitoring

### Cloudflare Analytics
- Automatisch aktiviert in `wrangler.toml`
- Metriken: Requests, Errors, Response Times

### Custom Logging
```javascript
console.log('Chatbot API Request:', {
  sessionId: body.sessionId,
  timestamp: new Date().toISOString(),
  region: request.cf.colo
});
```

## 🔐 Security

### Authentication
- Basic Auth: `irado:20Irado25!`
- Cloudflare Access (optional)

### Rate Limiting
- 10 Requests pro Stunde pro Session
- KV-basiert für Edge-Performance

## 🚀 Performance

### Edge Caching
```javascript
'Cache-Control': 'no-cache, no-store, must-revalidate'
```

### Cloudflare Features
- Edge Computing
- Global Distribution
- DDoS Protection
- SSL/TLS Termination

## 📝 OpenAPI Schema

### Standard Schema
```yaml
openapi: 3.0.3
info:
  title: Irado Chatbot API
  version: 1.0.0
```

### Cloudflare Schema
```yaml
openapi: 3.0.3
info:
  title: Irado Chatbot API (Cloudflare)
  version: 1.0.0
```

## 🧪 Testing

### cURL Examples
```bash
# Health Check
curl https://irado.mainfact.ai/api/health

# Chat Request
curl -X POST https://irado.mainfact.ai/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'irado:20Irado25!' | base64)" \
  -d '{"sessionId":"test","action":"sendMessage","chatInput":"Hallo"}'
```

### JavaScript Client
```javascript
const response = await fetch('https://irado.mainfact.ai/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + btoa('irado:20Irado25!')
  },
  body: JSON.stringify({
    sessionId: 'user_123',
    action: 'sendMessage',
    chatInput: 'Wann wird mein Grofvuil abgeholt?'
  })
});
```

## 🔄 Deployment Workflow

### 1. Development
```bash
wrangler dev --local
```

### 2. Staging
```bash
wrangler deploy --env staging
```

### 3. Production
```bash
wrangler deploy --env production
```

## 📞 Support

Bei Fragen oder Problemen:
- Email: irado@mainfact.ai
- Dokumentation: https://www.irado.nl
- API Schema: `/api/chat` OpenAPI 3.0

## 📄 Lizenz

Proprietary - Irado/Mainfact.ai
