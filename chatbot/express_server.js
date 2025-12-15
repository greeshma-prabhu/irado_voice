const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3254;

// Enable CORS for all routes
app.use(cors({
  origin: ['https://irado.mainfact.ai', 'http://localhost:8080', 'http://127.0.0.1:8080'],
  credentials: true
}));

// Simple proxy for chatbot API - must come before static file serving
app.use('/api/chat', (req, res) => {
  console.log('Received request to /api/chat');
  
  // Forward to chatbot service
  const http = require('http');
  const options = {
    hostname: '127.0.0.1',
    port: 5000,
    path: '/api/chat',
    method: req.method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Basic ' + Buffer.from('irado:20Irado25!').toString('base64')
    }
  };
  
  const proxyReq = http.request(options, (proxyRes) => {
    let data = '';
    proxyRes.on('data', (chunk) => {
      data += chunk;
    });
    proxyRes.on('end', () => {
      res.status(proxyRes.statusCode).json(JSON.parse(data));
    });
  });
  
  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Proxy error' });
  });
  
  if (req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });
    req.on('end', () => {
      proxyReq.write(body);
      proxyReq.end();
    });
  } else {
    proxyReq.end();
  }
});

// Serve static files from the website directory (after API routes)
app.use(express.static('/opt/irado/website'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Test endpoint for debugging
app.get('/api/test', (req, res) => {
  res.json({ message: 'Express server is working', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Express server running on port ${PORT}`);
  console.log(`Website available at: http://localhost:${PORT}`);
  console.log(`Chatbot API available at: http://localhost:${PORT}/api/chat`);
});
