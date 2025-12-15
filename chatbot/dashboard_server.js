const express = require('express');
const path = require('path');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = 3256;

// Enable CORS for all routes
app.use(cors({
  origin: ['https://irado.mainfact.ai', 'http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:3255'],
  credentials: true
}));

// Parse JSON bodies
app.use(express.json());

// Dashboard API proxy - forward to Flask dashboard service
app.use('/api/koad*', (req, res) => {
  console.log(`Dashboard API request: ${req.method} ${req.url}`);
  
  const http = require('http');
  const options = {
    hostname: '127.0.0.1',
    port: 3255, // Dashboard Flask service port (internal)
    path: req.url,
    method: req.method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
  
  const proxyReq = http.request(options, (proxyRes) => {
    let data = '';
    proxyRes.on('data', (chunk) => {
      data += chunk;
    });
    proxyRes.on('end', () => {
      try {
        const jsonData = JSON.parse(data);
        res.status(proxyRes.statusCode).json(jsonData);
      } catch (e) {
        res.status(proxyRes.statusCode).send(data);
      }
    });
  });
  
  proxyReq.on('error', (err) => {
    console.error('Dashboard proxy error:', err);
    res.status(500).json({ error: 'Dashboard service unavailable' });
  });
  
  if (req.method === 'POST' || req.method === 'PUT') {
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

// Chat history API proxy
app.use('/api/chat*', (req, res) => {
  console.log(`Chat API request: ${req.method} ${req.url}`);
  
  const http = require('http');
  const options = {
    hostname: '127.0.0.1',
    port: 3255, // Dashboard Flask service port (internal)
    path: req.url,
    method: req.method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
  
  const proxyReq = http.request(options, (proxyRes) => {
    let data = '';
    proxyRes.on('data', (chunk) => {
      data += chunk;
    });
    proxyRes.on('end', () => {
      try {
        const jsonData = JSON.parse(data);
        res.status(proxyRes.statusCode).json(jsonData);
      } catch (e) {
        res.status(proxyRes.statusCode).send(data);
      }
    });
  });
  
  proxyReq.on('error', (err) => {
    console.error('Chat API proxy error:', err);
    res.status(500).json({ error: 'Chat service unavailable' });
  });
  
  if (req.method === 'POST' || req.method === 'PUT') {
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

// Dashboard static files
app.use('/static', express.static('/opt/irado/chatbot/dashboard/static'));

// Dashboard main page
app.get('/', (req, res) => {
  res.sendFile('/opt/irado/chatbot/dashboard/templates/dashboard.html');
});

// Dashboard route
app.get('/dashboard', (req, res) => {
  res.sendFile('/opt/irado/chatbot/dashboard/templates/dashboard.html');
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'dashboard-server',
    timestamp: new Date().toISOString() 
  });
});

// Start Flask dashboard service
let flaskProcess = null;

function startFlaskService() {
  console.log('Starting Flask dashboard service...');
  
  flaskProcess = spawn('/opt/irado/chatbot/dashboard/venv/bin/python', [
    '/opt/irado/chatbot/dashboard/dashboard.py'
  ], {
    cwd: '/opt/irado/chatbot/dashboard',
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });
  
  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask error: ${data}`);
  });
  
  flaskProcess.on('close', (code) => {
    console.log(`Flask process exited with code ${code}`);
    // Restart after 5 seconds if it crashes
    setTimeout(startFlaskService, 5000);
  });
  
  flaskProcess.on('error', (err) => {
    console.error('Failed to start Flask service:', err);
  });
}

// Start Flask service
startFlaskService();

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  if (flaskProcess) {
    flaskProcess.kill();
  }
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Shutting down gracefully...');
  if (flaskProcess) {
    flaskProcess.kill();
  }
  process.exit(0);
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Dashboard Express server running on port ${PORT}`);
  console.log(`Dashboard available at: http://localhost:${PORT}`);
  console.log(`Dashboard API available at: http://localhost:${PORT}/api/koad`);
  console.log(`Chat API available at: http://localhost:${PORT}/api/chat`);
  console.log(`Flask service running internally on port 3255`);
});
