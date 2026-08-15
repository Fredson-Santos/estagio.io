import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  loadCards,
  isJobSaved,
  normalizeModalidade,
  saveJobToStorage,
} from "./trackerStorage";
import { STORAGE_KEY } from "../types/tracker";
import type { Card } from "../types/tracker";

// Mock localStorage + window
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    get _store() {
      return store;
    },
  };
})();

vi.stubGlobal("window", { localStorage: localStorageMock, location: { href: "https://estagio.io/vagas/123" } });
vi.stubGlobal("localStorage", localStorageMock);

function makeCard(overrides: Partial<Card> = {}): Card {
  return {
    id: "1",
    cargo: "Estágio em Engenharia de Software",
    empresa: "Nubank",
    local: "São Paulo, SP",
    modalidade: "Remoto",
    status: "salvo",
    link: "https://exemplo.com/vaga/1",
    updatedAt: "2026-08-01",
    notas: "",
    etapas: [],
    ...overrides,
  };
}

describe("trackerStorage", () => {
  beforeEach(() => {
    localStorageMock.clear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
  });

  describe("loadCards", () => {
    it("retorna array vazio quando localStorage está vazio", () => {
      expect(loadCards()).toEqual([]);
      expect(localStorageMock.getItem).toHaveBeenCalledWith(STORAGE_KEY);
    });

    it("retorna cards parseados corretamente", () => {
      const cards = [makeCard({ id: "1" }), makeCard({ id: "2", empresa: "Google" })];
      localStorageMock.setItem(STORAGE_KEY, JSON.stringify(cards));

      const result = loadCards();
      expect(result).toHaveLength(2);
      expect(result[0].id).toBe("1");
      expect(result[1].empresa).toBe("Google");
    });

    it("trata erros de JSON inválido ou formato inesperado", () => {
      localStorageMock.setItem(STORAGE_KEY, "invalid-json");
      expect(loadCards()).toEqual([]);

      localStorageMock.setItem(STORAGE_KEY, JSON.stringify({ not: "an array" }));
      expect(loadCards()).toEqual([]);
    });
  });

  describe("isJobSaved", () => {
    const cards = [
      makeCard({ cargo: "Estágio em Frontend", empresa: "Empresa A", link: "https://link.com/a" }),
    ];

    it("retorna true para match de cargo e empresa ignorando maiúsculas/minúsculas e espaços", () => {
      expect(
        isJobSaved(cards, {
          cargo: "  estágio em frontend  ",
          empresa: "EMPRESA A",
        })
      ).toBe(true);
    });

    it("retorna true para match de link", () => {
      expect(
        isJobSaved(cards, {
          cargo: "Outro cargo",
          empresa: "Outra empresa",
          link: "https://link.com/a",
        })
      ).toBe(true);
    });

    it("retorna false quando a vaga não está na lista", () => {
      expect(
        isJobSaved(cards, {
          cargo: "Estágio em Backend",
          empresa: "Empresa B",
          link: "https://link.com/b",
        })
      ).toBe(false);
    });

    it("retorna false se cargo ou empresa estiverem vazios", () => {
      expect(isJobSaved(cards, { cargo: "", empresa: "" })).toBe(false);
    });
  });

  describe("normalizeModalidade", () => {
    it("normaliza modalidades corretamente", () => {
      expect(normalizeModalidade("Remoto")).toBe("Remoto");
      expect(normalizeModalidade("remote")).toBe("Remoto");
      expect(normalizeModalidade("Híbrido")).toBe("Híbrido");
      expect(normalizeModalidade("hibrido")).toBe("Híbrido");
      expect(normalizeModalidade("Presencial")).toBe("Presencial");
      expect(normalizeModalidade("on-site")).toBe("Presencial");
      expect(normalizeModalidade("indefinido")).toBeUndefined();
      expect(normalizeModalidade(undefined)).toBeUndefined();
    });
  });

  describe("saveJobToStorage", () => {
    it("salva uma nova vaga com status salvo e dados corretos", () => {
      const result = saveJobToStorage({
        cargo: "Estágio em QA",
        empresa: "Tech Corp",
        local: "Rio de Janeiro, RJ",
        modalidade: "Remoto",
        link: "https://techcorp.com/vaga/qa",
      });

      expect(result.success).toBe(true);
      expect(result.alreadySaved).toBe(false);
      expect(result.cards).toHaveLength(1);
      expect(result.cards[0].cargo).toBe("Estágio em QA");
      expect(result.cards[0].empresa).toBe("Tech Corp");
      expect(result.cards[0].local).toBe("Rio de Janeiro, RJ");
      expect(result.cards[0].modalidade).toBe("Remoto");
      expect(result.cards[0].status).toBe("salvo");
      expect(result.cards[0].link).toBe("https://techcorp.com/vaga/qa");
      expect(result.cards[0].notas).toBe("");
      expect(result.cards[0].etapas).toEqual([]);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        STORAGE_KEY,
        expect.stringContaining("Estágio em QA")
      );
    });

    it("não duplica vaga se já estiver salva e retorna alreadySaved = true", () => {
      const existing = makeCard({
        cargo: "Estágio em QA",
        empresa: "Tech Corp",
      });
      localStorageMock.setItem(STORAGE_KEY, JSON.stringify([existing]));

      const result = saveJobToStorage({
        cargo: "Estágio em QA",
        empresa: "Tech Corp",
      });

      expect(result.success).toBe(true);
      expect(result.alreadySaved).toBe(true);
      expect(result.cards).toHaveLength(1);
    });

    it("insere novos cards no topo da lista", () => {
      const card1 = makeCard({ id: "1", cargo: "Vaga 1", empresa: "Empresa 1" });
      localStorageMock.setItem(STORAGE_KEY, JSON.stringify([card1]));

      const result = saveJobToStorage({
        cargo: "Vaga 2",
        empresa: "Empresa 2",
      });

      expect(result.cards).toHaveLength(2);
      expect(result.cards[0].cargo).toBe("Vaga 2");
      expect(result.cards[1].cargo).toBe("Vaga 1");
    });
  });
});
