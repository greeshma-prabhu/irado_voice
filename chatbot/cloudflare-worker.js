/**
 * Cloudflare Worker für Irado Chatbot API
 * Optimiert für Cloudflare Edge Computing
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS Headers für alle Anfragen
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
      'Access-Control-Max-Age': '86400',
    };

    // Handle CORS Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: corsHeaders,
      });
    }

    // Route handling
    if (url.pathname === '/api/chat') {
      return handleChatRequest(request, env, corsHeaders);
    }
    
    if (url.pathname === '/api/health') {
      return handleHealthCheck(request, corsHeaders);
    }

    // 404 für unbekannte Routen
    return new Response(JSON.stringify({ error: 'Not Found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  },
};

/**
 * Chatbot API Handler
 */
async function handleChatRequest(request, env, corsHeaders) {
  try {
    // Nur POST-Anfragen erlauben
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Request Body validieren
    const body = await request.json();
    if (!body.sessionId || !body.action || !body.chatInput) {
      return new Response(JSON.stringify({ 
        error: 'Invalid request format',
        code: 'INVALID_REQUEST'
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    // Forward zu Backend-Service
    const backendUrl = env.BACKEND_URL || 'http://localhost:5000/webhook/chat';
    const backendRequest = new Request(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Basic ${btoa('irado:20Irado25!')}`,
      },
      body: JSON.stringify(body),
    });

    const backendResponse = await fetch(backendRequest);
    const responseData = await backendResponse.json();

    // Response mit Cloudflare-Metadaten
    const response = {
      ...responseData,
      metadata: {
        processing_time: Date.now() - request.cf.timestamp,
        cloudflare: {
          region: request.cf.colo,
          datacenter: request.cf.datacenter,
          cache_status: 'MISS', // Für dynamische Inhalte
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
 * Health Check Handler
 */
async function handleHealthCheck(request, corsHeaders) {
  const healthData = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    cloudflare: {
      region: request.cf.colo,
      datacenter: request.cf.datacenter,
      country: request.cf.country,
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
