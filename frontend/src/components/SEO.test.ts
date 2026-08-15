import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import SEO from './SEO.astro';

describe('SEO Component', () => {
  it('renderiza meta tags, titulos e links de fontes otimizados', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(SEO, {
      props: {
        title: 'Estágio.io - Vagas de Estágio',
        description: 'Encontre as melhores vagas de estágio em tecnologia.',
      },
    });

    expect(html).toContain('<title>Estágio.io - Vagas de Estágio</title>');
    expect(html).toContain('content="Encontre as melhores vagas de estágio em tecnologia."');
    expect(html).toContain('rel="preconnect" href="https://fonts.googleapis.com"');
    expect(html).toContain('rel="preconnect" href="https://fonts.gstatic.com"');
    
    // Valida que a URL da fonte inclui display=swap e eixos fixos otimizados (evita payload de 3.8MB)
    expect(html).toContain('family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');
    expect(html).not.toContain('20..48,100..700');
  });
});
