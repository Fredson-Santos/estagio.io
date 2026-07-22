export const MODALITY_LABELS: Record<string, string> = {
  REMOTE: 'Remoto',
  REMOTO: 'Remoto',
  HYBRID: 'Híbrido',
  HIBRIDO: 'Híbrido',
  ONSITE: 'Presencial',
  ON_SITE: 'Presencial',
  'ON-SITE': 'Presencial',
  IN_PERSON: 'Presencial',
  PRESENCIAL: 'Presencial',
};

export function formatModality(rawModality?: string | null): string {
  if (!rawModality) return 'Presencial';
  const normalized = String(rawModality).trim().toUpperCase().replace('-', '_');
  return MODALITY_LABELS[normalized] || 'Presencial';
}
