/**
 * Extrai e formata o nome amigável da plataforma de origem da vaga.
 */
export function getPlatformName(sourceUrl?: string | null, sourceName?: string | null): string {
  if (sourceName && sourceName.trim()) {
    const clean = sourceName.trim();
    if (clean.toLowerCase().includes('gupy')) return 'Gupy';
    if (clean.toLowerCase().includes('eureca')) return 'Eureca';
    if (clean.toLowerCase().includes('vagas.com')) return 'Vagas.com';
    if (clean.toLowerCase().includes('superestagios') || clean.toLowerCase().includes('super estágios')) return 'SuperEstágios';
    if (clean.toLowerCase().includes('ciadeestagios') || clean.toLowerCase().includes('cia de estagios') || clean.toLowerCase().includes('cia de estágios')) return 'Cia de Estágios';
    if (clean.toLowerCase().includes('ciee')) return 'CIEE';
    if (clean.toLowerCase().includes('nube')) return 'Nube';
    return clean;
  }

  if (!sourceUrl) return 'Site Oficial';

  const urlLower = sourceUrl.toLowerCase();
  if (urlLower.includes('gupy.io')) return 'Gupy';
  if (urlLower.includes('eureca.me')) return 'Eureca';
  if (urlLower.includes('vagas.com.br')) return 'Vagas.com';
  if (urlLower.includes('superestagios.com.br')) return 'SuperEstágios';
  if (urlLower.includes('ciadeestagios.com.br')) return 'Cia de Estágios';
  if (urlLower.includes('ciee.org') || urlLower.includes('ciee.')) return 'CIEE';
  if (urlLower.includes('nube.com.br')) return 'Nube';
  if (urlLower.includes('catho.com.br')) return 'Catho';
  if (urlLower.includes('infojobs.com.br')) return 'InfoJobs';
  if (urlLower.includes('linkedin.com')) return 'LinkedIn';

  try {
    const parsed = new URL(sourceUrl);
    const host = parsed.hostname.replace(/^www\./, '');
    return host.charAt(0).toUpperCase() + host.slice(1);
  } catch {
    return 'Site Oficial';
  }
}
