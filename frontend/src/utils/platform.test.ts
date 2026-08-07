import { describe, it, expect } from 'vitest';
import { getPlatformName } from './platform';

describe('getPlatformName', () => {
  it('identifies Gupy platform correctly', () => {
    expect(getPlatformName('https://company.gupy.io/job/123')).toBe('Gupy');
    expect(getPlatformName(undefined, 'Gupy')).toBe('Gupy');
  });

  it('identifies Eureca platform correctly', () => {
    expect(getPlatformName('https://app.eureca.me/vagas/123')).toBe('Eureca');
    expect(getPlatformName('https://oportunidades.eureca.me/123')).toBe('Eureca');
    expect(getPlatformName(undefined, 'Eureca')).toBe('Eureca');
  });

  it('identifies Vagas.com correctly', () => {
    expect(getPlatformName('https://www.vagas.com.br/vagas/123')).toBe('Vagas.com');
  });

  it('identifies Cia de Estágios correctly', () => {
    expect(getPlatformName('https://app.ciadeestagios.com.br/vaga/123')).toBe('Cia de Estágios');
    expect(getPlatformName('https://ciadeestagios.com.br/vaga/123')).toBe('Cia de Estágios');
    expect(getPlatformName(undefined, 'Cia de Estagios')).toBe('Cia de Estágios');
  });

  it('falls back gracefully to generic hostname or default', () => {
    expect(getPlatformName('https://customjobboard.com/vaga')).toBe('Customjobboard.com');
    expect(getPlatformName(undefined, undefined)).toBe('Site Oficial');
  });
});
