import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import Sobre from './sobre.astro';

describe('Sobre Page', () => {
  it('renders updated Hero section content', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Sobre);

    expect(html).toContain('Chega de abrir 15 abas atrás de estágio.');
    expect(html).toContain('O estagio.io monitora os principais portais de carreira do Brasil');
  });

  it('renders "O problema" section', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Sobre);

    expect(html).toContain('Por que existimos');
    expect(html).toContain('Boas vagas somem rápido — e você não pode ficar em 10 sites por dia');
    expect(html).toContain('Toda semana surgem centenas de vagas de estágio espalhadas em diversas plataformas de carreira.');
    expect(html).not.toContain('Gupy');
    expect(html).not.toContain('CIEE');
    expect(html).not.toContain('Vagas.com');
    expect(html).not.toContain('LinkedIn');
  });

  it('renders "Nossa Missão" section with updated metrics', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Sobre);

    expect(html).toContain('Nossa Missão');
    expect(html).toContain('Todas as vagas em um só lugar');
    expect(html).toContain('10.000+');
    expect(html).toContain('Vagas Agregadas');
    expect(html).toContain('15+');
    expect(html).toContain('Plataformas Monitoradas');
    expect(html).not.toContain('Empresas Parceiras');
    expect(html).toContain('100%');
    expect(html).toContain('Gratuito para Alunos');
  });

  it('renders "Como funcionamos" and CTA section', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Sobre);

    expect(html).toContain('Como funcionamos?');
    expect(html).toContain('Plataformas de Carreira');
    expect(html).toContain('Portais de Estágio');
    expect(html).toContain('Redes Profissionais');
    expect(html).toContain('Pronto para dar o próximo passo?');
    expect(html).toContain('Ver vagas disponíveis');
    expect(html).toContain('href="/vagas"');
  });
});
