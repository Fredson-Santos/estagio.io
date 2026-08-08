import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import UmamiAnalytics from './UmamiAnalytics.astro';

describe('UmamiAnalytics Component', () => {
  it('renders umami script tag when websiteId and scriptUrl are present', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(UmamiAnalytics, {
      props: {
        websiteId: '4e1126d9-318f-4904-affc-191de8567099',
        scriptUrl: 'https://umami.conekta.tech/script.js',
      },
    });

    expect(html).toContain('https://umami.conekta.tech/script.js');
    expect(html).toContain('data-website-id="4e1126d9-318f-4904-affc-191de8567099"');
    expect(html).toContain('defer');
  });

  it('renders data-domains attribute when domains prop is provided', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(UmamiAnalytics, {
      props: {
        websiteId: '4e1126d9-318f-4904-affc-191de8567099',
        scriptUrl: 'https://umami.conekta.tech/script.js',
        domains: 'estagio.io',
      },
    });

    expect(html).toContain('data-domains="estagio.io"');
  });

  it('does not render script tag if websiteId is empty', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(UmamiAnalytics, {
      props: {
        websiteId: '',
        scriptUrl: '',
      },
    });

    expect(html).not.toContain('<script');
  });
});
