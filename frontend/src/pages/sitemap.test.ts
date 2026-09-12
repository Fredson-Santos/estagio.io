import { describe, it, expect, vi, beforeEach } from 'vitest';
import { buildSitemapEntries, GET } from './sitemap.xml';

vi.mock('../lib/api', () => ({
  fetchJobs: vi.fn(),
}));

import { fetchJobs } from '../lib/api';
const mockFetchJobs = vi.mocked(fetchJobs);

function createMockContext(): Parameters<typeof GET>[0] {
  return {
    url: new URL('https://estagio.io/sitemap.xml'),
    request: new Request('https://estagio.io/sitemap.xml'),
  } as Parameters<typeof GET>[0];
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe('sitemap.xml', () => {
  it('retorna Content-Type application/xml', async () => {
    mockFetchJobs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 5000 });
    const response = await GET(createMockContext());
    expect(response.headers.get('Content-Type')).toBe('application/xml; charset=utf-8');
  });

  it('retorna status 200', async () => {
    mockFetchJobs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 5000 });
    const response = await GET(createMockContext());
    expect(response.status).toBe(200);
  });

  it('inclui XML header e urlset namespace', async () => {
    mockFetchJobs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 5000 });
    const response = await GET(createMockContext());
    const body = await response.text();
    expect(body).toContain('<?xml version="1.0" encoding="UTF-8"?>');
    expect(body).toContain('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"');
  });

  it('inclui URLs estáticas: /, /vagas, /sobre', async () => {
    mockFetchJobs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 5000 });
    const entries = await buildSitemapEntries();
    const joined = entries.join('\n');
    expect(joined).toContain('https://estagio.io/');
    expect(joined).toContain('https://estagio.io/vagas');
    expect(joined).toContain('https://estagio.io/sobre');
  });

  it('inclui URLs dinâmicas de vagas quando backend retorna dados', async () => {
    mockFetchJobs.mockResolvedValue({
      items: [
        { id: 'abc-123', title: 'Dev', company: 'ACME', location: 'SP', posted_at: '2026-08-01T00:00:00Z' },
        { id: 'def-456', title: 'Design', company: 'Corp', location: 'RJ', posted_at: '2026-09-01T00:00:00Z' },
      ],
      total: 2,
      skip: 0,
      limit: 5000,
    });

    const entries = await buildSitemapEntries();
    const joined = entries.join('\n');
    expect(joined).toContain('https://estagio.io/vagas/abc-123');
    expect(joined).toContain('https://estagio.io/vagas/def-456');
    expect(joined).toContain('<lastmod>2026-08-01</lastmod>');
    expect(joined).toContain('<lastmod>2026-09-01</lastmod>');
  });

  it('retorna apenas URLs estáticas quando backend está offline (fallback)', async () => {
    mockFetchJobs.mockRejectedValue(new Error('Network error'));

    const entries = await buildSitemapEntries();
    expect(entries).toHaveLength(3); // Apenas /, /vagas, /sobre
    const joined = entries.join('\n');
    expect(joined).not.toContain('/vagas/');
  });

  it('escapa caracteres especiais em XML', async () => {
    mockFetchJobs.mockResolvedValue({
      items: [
        { id: 'test&id', title: 'Dev', company: 'A&B', location: 'SP' },
      ],
      total: 1,
      skip: 0,
      limit: 5000,
    });

    const entries = await buildSitemapEntries();
    const joined = entries.join('\n');
    expect(joined).toContain('test&amp;id');
    expect(joined).not.toContain('test&id');
  });

  it('define cache-control de 1h', async () => {
    mockFetchJobs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 5000 });
    const response = await GET(createMockContext());
    expect(response.headers.get('Cache-Control')).toBe('public, max-age=3600');
  });
});
