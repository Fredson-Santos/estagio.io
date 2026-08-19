import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';

describe('Favicon Component / Asset', () => {
  it('garante que o favicon.svg existe e contém a estrutura do logo estagio.io com dark mode', () => {
    const faviconPath = path.join(process.cwd(), 'public', 'favicon.svg');
    expect(fs.existsSync(faviconPath)).toBe(true);

    const svgContent = fs.readFileSync(faviconPath, 'utf-8');
    expect(svgContent).toContain('<svg');
    expect(svgContent).toContain('viewBox="0 0 32 32"');
    // Verifica suporte a dark mode via CSS media query
    expect(svgContent).toContain('prefers-color-scheme: dark');
    // Verifica presença das classes CSS para troca de tema
    expect(svgContent).toContain('.bg');
    expect(svgContent).toContain('.fg');
    // Verifica cores do modo claro (preto no branco)
    expect(svgContent).toContain('fill: black');
    expect(svgContent).toContain('fill: white');
    // Verifica cores do modo escuro (branco no escuro)
    expect(svgContent).toContain('fill: #F5F5F5');
    expect(svgContent).toContain('fill: #1F1F24');
  });
});
