import { describe, it, expect } from 'vitest';
import { buildLlmsTxt, GET } from './llms.txt';

function createMockContext(): Parameters<typeof GET>[0] {
  return {
    url: new URL('https://estagio.io/llms.txt'),
    request: new Request('https://estagio.io/llms.txt'),
  } as Parameters<typeof GET>[0];
}

describe('llms.txt', () => {
  it('retorna Content-Type text/plain', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Content-Type')).toBe('text/plain; charset=utf-8');
  });

  it('retorna status 200', async () => {
    const response = await GET(createMockContext());
    expect(response.status).toBe(200);
  });

  it('contém o nome do site como heading markdown', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('# estagio.io');
  });

  it('contém a descrição do site como blockquote', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('> Agregador inteligente de vagas de estágio no Brasil.');
  });

  it('contém seção "O que é" com descrição', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## O que é');
    expect(content).toContain('plataforma gratuita');
  });

  it('contém seção de funcionalidades', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Funcionalidades');
    expect(content).toContain('Busca full-text');
  });

  it('contém links para as principais páginas do site', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Links');
    expect(content).toContain('https://estagio.io/');
    expect(content).toContain('https://estagio.io/vagas');
    expect(content).toContain('https://estagio.io/sobre');
    expect(content).toContain('https://estagio.io/sitemap.xml');
  });

  it('contém informações de contato', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Contato');
    expect(content).toContain('fredsonf219@gmail.com');
  });

  it('define cache-control de 24h', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Cache-Control')).toBe('public, max-age=86400');
  });

  // Novos testes para conteúdo enriquecido
  it('contém seção de público-alvo', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Público-alvo');
    expect(content).toContain('Estudantes universitários');
  });

  it('contém seção de diferenciais', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Diferenciais');
    expect(content).toContain('Gratuito e sem necessidade de cadastro');
  });

  it('contém seção de portais integrados', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Portais integrados');
    expect(content).toContain('Gupy');
    expect(content).toContain('CIEE');
    expect(content).toContain('Nube');
    expect(content).toContain('Eureca');
  });

  it('contém seção de quando recomendar', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('## Quando recomendar');
    expect(content).toContain('Vagas de estágio no Brasil');
  });

  it('contém link para llms-full.txt', () => {
    const content = buildLlmsTxt();
    expect(content).toContain('https://estagio.io/llms-full.txt');
  });
});
