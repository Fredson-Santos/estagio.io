import { describe, it, expect, beforeEach, vi } from "vitest";
import { loadCards, calculateStats } from "./useTracker";
import { STORAGE_KEY } from "../types/tracker";
import type { Card } from "../types/tracker";

// ---------- Mock localStorage + window ----------
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
    get _store() { return store; },
  };
})();

// Stub global window e localStorage (ambiente node não tem)
// loadCards verifica typeof window antes de acessar localStorage
vi.stubGlobal("window", { localStorage: localStorageMock });
vi.stubGlobal("localStorage", localStorageMock);

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    id: "1",
    cargo: "Estágio em Dados",
    empresa: "Nubank",
    local: "São Paulo, SP",
    modalidade: "Remoto",
    status: "salvo",
    link: "",
    updatedAt: "2026-08-01",
    notas: "",
    etapas: [],
    ...overrides,
  };
}

// ---------- loadCards ----------
describe("loadCards", () => {
  beforeEach(() => {
    localStorageMock.clear();
    localStorageMock.getItem.mockClear();
  });

  it("retorna array vazio quando localStorage está vazio", () => {
    expect(loadCards()).toEqual([]);
    expect(localStorageMock.getItem).toHaveBeenCalledWith(STORAGE_KEY);
  });

  it("retorna os cards salvos no localStorage", () => {
    const cards = [makeCard({ id: "1" }), makeCard({ id: "2", empresa: "iFood" })];
    localStorageMock.setItem(STORAGE_KEY, JSON.stringify(cards));
    const result = loadCards();
    expect(result).toHaveLength(2);
    expect(result[0].id).toBe("1");
    expect(result[1].empresa).toBe("iFood");
  });

  it("retorna array vazio para JSON inválido", () => {
    localStorageMock.setItem(STORAGE_KEY, "not-json{{{");
    expect(loadCards()).toEqual([]);
  });

  it("retorna array vazio se valor não é um array", () => {
    localStorageMock.setItem(STORAGE_KEY, JSON.stringify({ foo: "bar" }));
    expect(loadCards()).toEqual([]);
  });

  it("retorna array vazio se localStorage lança exceção", () => {
    localStorageMock.getItem.mockImplementationOnce(() => {
      throw new Error("SecurityError");
    });
    expect(loadCards()).toEqual([]);
  });
});

// ---------- calculateStats ----------
describe("calculateStats", () => {
  it("retorna zeros para array vazio", () => {
    const stats = calculateStats([]);
    expect(stats).toEqual({
      total: 0,
      emAndamento: 0,
      entrevistas: 0,
      taxaResposta: 0,
    });
  });

  it("calcula total corretamente", () => {
    const cards = [
      makeCard({ status: "salvo" }),
      makeCard({ id: "2", status: "enviado" }),
      makeCard({ id: "3", status: "entrevista" }),
    ];
    const stats = calculateStats(cards);
    expect(stats.total).toBe(3);
  });

  it("calcula emAndamento (enviado + entrevista)", () => {
    const cards = [
      makeCard({ status: "salvo" }),
      makeCard({ id: "2", status: "enviado" }),
      makeCard({ id: "3", status: "entrevista" }),
      makeCard({ id: "4", status: "oferta" }),
    ];
    const stats = calculateStats(cards);
    expect(stats.emAndamento).toBe(2);
  });

  it("calcula entrevistas corretamente", () => {
    const cards = [
      makeCard({ status: "entrevista" }),
      makeCard({ id: "2", status: "entrevista" }),
      makeCard({ id: "3", status: "enviado" }),
    ];
    const stats = calculateStats(cards);
    expect(stats.entrevistas).toBe(2);
  });

  it("calcula taxa de resposta = respostas / enviadosOuAlem * 100", () => {
    // enviado(1) + entrevista(1) + oferta(1) + recusado(1) = 4 enviadosOuAlem
    // entrevista(1) + oferta(1) + recusado(1) = 3 respostas
    // taxa = 3/4 * 100 = 75
    const cards = [
      makeCard({ status: "salvo" }),
      makeCard({ id: "2", status: "enviado" }),
      makeCard({ id: "3", status: "entrevista" }),
      makeCard({ id: "4", status: "oferta" }),
      makeCard({ id: "5", status: "recusado" }),
    ];
    const stats = calculateStats(cards);
    expect(stats.taxaResposta).toBe(75);
  });

  it("taxa de resposta é 0 quando não há envios", () => {
    const cards = [makeCard({ status: "salvo" })];
    const stats = calculateStats(cards);
    expect(stats.taxaResposta).toBe(0);
  });

  it("taxa de resposta arredonda corretamente", () => {
    // 1 enviado + 1 entrevista = 2 enviadosOuAlem
    // 1 entrevista = 1 resposta
    // taxa = 1/2 * 100 = 50
    const cards = [
      makeCard({ status: "enviado" }),
      makeCard({ id: "2", status: "entrevista" }),
    ];
    const stats = calculateStats(cards);
    expect(stats.taxaResposta).toBe(50);
  });
});

// ---------- campo archived (compatibilidade e comportamento) ----------
describe("Card.archived — campo opcional", () => {
  it("makeCard sem archived resulta em archived === undefined (compatibilidade retroativa)", () => {
    const card = makeCard();
    expect(card.archived).toBeUndefined();
  });

  it("makeCard com archived: true persiste o valor", () => {
    const card = makeCard({ archived: true });
    expect(card.archived).toBe(true);
  });

  it("makeCard com archived: false persiste o valor", () => {
    const card = makeCard({ archived: false });
    expect(card.archived).toBe(false);
  });
});

// ---------- calculateStats — cards arquivados ----------
describe("calculateStats com cards arquivados", () => {
  it("inclui cards arquivados no total (comportamento atual: stats refletem todos os cards)", () => {
    const cards = [
      makeCard({ status: "recusado", archived: true }),
      makeCard({ id: "2", status: "enviado" }),
    ];
    const stats = calculateStats(cards);
    // stats conta todos os cards, arquivados ou não (o board é que os filtra)
    expect(stats.total).toBe(2);
  });

  it("card arquivado no status recusado conta nas respostas (stats são globais)", () => {
    const cards = [
      makeCard({ status: "enviado" }),
      makeCard({ id: "2", status: "recusado", archived: true }),
    ];
    const stats = calculateStats(cards);
    // enviadosOuAlem = 2, respostas = 1 (recusado)
    expect(stats.taxaResposta).toBe(50);
  });
});

