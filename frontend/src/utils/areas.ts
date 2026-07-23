export const AREA_LABELS: Record<string, string> = {
  TI_SOFTWARE: 'TI & Software',
  DADOS: 'Dados',
  DESIGN: 'Design & UX',
  MARKETING: 'Marketing',
  NEGOCIOS: 'Vendas & Negócios',
  RH: 'RH',
  FINANCAS: 'Finanças',
  ENGENHARIA_OUTRAS: 'Engenharia',
  DIREITO: 'Direito',
  OUTROS: 'Outros',
};

export interface AreaOption {
  value: string;
  label: string;
}

export const AREA_OPTIONS: AreaOption[] = [
  { value: 'TI_SOFTWARE', label: AREA_LABELS.TI_SOFTWARE },
  { value: 'DADOS', label: AREA_LABELS.DADOS },
  { value: 'DESIGN', label: AREA_LABELS.DESIGN },
  { value: 'MARKETING', label: AREA_LABELS.MARKETING },
  { value: 'NEGOCIOS', label: AREA_LABELS.NEGOCIOS },
  { value: 'RH', label: AREA_LABELS.RH },
  { value: 'FINANCAS', label: AREA_LABELS.FINANCAS },
  { value: 'DIREITO', label: AREA_LABELS.DIREITO },
  { value: 'ENGENHARIA_OUTRAS', label: AREA_LABELS.ENGENHARIA_OUTRAS },
  { value: 'OUTROS', label: AREA_LABELS.OUTROS },
];

export function getAreaLabel(area?: string | null): string {
  if (!area) return 'Outros';
  return AREA_LABELS[area] || area;
}
