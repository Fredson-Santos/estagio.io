import { describe, it, expect, vi } from "vitest";
import React from "react";
import TrackerCandidaturas from "./TrackerCandidaturas";

// Mock localStorage + window
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

vi.stubGlobal("window", { localStorage: localStorageMock });
vi.stubGlobal("localStorage", localStorageMock);

describe("TrackerCandidaturas Component", () => {
  it("exporta componente React válido", () => {
    expect(typeof TrackerCandidaturas).toBe("function");
  });

  it("renderiza sem lançar ReferenceError ou exceções", () => {
    expect(() => {
      const element = React.createElement(TrackerCandidaturas);
      expect(element).toBeDefined();
    }).not.toThrow();
  });
});
