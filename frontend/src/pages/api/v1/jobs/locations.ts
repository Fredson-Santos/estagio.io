import type { APIRoute } from 'astro';
import { getBackendUrl } from '../../../../lib/api';

/**
 * Proxy route: GET /api/v1/jobs/locations
 * Encaminha a requisição do browser para o backend, evitando CORS.
 * Parâmetros suportados: q (string), limit (number)
 */
export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const q = url.searchParams.get('q') ?? '';
  const limit = url.searchParams.get('limit') ?? '8';

  const backendUrl = getBackendUrl();
  const backendPath = `${backendUrl}/api/v1/jobs/locations?q=${encodeURIComponent(q)}&limit=${encodeURIComponent(limit)}`;

  try {
    const res = await fetch(backendPath, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(5000),
    });

    if (!res.ok) {
      return new Response(JSON.stringify([]), {
        status: res.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const data = await res.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch {
    return new Response(JSON.stringify([]), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
