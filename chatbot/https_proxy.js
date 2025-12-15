const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3001;

// Enable CORS for all routes
app.use(cors({
  origin: ['https://irado.mainfact.ai', 'http://localhost:8080', 'http://127.0.0.1:8080'],
  credentials: true
}));

// Serve static files from the website directory
app.use(express.static('/opt/irado/website'));

// Proxy for chatbot API - handle requests from external domain
app.use('/api/chat', createProxyMiddleware({
  target: 'http://127.0.0.1:5000', // Target the Python Flask app
  changeOrigin: true,
  pathRewrite: {
    '^/api/chat': '/webhook/chat' // Rewrite /api/chat to /webhook/chat for the Flask app
  },
  onProxyReq: (proxyReq, req, res) => {
    // Add basic auth header
    const auth = Buffer.from('irado:20Irado25!').toString('base64');
    proxyReq.setHeader('Authorization', `Basic ${auth}`);
    proxyReq.setHeader('Content-Type', 'application/json');
    proxyReq.setHeader('Accept', 'application/json');
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Proxy error' });
  }
}));

// Health check endpoint for the HTTPS proxy
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`HTTPS Proxy server running on port ${PORT}`);
  console.log(`Website available at: http://localhost:${PORT}`);
  console.log(`Chatbot API available at: http://localhost:${PORT}/api/chat`);
  console.log(`External domain requests will be proxied to our chatbot service`);
});



