import { describe, it, expect } from 'vitest';
import { formatJobDescription } from './formatDescription';

describe('formatJobDescription', () => {
  it('should unescape &nbsp; and format HTML', () => {
    const raw = 'Estados Unidos.&nbsp;Na Software.com.br prezamos pelo respeito.';
    const formatted = formatJobDescription(raw);
    expect(formatted).not.toContain('&nbsp;');
    expect(formatted).toContain('Estados Unidos. Na Software.com.br');
  });

  it('should format semicolon separated lists into bullet points', () => {
    const raw = 'Responsabilidades;Atuar ativamente;Auxiliar os consultores';
    const formatted = formatJobDescription(raw);
    expect(formatted).toContain('<ul class="list-disc pl-5 my-3 space-y-1.5 text-on-surface-variant font-body-md">');
  });
});
