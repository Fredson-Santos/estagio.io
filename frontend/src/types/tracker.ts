// ---------- Types ----------
export interface Etapa {
  id: string;
  titulo: string;
  feita: boolean;
}

export type Modalidade = "Remoto" | "Presencial" | "Híbrido";

export interface Card {
  id: string;
  cargo: string;
  empresa: string;
  local?: string;
  modalidade?: Modalidade;
  status: string;
  link: string;
  updatedAt: string;
  prazo?: string;
  notas: string;
  etapas: Etapa[];
}

export interface ColunaConfig {
  id: string;
  label: string;
  hint: string;
  dot: string;
  header: string;
  headerBorder: string;
  badge: string;
  cardBorder: string;
  dropActive: string;
}

export interface TrackerStats {
  total: number;
  emAndamento: number;
  entrevistas: number;
  taxaResposta: number;
}

/** Dados necessários para criar uma nova candidatura. */
export type NewCardData = Omit<Card, "id" | "status" | "updatedAt" | "notas" | "etapas">;

// ---------- Constants ----------
export const STORAGE_KEY = "estagio_tracker_cards";

/** Mapa de cor real da borda esquerda por coluna (para Tailwind v4 que não gera classes dinâmicas de border-l-color customizada) */
export const CARD_BORDER_LEFT: Record<string, string> = {
  salvo: "#c1c6d7",
  enviado: "#0058c3",
  entrevista: "#f59e0b",
  oferta: "#10b981",
  recusado: "#ba1a1a",
};

export const COLUNAS: ColunaConfig[] = [
  {
    id: "salvo",
    label: "Salvo",
    hint: "Quer se candidatar",
    dot: "bg-outline-variant",
    header: "bg-surface-container-low dark:bg-slate-800/60",
    headerBorder: "border-outline-variant/30 dark:border-slate-700/60",
    badge: "bg-surface-container text-on-surface-variant dark:bg-slate-800 dark:text-slate-300",
    cardBorder: "",
    dropActive: "border-outline bg-surface-container-low dark:bg-slate-800/40",
  },
  {
    id: "enviado",
    label: "Enviado",
    hint: "Aguardando retorno",
    dot: "bg-primary",
    header: "bg-primary/5 dark:bg-primary/10",
    headerBorder: "border-primary/25 dark:border-primary/20",
    badge: "bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-fixed-dim",
    cardBorder: "",
    dropActive: "border-primary bg-primary/5 dark:bg-primary/10",
  },
  {
    id: "entrevista",
    label: "Entrevista",
    hint: "Em processo",
    dot: "bg-amber-500",
    header: "bg-amber-500/5 dark:bg-amber-500/10",
    headerBorder: "border-amber-500/25 dark:border-amber-500/20",
    badge: "bg-amber-500/10 text-amber-700 dark:text-amber-300 dark:bg-amber-500/20",
    cardBorder: "",
    dropActive: "border-amber-400 bg-amber-500/10 dark:bg-amber-500/15",
  },
  {
    id: "oferta",
    label: "Oferta",
    hint: "Proposta recebida",
    dot: "bg-emerald-500",
    header: "bg-emerald-500/5 dark:bg-emerald-500/10",
    headerBorder: "border-emerald-500/25 dark:border-emerald-500/20",
    badge: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 dark:bg-emerald-500/20",
    cardBorder: "",
    dropActive: "border-emerald-400 bg-emerald-500/10 dark:bg-emerald-500/15",
  },
  {
    id: "recusado",
    label: "Recusado",
    hint: "Não seguiu",
    dot: "bg-red-500",
    header: "bg-red-500/5 dark:bg-red-500/10",
    headerBorder: "border-red-500/25 dark:border-red-500/20",
    badge: "bg-red-500/10 text-red-700 dark:text-red-300 dark:bg-red-500/20",
    cardBorder: "",
    dropActive: "border-red-400 bg-red-500/10 dark:bg-red-500/15",
  },
];

export const MODALIDADE_STYLE: Record<string, string> = {
  Remoto: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800/60",
  Presencial: "bg-surface-container text-on-surface-variant border-outline-variant/40 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
  Híbrido: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800/60",
};

export const SUGESTOES_ETAPAS = [
  "Teste lógico",
  "Teste técnico",
  "Dinâmica em grupo",
  "Entrevista RH",
  "Entrevista técnica",
  "Entrevista com gestor",
  "Case/desafio",
  "Proposta enviada",
];

// ---------- Utilities ----------
export function daysAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000);
  if (diff <= 0) return "hoje";
  if (diff === 1) return "1 dia atrás";
  return `${diff} dias atrás`;
}

export function statusDateLabel(status: string, dateStr: string): string {
  const ago = daysAgo(dateStr);
  const prefixMap: Record<string, string> = {
    salvo: "Salvo",
    enviado: "Enviado",
    entrevista: "Entrevista",
    oferta: "Oferta",
    recusado: "Recusado",
  };
  const prefix = prefixMap[status] || "Atualizado";
  return `${prefix} ${ago}`;
}

export function formatPrazo(prazo?: string): string | null {
  if (!prazo) return null;
  const target = new Date(prazo).getTime();
  if (isNaN(target)) return null;
  const diffDays = Math.ceil((target - Date.now()) / 86400000);
  if (diffDays > 1) return `${diffDays} dias p/ prazo`;
  if (diffDays === 1) return "1 dia p/ prazo";
  if (diffDays === 0) return "Prazo hoje";
  return "Prazo expirado";
}

export function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}
