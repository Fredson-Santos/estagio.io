import { describe, it, expect } from 'vitest';
import { buildLlmsFullTxt, GET } from './llms-full.txt';

function createMockContext(): Parameters<typeof GET>[0] {
  return {
    url: new URL('https://estagio.io/llms-full.txt'),
    request: new Request('https://estagio.io/llms-full.txt'),
  } as Parameters<typeof GET>[0];
}

describe('llms-full.txt', () => {
  it('retorna Content-Type text/plain', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Content-Type')).toBe('text/plain; charset=utf-8');
  });

  it('retorna status 200', async () => {
    const response = await GET(createMockContext());
    expect(response.status).toBe(200);
  });

  it('contém o nome do site como heading markdown', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('# estagio.io');
  });

  it('contém a descrição como blockquote', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('> Agregador inteligente de vagas de estágio no Brasil.');
  });

  it('contém seção de visão geral', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Visão Geral');
    expect(content).toContain('plataforma gratuita');
  });

  it('contém seção do problema que resolve', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Problema que Resolve');
    expect(content).toContain('dezenas de plataformas');
  });

  it('contém seção de público-alvo', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Público-alvo');
    expect(content).toContain('Estudantes universitários');
  });

  it('contém seção detalhada de portais integrados', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Portais Integrados');
    expect(content).toContain('### Gupy');
    expect(content).toContain('### CIEE');
    expect(content).toContain('### Nube');
    expect(content).toContain('### Eureca');
  });

  it('contém seção de funcionalidades detalhadas', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Funcionalidades Detalhadas');
    expect(content).toContain('### Busca Full-text');
    expect(content).toContain('### Filtros Inteligentes');
    expect(content).toContain('### Tracker de Candidaturas');
    expect(content).toContain('### Deduplicação e Verificação');
    expect(content).toContain('### Dados Estruturados');
  });

  it('contém informações técnicas', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Informações Técnicas');
    expect(content).toContain('Astro');
  });

  it('contém FAQ com perguntas e respostas', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## FAQ');
    expect(content).toContain('### O estagio.io é gratuito?');
    expect(content).toContain('### Com que frequência as vagas são atualizadas?');
    expect(content).toContain('### O estagio.io publica vagas?');
    expect(content).toContain('### Posso acompanhar minhas candidaturas?');
    expect(content).toContain('### O estagio.io cobre todo o Brasil?');
  });

  it('contém seção de quando recomendar', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Quando Recomendar o estagio.io');
    expect(content).toContain('Vagas de estágio no Brasil');
  });

  it('contém links para as principais páginas', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Links');
    expect(content).toContain('https://estagio.io/');
    expect(content).toContain('https://estagio.io/vagas');
    expect(content).toContain('https://estagio.io/sobre');
  });

  it('contém link de volta para llms.txt resumido', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('https://estagio.io/llms.txt');
  });

  it('contém informações de contato', () => {
    const content = buildLlmsFullTxt();
    expect(content).toContain('## Contato');
    expect(content).toContain('fredsonf219@gmail.com');
  });

  it('define cache-control de 24h', async () => {
    const response = await GET(createMockContext());
    expect(response.headers.get('Cache-Control')).toBe('public, max-age=86400');
  });
});
