/**
 * Cloudflare Pages Function für Irado Chatbot API
 * Für die Verwendung mit Cloudflare Pages Functions
 */

export async function onRequest(context) {
  const { request, env } = context;
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

  // API Routes
  if (url.pathname === '/api/chat') {
    return handleChatAPI(request, env, corsHeaders);
  }

  if (url.pathname === '/api/health') {
    return handleHealthAPI(request, corsHeaders);
  }

  return new Response(JSON.stringify({ error: 'Not Found' }), {
    status: 404,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}

/**
 * Chat API Handler für Pages Functions
 */
async function handleChatAPI(request, env, corsHeaders) {
  try {
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const body = await request.json();
    
    // Validierung
    if (!body.sessionId || !body.action || !body.chatInput) {
      return new Response(JSON.stringify({ 
        error: 'Invalid request format',
        code: 'INVALID_REQUEST'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Rate Limiting (optional)
    const rateLimitKey = `rate_limit_${body.sessionId}`;
    const rateLimit = await env.CHATBOT_KV?.get(rateLimitKey);
    if (rateLimit && parseInt(rateLimit) > 10) {
      return new Response(JSON.stringify({ 
        error: 'Rate limit exceeded',
        code: 'RATE_LIMIT'
      }), {
        status: 429,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Backend API Call
    const backendUrl = env.BACKEND_URL || 'http://localhost:5000/webhook/chat';
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Basic ${btoa('irado:20Irado25!')}`,
      },
      body: JSON.stringify(body),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend error: ${backendResponse.status}`);
    }

    const responseData = await backendResponse.json();

    // Rate Limiting Update
    if (env.CHATBOT_KV) {
      await env.CHATBOT_KV.put(rateLimitKey, '1', { expirationTtl: 3600 });
    }

    // Response mit Cloudflare-Metadaten
    const response = {
      ...responseData,
      metadata: {
        processing_time: Date.now(),
        cloudflare: {
          region: request.cf?.colo || 'unknown',
          datacenter: request.cf?.datacenter || 'unknown',
        },
      },
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
      },
    });

  } catch (error) {
    console.error('Chatbot API Error:', error);
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      code: 'INTERNAL_ERROR'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * Health Check für Pages Functions
 */
async function handleHealthAPI(request, corsHeaders) {
  const healthData = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    cloudflare: {
      region: request.cf?.colo || 'unknown',
      datacenter: request.cf?.datacenter || 'unknown',
      country: request.cf?.country || 'unknown',
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
