import { describe, it, expect } from 'vitest';
import { GET } from './robots.txt';

function createMockContext(): Parameters<typeof GET>[0] {
  return {
    url: new URL('https://estagio.io/robots.txt'),
    request: new Request('https://estagio.io/robots.txt'),
  } as Parameters<typeof GET>[0];
}

describe('robots.txt', () => {
  it('retorna Content-Type text/plain', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Content-Type')).toBe('text/plain; charset=utf-8');
  });

  it('retorna status 200', async () => {
    const response = await GET(createMockContext());
    expect(response.status).toBe(200);
  });

  it('permite crawling geral com User-agent: *', async () => {
    const response = await GET(createMockContext());
    const body = await response.text();
    expect(body).toContain('User-agent: *');
    expect(body).toContain('Allow: /');
  });

  it('bloqueia rotas privadas: admin, api, tracker', async () => {
    const response = await GET(createMockContext());
    const body = await response.text();
    expect(body).toContain('Disallow: /admin/');
    expect(body).toContain('Disallow: /api/');
    expect(body).toContain('Disallow: /tracker/');
  });

  it('referencia o sitemap com URL absoluta', async () => {
    const response = await GET(createMockContext());
    const body = await response.text();
    expect(body).toContain('Sitemap: https://estagio.io/sitemap.xml');
  });

  it('define cache-control de 24h', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Cache-Control')).toBe('public, max-age=86400');
  });
});
