import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';

describe('Favicon Component / Asset', () => {
  it('garante que o favicon.svg existe e contém a estrutura de um chapéu de formatura', () => {
    const faviconPath = path.join(process.cwd(), 'public', 'favicon.svg');
    expect(fs.existsSync(faviconPath)).toBe(true);

    const svgContent = fs.readFileSync(faviconPath, 'utf-8');
    expect(svgContent).toContain('<svg');
    expect(svgContent).toContain('viewBox="0 0 128 128"');
    // Verifica presença dos elementos visuais do chapéu de formatura (corpo, botão e tassel)
    expect(svgContent).toContain('#0058C3'); // Cor primária estagio.io
    expect(svgContent).toContain('#FFC107'); // Cor do tassel/borla do cap
  });
});
