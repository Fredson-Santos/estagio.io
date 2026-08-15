import { describe, it, expect } from "vitest";
import {
  COLUNAS,
  CARD_BORDER_LEFT,
  MODALIDADE_STYLE,
  SUGESTOES_ETAPAS,
  STORAGE_KEY,
  daysAgo,
  initials,
  statusDateLabel,
  formatPrazo,
} from "./tracker";

describe("tracker constants", () => {
  it("COLUNAS contém os 5 status esperados na ordem correta", () => {
    expect(COLUNAS).toHaveLength(5);
    const ids = COLUNAS.map((c) => c.id);
    expect(ids).toEqual(["salvo", "enviado", "entrevista", "oferta", "recusado"]);
  });

  it("COLUNAS cada coluna tem todas as propriedades obrigatórias", () => {
    const requiredKeys = [
      "id", "label", "hint", "dot", "header",
      "headerBorder", "badge", "cardBorder", "dropActive",
    ];
    for (const col of COLUNAS) {
      for (const key of requiredKeys) {
        expect(col).toHaveProperty(key);
      }
    }
  });

  it("CARD_BORDER_LEFT tem cores hex válidas para todos os status", () => {
    const statusIds = COLUNAS.map((c) => c.id);
    for (const id of statusIds) {
      expect(CARD_BORDER_LEFT[id]).toBeDefined();
      expect(CARD_BORDER_LEFT[id]).toMatch(/^#[0-9a-fA-F]{6}$/);
    }
  });

  it("MODALIDADE_STYLE tem entradas para todas as modalidades", () => {
    expect(MODALIDADE_STYLE).toHaveProperty("Remoto");
    expect(MODALIDADE_STYLE).toHaveProperty("Presencial");
    expect(MODALIDADE_STYLE).toHaveProperty("Híbrido");
  });

  it("SUGESTOES_ETAPAS é um array não-vazio de strings", () => {
    expect(SUGESTOES_ETAPAS.length).toBeGreaterThan(0);
    for (const s of SUGESTOES_ETAPAS) {
      expect(typeof s).toBe("string");
      expect(s.trim().length).toBeGreaterThan(0);
    }
  });

  it("STORAGE_KEY é uma string não-vazia", () => {
    expect(typeof STORAGE_KEY).toBe("string");
    expect(STORAGE_KEY.length).toBeGreaterThan(0);
  });
});

describe("daysAgo", () => {
  it('retorna "hoje" para a data atual', () => {
    const today = new Date().toISOString().slice(0, 10);
    expect(daysAgo(today)).toBe("hoje");
  });

  it('retorna "1 dia atrás" para ontem', () => {
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    expect(daysAgo(yesterday)).toBe("1 dia atrás");
  });

  it('retorna "N dias atrás" para datas anteriores', () => {
    const threeDaysAgo = new Date(Date.now() - 3 * 86400000).toISOString().slice(0, 10);
    expect(daysAgo(threeDaysAgo)).toBe("3 dias atrás");
  });

  it('retorna "hoje" para datas futuras', () => {
    const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    expect(daysAgo(tomorrow)).toBe("hoje");
  });
});

describe("initials", () => {
  it("extrai as iniciais das duas primeiras palavras", () => {
    expect(initials("Grupo Bradesco")).toBe("GB");
    expect(initials("Creditas Soluções Financeiras")).toBe("CS");
  });

  it("retorna uma letra para nomes com uma palavra", () => {
    expect(initials("Nubank")).toBe("N");
    expect(initials("Knewin")).toBe("K");
  });

  it("converte para maiúsculas", () => {
    expect(initials("grupo bradesco")).toBe("GB");
  });

  it("lida com múltiplos espaços", () => {
    expect(initials("  Grupo   Bradesco  ")).toBe("GB");
  });
});

describe("statusDateLabel", () => {
  it("retorna o prefixo do status com a data relativa", () => {
    const today = new Date().toISOString().slice(0, 10);
    expect(statusDateLabel("salvo", today)).toBe("Salvo hoje");
    expect(statusDateLabel("enviado", today)).toBe("Enviado hoje");
    expect(statusDateLabel("entrevista", today)).toBe("Entrevista hoje");
  });
});

describe("formatPrazo", () => {
  it("retorna null se não houver prazo", () => {
    expect(formatPrazo(undefined)).toBeNull();
    expect(formatPrazo("")).toBeNull();
  });

  it("formata dias restantes corretamente", () => {
    const threeDays = new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
    expect(formatPrazo(threeDays)).toBe("3 dias p/ prazo");
  });
});

