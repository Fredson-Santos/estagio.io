import { useState, useMemo, useEffect, useCallback } from "react";
import type { Card, TrackerStats, NewCardData } from "../types/tracker";
import { STORAGE_KEY } from "../types/tracker";

import { loadCards } from "../utils/trackerStorage";
export { loadCards };

/** Calcula estatísticas do tracker a partir da lista de cards. */
export function calculateStats(cards: Card[]): TrackerStats {
  const total = cards.length;
  const emAndamento = cards.filter((c) =>
    ["enviado", "entrevista"].includes(c.status)
  ).length;
  const entrevistas = cards.filter((c) => c.status === "entrevista").length;
  const enviadosOuAlem = cards.filter((c) =>
    ["enviado", "entrevista", "oferta", "recusado"].includes(c.status)
  ).length;
  const respostas = cards.filter((c) =>
    ["entrevista", "oferta", "recusado"].includes(c.status)
  ).length;
  const taxaResposta =
    enviadosOuAlem === 0 ? 0 : Math.round((respostas / enviadosOuAlem) * 100);
  return { total, emAndamento, entrevistas, taxaResposta };
}

/**
 * Hook de state management do Tracker de Candidaturas.
 * Persiste dados automaticamente no localStorage após montagem no cliente.
 */
export function useTracker() {
  const [cards, setCards] = useState<Card[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [query, setQuery] = useState("");
  const [dragId, setDragId] = useState<string | null>(null);
  const [dragOverCol, setDragOverCol] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [mobileFilter, setMobileFilter] = useState("todos");

  // Carrega do localStorage no cliente
  useEffect(() => {
    const loaded = loadCards();
    setCards(loaded);
    setIsLoaded(true);
  }, []);

  // Persiste no localStorage apenas após o carregamento inicial
  useEffect(() => {
    if (!isLoaded) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cards));
    } catch {
      // localStorage full or unavailable
    }
  }, [cards, isLoaded]);

  const filtered = useMemo(() => {
    if (!query.trim()) return cards;
    const q = query.toLowerCase();
    return cards.filter(
      (c) =>
        c.cargo.toLowerCase().includes(q) || c.empresa.toLowerCase().includes(q)
    );
  }, [cards, query]);

  const byStatus = useCallback(
    (status: string) => filtered.filter((c) => c.status === status),
    [filtered]
  );

  const stats: TrackerStats = useMemo(() => calculateStats(cards), [cards]);

  function moveCard(id: string, status: string) {
    setCards((prev) =>
      prev.map((c) =>
        c.id === id
          ? { ...c, status, updatedAt: new Date().toISOString().slice(0, 10) }
          : c
      )
    );
  }

  function deleteCard(id: string) {
    setCards((prev) => prev.filter((c) => c.id !== id));
    setDetailId(null);
  }

  function addCard(data: NewCardData) {
    setCards((prev) => [
      {
        id: String(Date.now()),
        status: "salvo",
        updatedAt: new Date().toISOString().slice(0, 10),
        notas: "",
        etapas: [],
        ...data,
      },
      ...prev,
    ]);
    setModalOpen(false);
  }

  function addEtapa(cardId: string, titulo: string) {
    if (!titulo.trim()) return;
    setCards((prev) =>
      prev.map((c) =>
        c.id === cardId
          ? {
              ...c,
              etapas: [
                ...c.etapas,
                { id: String(Date.now()), titulo: titulo.trim(), feita: false },
              ],
            }
          : c
      )
    );
  }

  function toggleEtapa(cardId: string, etapaId: string) {
    setCards((prev) =>
      prev.map((c) =>
        c.id === cardId
          ? {
              ...c,
              etapas: c.etapas.map((e) =>
                e.id === etapaId ? { ...e, feita: !e.feita } : e
              ),
            }
          : c
      )
    );
  }

  function removeEtapa(cardId: string, etapaId: string) {
    setCards((prev) =>
      prev.map((c) =>
        c.id === cardId
          ? { ...c, etapas: c.etapas.filter((e) => e.id !== etapaId) }
          : c
      )
    );
  }

  const detailCard = cards.find((c) => c.id === detailId) || null;

  // Drag handlers
  function onDragStart(id: string) {
    setDragId(id);
  }

  function onDragEnd() {
    setDragId(null);
  }

  function onDragOverCol(colId: string) {
    setDragOverCol(colId);
  }

  function onDragLeaveCol(colId: string) {
    setDragOverCol((c) => (c === colId ? null : c));
  }

  function onDropCol(colId: string) {
    if (dragId) moveCard(dragId, colId);
    setDragId(null);
    setDragOverCol(null);
  }

  return {
    // State
    cards,
    isLoaded,
    query,
    setQuery,
    dragId,
    dragOverCol,
    modalOpen,
    setModalOpen,
    detailId,
    setDetailId,
    mobileFilter,
    setMobileFilter,

    // Computed
    filtered,
    byStatus,
    stats,
    detailCard,

    // Actions
    moveCard,
    deleteCard,
    addCard,
    addEtapa,
    toggleEtapa,
    removeEtapa,

    // Drag
    onDragStart,
    onDragEnd,
    onDragOverCol,
    onDragLeaveCol,
    onDropCol,
  };
}
