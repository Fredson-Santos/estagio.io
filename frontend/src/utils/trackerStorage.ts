import type { Card, Modalidade } from "../types/tracker";
import { STORAGE_KEY } from "../types/tracker";

export interface SaveJobInput {
  cargo: string;
  empresa: string;
  local?: string;
  modalidade?: string;
  link?: string;
}

export interface SaveJobResult {
  success: boolean;
  alreadySaved: boolean;
  cards: Card[];
}

/**
 * Carrega cards do localStorage com tratamento seguro para SSR,
 * dados corrompidos e localStorage indisponível.
 */
export function loadCards(): Card[] {
  try {
    if (typeof window === "undefined") return [];
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch {
    // localStorage unavailable or corrupted data
  }
  return [];
}

/**
 * Verifica se uma vaga já está salva na lista de cards.
 */
export function isJobSaved(
  cards: Card[],
  job: { cargo: string; empresa: string; link?: string }
): boolean {
  if (!job.cargo || !job.empresa) return false;
  const targetCargo = job.cargo.trim().toLowerCase();
  const targetEmpresa = job.empresa.trim().toLowerCase();
  const targetLink = job.link?.trim();

  return cards.some((c) => {
    const cargoMatch = c.cargo?.trim().toLowerCase() === targetCargo;
    const empresaMatch = c.empresa?.trim().toLowerCase() === targetEmpresa;
    if (cargoMatch && empresaMatch) return true;
    if (targetLink && c.link?.trim() && c.link.trim() === targetLink) return true;
    return false;
  });
}

/**
 * Normaliza a modalidade para o tipo padrão do tracker.
 */
export function normalizeModalidade(modalityStr?: string): Modalidade | undefined {
  if (!modalityStr) return undefined;
  const m = modalityStr.trim().toLowerCase();
  if (m.includes("remoto") || m.includes("remote")) return "Remoto";
  if (m.includes("híbrido") || m.includes("hibrido") || m.includes("hybrid")) return "Híbrido";
  if (m.includes("presencial") || m.includes("on-site") || m.includes("onsite")) return "Presencial";
  return undefined;
}

/**
 * Salva uma vaga no localStorage do Tracker.
 */
export function saveJobToStorage(job: SaveJobInput): SaveJobResult {
  const cards = loadCards();
  if (isJobSaved(cards, job)) {
    return { success: true, alreadySaved: true, cards };
  }

  const newCard: Card = {
    id: String(Date.now()),
    cargo: job.cargo.trim(),
    empresa: job.empresa.trim(),
    local: job.local?.trim() || undefined,
    modalidade: normalizeModalidade(job.modalidade),
    status: "salvo",
    link: job.link?.trim() || (typeof window !== "undefined" ? window.location.href : ""),
    updatedAt: new Date().toISOString().slice(0, 10),
    notas: "",
    etapas: [],
  };

  const updatedCards = [newCard, ...cards];
  try {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedCards));
    }
  } catch (e) {
    console.error("Falha ao salvar vaga no localStorage", e);
    return { success: false, alreadySaved: false, cards };
  }

  return { success: true, alreadySaved: false, cards: updatedCards };
}
