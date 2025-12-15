/**
 * Erweiterte Cloudflare Monitoring für Irado Chatbot API
 * Optimiert für Cloudflare Analytics, Logs und Alerts
 */

export default {
  async fetch(request, env, ctx) {
    const startTime = Date.now();
    const requestId = generateRequestId();
    
    // Cloudflare-spezifische Metadaten sammeln
    const cfMetadata = {
      requestId,
      timestamp: new Date().toISOString(),
      region: request.cf.colo,
      datacenter: request.cf.datacenter,
      country: request.cf.country,
      city: request.cf.city,
      timezone: request.cf.timezone,
      asn: request.cf.asn,
      asOrganization: request.cf.asOrganization,
      userAgent: request.headers.get('user-agent'),
      ip: request.headers.get('cf-connecting-ip'),
      rayId: request.headers.get('cf-ray'),
    };

    try {
      const response = await handleRequest(request, env, cfMetadata);
      
      // Performance-Metriken
      const processingTime = Date.now() - startTime;
      
      // Cloudflare Analytics Events
      await logAnalyticsEvent(env, {
        ...cfMetadata,
        status: response.status,
        processingTime,
        endpoint: new URL(request.url).pathname,
        method: request.method,
      });

      // Response mit Monitoring-Headers
      response.headers.set('X-Request-ID', requestId);
      response.headers.set('X-Processing-Time', processingTime.toString());
      response.headers.set('X-Cloudflare-Region', request.cf.colo);
      
      return response;

    } catch (error) {
      // Error Monitoring
      await logError(env, {
        ...cfMetadata,
        error: error.message,
        stack: error.stack,
        processingTime: Date.now() - startTime,
      });

      return new Response(JSON.stringify({ 
        error: 'Internal server error',
        requestId,
        timestamp: new Date().toISOString()
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};

/**
 * Request Handler mit erweitertem Monitoring
 */
async function handleRequest(request, env, metadata) {
  const url = new URL(request.url);
  
  // CORS Headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
    'Access-Control-Max-Age': '86400',
  };

  // CORS Preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  // Chat API mit detailliertem Monitoring
  if (url.pathname === '/api/chat') {
    return handleChatWithMonitoring(request, env, metadata, corsHeaders);
  }

  // Health Check mit System-Status
  if (url.pathname === '/api/health') {
    return handleHealthWithMonitoring(request, metadata, corsHeaders);
  }

  // Metrics Endpoint für Cloudflare Dashboard
  if (url.pathname === '/api/metrics') {
    return handleMetrics(request, env, metadata);
  }

  return new Response(JSON.stringify({ error: 'Not Found' }), {
    status: 404,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}

/**
 * Chat API mit erweitertem Monitoring
 */
async function handleChatWithMonitoring(request, env, metadata, corsHeaders) {
  const chatStartTime = Date.now();
  
  try {
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const body = await request.json();
    
    // Rate Limiting mit detailliertem Logging
    const rateLimitResult = await checkRateLimit(env, body.sessionId, metadata);
    if (!rateLimitResult.allowed) {
      await logRateLimitHit(env, {
        ...metadata,
        sessionId: body.sessionId,
        limit: rateLimitResult.limit,
        current: rateLimitResult.current,
      });
      
      return new Response(JSON.stringify({ 
        error: 'Rate limit exceeded',
        code: 'RATE_LIMIT',
        retryAfter: rateLimitResult.retryAfter
      }), {
        status: 429,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Backend API Call mit Monitoring
    const backendStartTime = Date.now();
    const backendUrl = env.BACKEND_URL || 'http://localhost:5000/webhook/chat';
    
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Basic ${btoa('irado:20Irado25!')}`,
        'X-Request-ID': metadata.requestId,
        'X-Cloudflare-Region': metadata.region,
      },
      body: JSON.stringify(body),
    });

    const backendTime = Date.now() - backendStartTime;
    const totalTime = Date.now() - chatStartTime;

    if (!backendResponse.ok) {
      await logBackendError(env, {
        ...metadata,
        backendStatus: backendResponse.status,
        backendTime,
        sessionId: body.sessionId,
      });
      
      throw new Error(`Backend error: ${backendResponse.status}`);
    }

    const responseData = await backendResponse.json();

    // Erfolgreiche Antwort mit detaillierten Metriken
    const response = {
      ...responseData,
      metadata: {
        processing_time: totalTime,
        backend_time: backendTime,
        cloudflare: {
          region: metadata.region,
          datacenter: metadata.datacenter,
          requestId: metadata.requestId,
        },
        rate_limit: {
          remaining: rateLimitResult.remaining,
          reset_time: rateLimitResult.resetTime,
        },
      },
    };

    // Success Metrics
    await logSuccessMetrics(env, {
      ...metadata,
      sessionId: body.sessionId,
      processingTime: totalTime,
      backendTime,
      responseLength: JSON.stringify(response).length,
    });

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'X-Processing-Time': totalTime.toString(),
        'X-Backend-Time': backendTime.toString(),
      },
    });

  } catch (error) {
    await logChatError(env, {
      ...metadata,
      error: error.message,
      processingTime: Date.now() - chatStartTime,
    });
    
    throw error;
  }
}

/**
 * Health Check mit System-Monitoring
 */
async function handleHealthWithMonitoring(request, metadata, corsHeaders) {
  const healthData = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    cloudflare: {
      region: metadata.region,
      datacenter: metadata.datacenter,
      country: metadata.country,
      city: metadata.city,
    },
    system: {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      version: '1.0.0',
    },
    monitoring: {
      requestId: metadata.requestId,
      rayId: metadata.rayId,
    },
  };

  return new Response(JSON.stringify(healthData), {
    status: 200,
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=60',
    },
  });
}

/**
 * Metrics Endpoint für Cloudflare Dashboard
 */
async function handleMetrics(request, env, metadata) {
  const metrics = await getMetrics(env);
  
  return new Response(JSON.stringify(metrics), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache',
    },
  });
}

/**
 * Rate Limiting mit detailliertem Monitoring
 */
async function checkRateLimit(env, sessionId, metadata) {
  const rateLimitKey = `rate_limit_${sessionId}`;
  const current = await env.CHATBOT_KV?.get(rateLimitKey) || 0;
  const limit = 10; // 10 requests per hour
  const window = 3600; // 1 hour
  
  if (parseInt(current) >= limit) {
    return {
      allowed: false,
      limit,
      current: parseInt(current),
      retryAfter: window,
    };
  }

  // Update counter
  await env.CHATBOT_KV?.put(rateLimitKey, (parseInt(current) + 1).toString(), { 
    expirationTtl: window 
  });

  return {
    allowed: true,
    limit,
    current: parseInt(current) + 1,
    remaining: limit - (parseInt(current) + 1),
    resetTime: Date.now() + (window * 1000),
  };
}

/**
 * Analytics Event Logging
 */
async function logAnalyticsEvent(env, data) {
  // Cloudflare Analytics
  console.log('Analytics Event:', JSON.stringify(data));
  
  // Optional: Send to external analytics
  if (env.ANALYTICS_WEBHOOK) {
    try {
      await fetch(env.ANALYTICS_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error('Analytics webhook error:', error);
    }
  }
}

/**
 * Error Logging
 */
async function logError(env, data) {
  console.error('API Error:', JSON.stringify(data));
  
  // Optional: Send to error tracking service
  if (env.ERROR_WEBHOOK) {
    try {
      await fetch(env.ERROR_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error('Error webhook error:', error);
    }
  }
}

/**
 * Rate Limit Hit Logging
 */
async function logRateLimitHit(env, data) {
  console.warn('Rate Limit Hit:', JSON.stringify(data));
}

/**
 * Backend Error Logging
 */
async function logBackendError(env, data) {
  console.error('Backend Error:', JSON.stringify(data));
}

/**
 * Success Metrics Logging
 */
async function logSuccessMetrics(env, data) {
  console.log('Success Metrics:', JSON.stringify(data));
}

/**
 * Chat Error Logging
 */
async function logChatError(env, data) {
  console.error('Chat Error:', JSON.stringify(data));
}

/**
 * Get Metrics for Dashboard
 */
async function getMetrics(env) {
  // Hier könntest du Metriken aus KV Store oder externen Services sammeln
  return {
    timestamp: new Date().toISOString(),
    requests: {
      total: 0, // Würde aus KV Store kommen
      successful: 0,
      errors: 0,
      rate_limited: 0,
    },
    performance: {
      avg_response_time: 0,
      p95_response_time: 0,
      p99_response_time: 0,
    },
    regions: {
      // Würde aus Analytics kommen
    },
  };
}

/**
 * Generate Request ID
 */
function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
