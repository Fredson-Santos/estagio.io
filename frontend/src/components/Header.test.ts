import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import Header from './Header.astro';

describe('Header Component', () => {
  it('renders brand logo and navigation links correctly', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Header);

    expect(html).toContain('estagio.io');
    expect(html).toContain('href="/"');
    expect(html).toContain('href="/vagas"');
    expect(html).toContain('href="/sobre"');
    expect(html).toContain('id="mobile-menu-btn"');
    expect(html).toContain('id="theme-toggle-btn"');
    expect(html).toContain('id="mobile-menu"');
  });
});
