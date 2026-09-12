import type { APIRoute } from 'astro';

const SITE_URL = 'https://estagio.io';

export function buildLlmsTxt(): string {
  return [
    '# estagio.io',
    '',
    '> Agregador inteligente de vagas de estágio no Brasil.',
    '',
    '## O que é',
    '',
    'O estagio.io é uma plataforma gratuita que centraliza vagas de estágio',
    'de múltiplos portais brasileiros (Gupy, CIEE, Nube, Eureca e outros)',
    'em um único lugar, com busca por texto, filtros por modalidade (remoto,',
    'híbrido, presencial), área de atuação e localização.',
    '',
    '## Funcionalidades',
    '',
    '- Busca full-text por cargo, empresa ou palavra-chave',
    '- Filtros por modalidade, área e localização',
    '- Atualização automática 24/7 via web scraping',
    '- Deduplicação e verificação de vagas',
    '- Tracker de candidaturas com kanban visual',
    '- Dados estruturados Schema.org (JobPosting)',
    '',
    '## Links',
    '',
    `- [Página inicial](${SITE_URL}/)`,
    `- [Buscar vagas](${SITE_URL}/vagas)`,
    `- [Sobre o projeto](${SITE_URL}/sobre)`,
    `- [Sitemap](${SITE_URL}/sitemap.xml)`,
    '',
    '## Contato',
    '',
    '- Email: fredsonf219@gmail.com',
    `- GitHub: https://github.com/Fredson-Santos/estagio.io`,
    '',
  ].join('\n');
}

export const GET: APIRoute = () => {
  const body = buildLlmsTxt();

  return new Response(body, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400',
    },
  });
};
