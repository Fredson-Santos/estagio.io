import { describe, it, expect } from 'vitest';
import { formatModality } from './modality';

describe('formatModality', () => {
  it('should format ONSITE and variations to Presencial', () => {
    expect(formatModality('ONSITE')).toBe('Presencial');
    expect(formatModality('onsite')).toBe('Presencial');
    expect(formatModality('on-site')).toBe('Presencial');
    expect(formatModality('ON_SITE')).toBe('Presencial');
    expect(formatModality('in-person')).toBe('Presencial');
  });

  it('should format REMOTE and variations to Remoto', () => {
    expect(formatModality('REMOTE')).toBe('Remoto');
    expect(formatModality('remote')).toBe('Remoto');
    expect(formatModality('remoto')).toBe('Remoto');
  });

  it('should format HYBRID and variations to Híbrido', () => {
    expect(formatModality('HYBRID')).toBe('Híbrido');
    expect(formatModality('hybrid')).toBe('Híbrido');
    expect(formatModality('hibrido')).toBe('Híbrido');
  });

  it('should fallback to Presencial when null or unknown', () => {
    expect(formatModality(null)).toBe('Presencial');
    expect(formatModality(undefined)).toBe('Presencial');
    expect(formatModality('unknown_value')).toBe('Presencial');
  });
});
