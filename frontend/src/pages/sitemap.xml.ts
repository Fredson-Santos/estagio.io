import type { APIRoute } from 'astro';
import { fetchJobs } from '../lib/api';
import type { Job } from '../lib/types';

const SITE_URL = 'https://estagio.io';

const STATIC_PAGES = [
  { path: '/', priority: '1.0', changefreq: 'daily' },
  { path: '/vagas', priority: '0.9', changefreq: 'hourly' },
  { path: '/sobre', priority: '0.5', changefreq: 'monthly' },
];

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return new Date().toISOString().split('T')[0];
  try {
    return new Date(dateStr).toISOString().split('T')[0];
  } catch {
    return new Date().toISOString().split('T')[0];
  }
}

export async function buildSitemapEntries(): Promise<string[]> {
  const today = new Date().toISOString().split('T')[0];

  const entries: string[] = STATIC_PAGES.map(
    (page) => `  <url>
    <loc>${escapeXml(SITE_URL + page.path)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`
  );

  let jobs: Job[] = [];
  try {
    const data = await fetchJobs('/jobs?limit=5000');
    jobs = data.items;
  } catch {
    // Backend offline — retorna apenas páginas estáticas
  }

  for (const job of jobs) {
    entries.push(`  <url>
    <loc>${escapeXml(`${SITE_URL}/vagas/${job.id}`)}</loc>
    <lastmod>${formatDate(job.posted_at)}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`);
  }

  return entries;
}

export const GET: APIRoute = async () => {
  const entries = await buildSitemapEntries();

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries.join('\n')}
</urlset>`;

  return new Response(xml, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
