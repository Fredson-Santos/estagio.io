import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

/**
 * Testes de configuração de segurança do Astro.
 *
 * Valida que a configuração `security.allowedDomains` está presente
 * e correta para evitar erros de CSRF (Cross-site POST form submissions
 * are forbidden) quando o site roda atrás de proxy reverso (Dokploy/Traefik).
 */
describe('astro.config.mjs – security', () => {
  const configPath = resolve(import.meta.dirname, '../../astro.config.mjs');
  const configContent = readFileSync(configPath, 'utf-8');

  it('deve manter checkOrigin habilitado', () => {
    expect(configContent).toContain('checkOrigin: true');
  });

  it('deve conter allowedDomains com o hostname estagio.io', () => {
    expect(configContent).toContain('allowedDomains');
    expect(configContent).toContain("hostname: 'estagio.io'");
  });

  it('deve especificar protocol https no allowedDomains', () => {
    expect(configContent).toContain("protocol: 'https'");
  });

  it('não deve desabilitar a proteção CSRF', () => {
    expect(configContent).not.toContain('checkOrigin: false');
  });
});
