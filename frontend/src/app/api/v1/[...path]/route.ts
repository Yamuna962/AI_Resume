import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') ||
  'http://127.0.0.1:8000';

const BACKEND_UNAVAILABLE_MESSAGE =
  'Backend service unavailable. Start the backend server and ensure PostgreSQL is running.';

async function proxyRequest(request: NextRequest, path: string[]) {
  const segment = path.join('/');

  const needsTrailingSlash =
    path.length === 1 &&
    (path[0] === 'profile' || path[0] === 'history');

  const targetPath = needsTrailingSlash
    ? `/api/v1/${segment}/`
    : `/api/v1/${segment}`;

  const url = new URL(targetPath, BACKEND_URL);
  url.search = request.nextUrl.search;

  // Copy incoming request headers
  const headers = new Headers();

  const skipHeaders = new Set([
    'host',
    'connection',
    'expect',
    'content-length',
    'transfer-encoding',
  ]);

  request.headers.forEach((value, key) => {
    if (!skipHeaders.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  const init: RequestInit = {
    method: request.method,
    headers,
    redirect: 'manual',
  };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  try {
    const backendRes = await fetch(url.toString(), init);

    // Read response body
    const body = await backendRes.text();

    // Only forward safe headers
    const responseHeaders = new Headers();

    const contentType = backendRes.headers.get('content-type');
    if (contentType) {
      responseHeaders.set('content-type', contentType);
    }

    const cacheControl = backendRes.headers.get('cache-control');
    if (cacheControl) {
      responseHeaders.set('cache-control', cacheControl);
    }

    return new NextResponse(body, {
      status: backendRes.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('========== PROXY ERROR ==========');
    console.error('Backend URL:', BACKEND_URL);
    console.error(error);
    console.error('=================================');

    return NextResponse.json(
      {
        success: false,
        error: BACKEND_UNAVAILABLE_MESSAGE,
        detail:
          error instanceof Error
            ? error.message
            : 'Unknown proxy error',
      },
      {
        status: 503,
      }
    );
  }
}

type RouteContext = {
  params: Promise<{
    path: string[];
  }>;
};

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  context: RouteContext
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  context: RouteContext
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}