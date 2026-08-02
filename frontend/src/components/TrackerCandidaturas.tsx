import React, { useState, useMemo } from "react";
import type { ReactNode } from "react";

// ---------- Tipos ----------
interface Etapa {
  id: string;
  titulo: string;
  feita: boolean;
}

interface Card {
  id: string;
  cargo: string;
  empresa: string;
  local: string;
  modalidade: "Remoto" | "Presencial" | "Híbrido";
  status: string;
  link: string;
  updatedAt: string;
  notas: string;
  etapas: Etapa[];
}

interface ColunaConfig {
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

// ---------- Config das colunas ----------
// Mapa de cor real da borda esquerda por coluna (para Tailwind v4 que não gera classes dinâmicas de border-l-color customizada)
const CARD_BORDER_LEFT: Record<string, string> = {
  salvo: "#c1c6d7",
  enviado: "#0058c3",
  entrevista: "#f59e0b",
  oferta: "#10b981",
  recusado: "#ba1a1a",
};

const COLUNAS: ColunaConfig[] = [
  {
    id: "salvo",
    label: "Salvo",
    hint: "Quer se candidatar",
    dot: "bg-[#c1c6d7]",
    header: "bg-surface-container-low",
    headerBorder: "border-outline-variant/40",
    badge: "bg-surface-container text-on-surface-variant",
    cardBorder: "",
    dropActive: "border-outline bg-surface-container-low",
  },
  {
    id: "enviado",
    label: "Enviado",
    hint: "Aguardando retorno",
    dot: "bg-primary",
    header: "bg-primary/5",
    headerBorder: "border-primary/20",
    badge: "bg-primary/10 text-primary",
    cardBorder: "",
    dropActive: "border-primary bg-primary/5",
  },
  {
    id: "entrevista",
    label: "Entrevista",
    hint: "Em processo",
    dot: "bg-amber-500",
    header: "bg-amber-50/70",
    headerBorder: "border-amber-200",
    badge: "bg-amber-100 text-amber-700",
    cardBorder: "",
    dropActive: "border-amber-300 bg-amber-50/60",
  },
  {
    id: "oferta",
    label: "Oferta",
    hint: "Proposta recebida",
    dot: "bg-emerald-500",
    header: "bg-emerald-50/70",
    headerBorder: "border-emerald-200",
    badge: "bg-emerald-100 text-emerald-700",
    cardBorder: "",
    dropActive: "border-emerald-300 bg-emerald-50/60",
  },
  {
    id: "recusado",
    label: "Recusado",
    hint: "Não seguiu",
    dot: "bg-red-500",
    header: "bg-red-50/70",
    headerBorder: "border-red-200",
    badge: "bg-red-100 text-red-700",
    cardBorder: "",
    dropActive: "border-red-300 bg-red-50/60",
  },
];

const MODALIDADE_STYLE: Record<string, string> = {
  Remoto: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Presencial: "bg-surface-container text-on-surface-variant border-outline-variant/40",
  Híbrido: "bg-amber-50 text-amber-700 border-amber-200",
};

// ---------- Seed data ----------
const SEED: Card[] = [
  {
    id: "1",
    cargo: "Estágio em Tecnologia",
    empresa: "Grupo Bradesco Seguros",
    local: "Rio de Janeiro, RJ",
    modalidade: "Presencial",
    status: "entrevista",
    link: "",
    updatedAt: "2026-07-28",
    notas: "Entrevista técnica marcada",
    etapas: [
      { id: "e1", titulo: "Teste lógico", feita: true },
      { id: "e2", titulo: "Dinâmica em grupo", feita: true },
      { id: "e3", titulo: "Entrevista técnica", feita: false },
    ],
  },
  {
    id: "2",
    cargo: "Pessoa Estagiária de Dados",
    empresa: "Knewin",
    local: "Remoto",
    modalidade: "Remoto",
    status: "enviado",
    link: "",
    updatedAt: "2026-07-31",
    notas: "",
    etapas: [],
  },
  {
    id: "3",
    cargo: "Programa de Estágio 2026: Builders",
    empresa: "Creditas Soluções Financeiras",
    local: "Remoto",
    modalidade: "Remoto",
    status: "salvo",
    link: "",
    updatedAt: "2026-07-25",
    notas: "",
    etapas: [],
  },
  {
    id: "4",
    cargo: "Estágio Tecnologia - Financeiro",
    empresa: "Villares Metals",
    local: "Sumaré, SP",
    modalidade: "Presencial",
    status: "oferta",
    link: "",
    updatedAt: "2026-07-30",
    notas: "Proposta: R$ 1.800 + VT + VR",
    etapas: [
      { id: "e1", titulo: "Teste técnico", feita: true },
      { id: "e2", titulo: "Entrevista com gestor", feita: true },
      { id: "e3", titulo: "Proposta enviada", feita: true },
    ],
  },
  {
    id: "5",
    cargo: "Programa de Estágio MRV&CO",
    empresa: "MRV&CO",
    local: "São Paulo, SP",
    modalidade: "Presencial",
    status: "recusado",
    link: "",
    updatedAt: "2026-07-20",
    notas: "Buscam formação em Engenharia Civil",
    etapas: [],
  },
  {
    id: "6",
    cargo: "Estágio em Marketing de Produtos Digitais",
    empresa: "Pecege",
    local: "São Paulo, SP",
    modalidade: "Híbrido",
    status: "salvo",
    link: "",
    updatedAt: "2026-07-31",
    notas: "",
    etapas: [],
  },
];

const SUGESTOES_ETAPAS = [
  "Teste lógico",
  "Teste técnico",
  "Dinâmica em grupo",
  "Entrevista RH",
  "Entrevista técnica",
  "Entrevista com gestor",
  "Case/desafio",
  "Proposta enviada",
];

// ---------- Utilidades ----------
function daysAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000);
  if (diff <= 0) return "hoje";
  if (diff === 1) return "1 dia atrás";
  return `${diff} dias atrás`;
}

function initials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

// ---------- Sub-componentes ----------

function StatCard({ label, value, icon, accent }: { label: string; value: string | number; icon: string; accent?: boolean }) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-xl px-4 py-3.5 flex items-center gap-3">
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${
          accent ? "bg-primary text-on-primary" : "bg-surface-container text-on-surface-variant"
        }`}
      >
        <span className="material-symbols-outlined text-[18px]">{icon}</span>
      </div>
      <div>
        <p className="font-headline-sm text-headline-sm font-bold leading-none text-on-surface">{value}</p>
        <p className="font-label-sm text-label-sm text-on-surface-variant mt-1">{label}</p>
      </div>
    </div>
  );
}

function FilterChip({ active, label, count, dot, onClick }: { active: boolean; label: string; count: number; dot: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 flex items-center gap-1.5 font-label-sm text-label-sm px-3 py-2 rounded-full border transition-colors ${
        active
          ? "bg-on-surface text-surface border-on-surface"
          : "bg-surface-container-lowest text-on-surface-variant border-outline-variant/40"
      }`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${active ? "bg-surface" : dot}`} />
      {label}
      <span className={active ? "text-surface/70" : "text-outline"}>{count}</span>
    </button>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-label-sm text-label-sm text-on-surface-variant">{label}</span>
      {children}
    </label>
  );
}

// ---------- Componente Principal ----------
export default function TrackerCandidaturas() {
  const [cards, setCards] = useState<Card[]>(SEED);
  const [query, setQuery] = useState("");
  const [dragId, setDragId] = useState<string | null>(null);
  const [dragOverCol, setDragOverCol] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [mobileFilter, setMobileFilter] = useState("todos");

  const filtered = useMemo(() => {
    if (!query.trim()) return cards;
    const q = query.toLowerCase();
    return cards.filter(
      (c) =>
        c.cargo.toLowerCase().includes(q) || c.empresa.toLowerCase().includes(q)
    );
  }, [cards, query]);

  const byStatus = (status: string) => filtered.filter((c) => c.status === status);

  const stats = useMemo(() => {
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
  }, [cards]);

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

  function addCard(data: Omit<Card, "id" | "status" | "updatedAt" | "notas" | "etapas">) {
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

  return (
    <>
      {/* Stats bar + Search — seção com max-width */}
      <div style={{ padding: "0 24px", maxWidth: "1200px", margin: "0 auto" }}>
        {/* Stats bar */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
          <StatCard label="Total" value={stats.total} icon="apartment" />
          <StatCard label="Em andamento" value={stats.emAndamento} icon="schedule" />
          <StatCard label="Entrevistas" value={stats.entrevistas} icon="trending_up" accent />
          <StatCard label="Taxa de resposta" value={`${stats.taxaResposta}%`} icon="trending_up" />
        </div>

        {/* Search + New button */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "24px" }}>
          <div style={{ position: "relative", flex: 1, maxWidth: "360px" }}>
            <span
              className="material-symbols-outlined"
              style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", fontSize: "16px", color: "#727786", pointerEvents: "none" }}
            >search</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por cargo ou empresa"
              style={{
                width: "100%",
                paddingLeft: "36px",
                paddingRight: "12px",
                paddingTop: "8px",
                paddingBottom: "8px",
                borderRadius: "8px",
                border: "1px solid #c1c6d7",
                background: "#ffffff",
                fontSize: "14px",
                outline: "none",
                boxSizing: "border-box",
              }}
            />
          </div>
          <button
            onClick={() => setModalOpen(true)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "#0058c3",
              color: "#ffffff",
              fontSize: "14px",
              fontWeight: 500,
              padding: "8px 20px",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: "18px" }}>add</span>
            Nova candidatura
          </button>
        </div>
      </div>

      {/* Board — desktop */}
      <div
        className="hidden md:flex gap-4 overflow-x-auto pb-4"
        style={{ paddingLeft: "24px", paddingRight: "24px", scrollbarWidth: "thin", scrollbarColor: "#c1c6d7 transparent" }}
      >
        {COLUNAS.map((col) => {
          const items = byStatus(col.id);
          const isOver = dragOverCol === col.id;
          return (
            <div
              key={col.id}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOverCol(col.id);
              }}
              onDragLeave={() => setDragOverCol((c) => (c === col.id ? null : c))}
              onDrop={(e) => {
                e.preventDefault();
                if (dragId) moveCard(dragId, col.id);
                setDragId(null);
                setDragOverCol(null);
              }}
              className={`flex-shrink-0 w-[270px] rounded-xl border transition-colors ${
                isOver ? col.dropActive : `${col.headerBorder} bg-surface-container-lowest`
              }`}
            >
              <div
                className={`px-4 pt-4 pb-3 flex items-center justify-between rounded-t-xl border-b ${col.header} ${col.headerBorder}`}
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${col.dot}`} />
                  <div>
                    <h3 className="font-label-md text-label-md font-semibold text-on-surface">
                      {col.label}
                    </h3>
                    <p className="font-label-sm text-label-sm text-on-surface-variant/70">{col.hint}</p>
                  </div>
                </div>
                <span
                  className={`font-label-sm text-label-sm font-semibold rounded-full w-6 h-6 flex items-center justify-center ${col.badge}`}
                >
                  {items.length}
                </span>
              </div>

              <div className="px-2.5 pb-3 flex flex-col gap-2 min-h-[80px] pt-3">
                {items.length === 0 && (
                  <div className="text-center font-body-sm text-body-sm text-outline/50 py-8 px-3 border border-dashed border-outline-variant/60 rounded-lg mx-1">
                    Arraste um card pra cá
                  </div>
                )}
                {items.map((card) => (
                  <div
                    key={card.id}
                    draggable
                    onDragStart={() => setDragId(card.id)}
                    onDragEnd={() => setDragId(null)}
                    onClick={() => setDetailId(card.id)}
                    className={`bg-surface-container-lowest rounded-lg border border-outline-variant/30 border-l-[3px] p-3.5 cursor-pointer hover:shadow-md transition-all ${
                      dragId === card.id ? "opacity-40" : "opacity-100"
                    }`}
                    style={{ borderLeftColor: CARD_BORDER_LEFT[card.status] }}
                  >
                    <div className="flex items-start gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary font-label-sm font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                        {initials(card.empresa)}
                      </div>
                      <div className="min-w-0">
                        <p className="font-label-md font-semibold text-on-surface leading-snug line-clamp-2">
                          {card.cargo}
                        </p>
                        <p className="font-label-sm text-on-surface-variant mt-0.5 truncate">
                          {card.empresa}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 text-body-sm font-body-sm text-on-surface-variant mt-2.5">
                      <span className="material-symbols-outlined text-[13px]">location_on</span>
                      <span className="truncate">{card.local}</span>
                    </div>

                    <div className="flex items-center justify-between mt-2.5">
                      <span
                        className={`font-label-sm text-label-sm px-2 py-0.5 rounded-full border ${MODALIDADE_STYLE[card.modalidade]}`}
                      >
                        {card.modalidade}
                      </span>
                      <div className="flex items-center gap-2">
                        {card.etapas && card.etapas.length > 0 && (
                          <span className="font-label-sm text-outline">
                            {card.etapas.filter((e) => e.feita).length}/{card.etapas.length}
                          </span>
                        )}
                        <span className="font-label-sm text-outline">
                          {daysAgo(card.updatedAt)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
        {/* Spacer para garantir que a última coluna não seja cortada */}
        <div className="flex-shrink-0 w-1" />
      </div>

      {/* Board — mobile */}
      <div className="md:hidden px-4">
        <div className="flex gap-1.5 overflow-x-auto pb-3 no-scrollbar">
          <FilterChip
            active={mobileFilter === "todos"}
            label="Todos"
            count={filtered.length}
            dot="bg-on-surface-variant"
            onClick={() => setMobileFilter("todos")}
          />
          {COLUNAS.map((col) => (
            <FilterChip
              key={col.id}
              active={mobileFilter === col.id}
              label={col.label}
              count={byStatus(col.id).length}
              dot={col.dot}
              onClick={() => setMobileFilter(col.id)}
            />
          ))}
        </div>

        <div className="flex flex-col gap-md mt-2">
          {filtered
            .filter((c) => mobileFilter === "todos" || c.status === mobileFilter)
            .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
            .map((card) => {
              const col = COLUNAS.find((c) => c.id === card.status);
              if (!col) return null;
              return (
                <div
                  key={card.id}
                  onClick={() => setDetailId(card.id)}
                  className={`bg-surface-container-lowest rounded-xl border border-outline-variant/30 border-l-[3px] ${col.cardBorder} p-4 active:bg-surface-container-low transition-colors`}
                >
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary font-bold flex items-center justify-center flex-shrink-0">
                      {initials(card.empresa)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-label-md font-semibold text-on-surface leading-snug">
                        {card.cargo}
                      </p>
                      <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
                        {card.empresa}
                      </p>
                      <div className="flex items-center gap-1.5 font-body-sm text-body-sm text-on-surface-variant mt-1.5">
                        <span className="material-symbols-outlined text-[14px]">location_on</span>
                        <span className="truncate">{card.local}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-outline-variant/20">
                    <span
                      className={`flex items-center gap-1.5 font-label-sm text-label-sm px-2 py-0.5 rounded-full ${col.badge}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${col.dot}`} />
                      {col.label}
                    </span>
                    <div className="flex items-center gap-2">
                      {card.etapas && card.etapas.length > 0 && (
                        <span className="font-label-sm text-outline">
                          {card.etapas.filter((e) => e.feita).length}/{card.etapas.length}
                        </span>
                      )}
                      <span className="font-label-sm text-outline">
                        {daysAgo(card.updatedAt)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

          {filtered.filter(
            (c) => mobileFilter === "todos" || c.status === mobileFilter
          ).length === 0 && (
            <div className="text-center font-body-sm text-body-sm text-on-surface-variant py-16 border border-dashed border-outline-variant/30 rounded-xl bg-surface-container-low/30">
              Nenhuma candidatura aqui ainda
            </div>
          )}
        </div>
      </div>

      {/* Botão flutuante — mobile */}
      <button
        onClick={() => setModalOpen(true)}
        className="md:hidden fixed bottom-5 right-5 w-14 h-14 rounded-full bg-primary text-on-primary shadow-lg flex items-center justify-center z-40 hover:brightness-110 active:scale-95 transition-all"
      >
        <span className="material-symbols-outlined text-[24px]">add</span>
      </button>

      {/* Modal: nova candidatura */}
      {modalOpen && (
        <NovaCandidaturaModal
          onClose={() => setModalOpen(false)}
          onSave={addCard}
        />
      )}

      {/* Modal: detalhe */}
      {detailCard && (
        <DetalheModal
          card={detailCard}
          onClose={() => setDetailId(null)}
          onDelete={() => deleteCard(detailCard.id)}
          onMove={(status) => moveCard(detailCard.id, status)}
          onAddEtapa={(titulo) => addEtapa(detailCard.id, titulo)}
          onToggleEtapa={(etapaId) => toggleEtapa(detailCard.id, etapaId)}
          onRemoveEtapa={(etapaId) => removeEtapa(detailCard.id, etapaId)}
        />
      )}

      <style>{`.no-scrollbar::-webkit-scrollbar { display: none; } .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }`}</style>
    </>
  );
}

function NovaCandidaturaModal({ onClose, onSave }: { onClose: () => void; onSave: (data: any) => void }) {
  const [form, setForm] = useState({
    cargo: "",
    empresa: "",
    local: "",
    modalidade: "Presencial" as string,
    link: "",
  });

  const canSave = form.cargo.trim() && form.empresa.trim();

  const inputStyle: React.CSSProperties = {
    width: "100%", fontSize: 14, padding: "8px 12px",
    borderRadius: 8, border: "1px solid #c1c6d7",
    background: "#fff", outline: "none", boxSizing: "border-box",
  };
  const labelStyle: React.CSSProperties = {
    display: "flex", flexDirection: "column", gap: 4,
  };
  const labelTextStyle: React.CSSProperties = {
    fontSize: 12, fontWeight: 500, color: "#414754",
  };

  return (
    <div
      style={{
        position: "fixed", inset: 0,
        background: "rgba(25,28,29,0.5)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 50, padding: "16px",
        backdropFilter: "blur(4px)",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: "12px",
          width: "100%",
          maxWidth: "460px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 20px 40px rgba(0,0,0,0.15)",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid #e5e7eb" }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, color: "#191c1d", margin: 0 }}>Nova candidatura</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "#414754", display: "flex", padding: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>close</span>
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: "16px 20px", display: "flex", flexDirection: "column", gap: 14 }}>
          <label style={labelStyle}>
            <span style={labelTextStyle}>Cargo *</span>
            <input
              autoFocus
              value={form.cargo}
              onChange={(e) => setForm({ ...form, cargo: e.target.value })}
              placeholder="Ex: Estágio em Dados"
              style={inputStyle}
            />
          </label>
          <label style={labelStyle}>
            <span style={labelTextStyle}>Empresa *</span>
            <input
              value={form.empresa}
              onChange={(e) => setForm({ ...form, empresa: e.target.value })}
              placeholder="Ex: Nubank"
              style={inputStyle}
            />
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <label style={labelStyle}>
              <span style={labelTextStyle}>Local</span>
              <input
                value={form.local}
                onChange={(e) => setForm({ ...form, local: e.target.value })}
                placeholder="Cidade ou Remoto"
                style={inputStyle}
              />
            </label>
            <label style={labelStyle}>
              <span style={labelTextStyle}>Modalidade</span>
              <div style={{ position: "relative" }}>
                <select
                  value={form.modalidade}
                  onChange={(e) => setForm({ ...form, modalidade: e.target.value })}
                  style={{ ...inputStyle, appearance: "none", cursor: "pointer", paddingRight: 32 }}
                >
                  <option>Presencial</option>
                  <option>Remoto</option>
                  <option>Híbrido</option>
                </select>
                <span className="material-symbols-outlined" style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#727786", pointerEvents: "none" }}>expand_more</span>
              </div>
            </label>
          </div>
          <label style={labelStyle}>
            <span style={labelTextStyle}>Link da vaga (opcional)</span>
            <input
              value={form.link}
              onChange={(e) => setForm({ ...form, link: e.target.value })}
              placeholder="https://..."
              style={inputStyle}
            />
          </label>
        </div>

        {/* Footer */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, padding: "12px 20px", borderTop: "1px solid #e5e7eb" }}>
          <button
            onClick={onClose}
            style={{ fontSize: 13, color: "#414754", background: "none", border: "1px solid #c1c6d7", padding: "8px 16px", borderRadius: 8, cursor: "pointer" }}
          >
            Cancelar
          </button>
          <button
            disabled={!canSave}
            onClick={() => onSave(form)}
            style={{
              fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 8, cursor: canSave ? "pointer" : "not-allowed",
              background: canSave ? "#0058c3" : "#e5e7eb",
              color: canSave ? "#ffffff" : "#9ca3af",
              border: "none",
            }}
          >
            Salvar
          </button>
        </div>
      </div>
    </div>
  );
}

function DetalheModal({
  card,
  onClose,
  onDelete,
  onMove,
  onAddEtapa,
  onToggleEtapa,
  onRemoveEtapa,
}: {
  card: Card;
  onClose: () => void;
  onDelete: () => void;
  onMove: (status: string) => void;
  onAddEtapa: (titulo: string) => void;
  onToggleEtapa: (etapaId: string) => void;
  onRemoveEtapa: (etapaId: string) => void;
}) {
  const [novaEtapa, setNovaEtapa] = useState("");
  const sugestoesDisponiveis = SUGESTOES_ETAPAS.filter(
    (s) => !card.etapas?.some((e) => e.titulo === s)
  );

  const statusColors: Record<string, { bg: string; border: string; text: string }> = {
    salvo:      { bg: "#f3f4f5", border: "#c1c6d7", text: "#414754" },
    enviado:    { bg: "#eff4ff", border: "#0058c3", text: "#0058c3" },
    entrevista: { bg: "#fffbeb", border: "#f59e0b", text: "#92400e" },
    oferta:     { bg: "#ecfdf5", border: "#10b981", text: "#065f46" },
    recusado:   { bg: "#fff1f2", border: "#ba1a1a", text: "#9f1239" },
  };

  return (
    <div
      style={{
        position: "fixed", inset: 0,
        background: "rgba(25,28,29,0.45)",
        display: "flex", alignItems: "center", justifyContent: "center",
        zIndex: 50, padding: "16px",
        backdropFilter: "blur(4px)",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: "12px",
          width: "100%",
          maxWidth: "480px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 20px 40px rgba(0,0,0,0.15)",
          maxHeight: "88vh",
          overflowY: "auto",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", padding: "20px 20px 16px", borderBottom: "1px solid #e5e7eb" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: "#eff4ff", color: "#0058c3", fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 14 }}>
              {initials(card.empresa)}
            </div>
            <div>
              <h2 style={{ fontSize: 18, fontWeight: 600, color: "#191c1d", lineHeight: 1.3, margin: 0 }}>{card.cargo}</h2>
              <p style={{ fontSize: 13, color: "#414754", marginTop: 2 }}>{card.empresa}</p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", padding: 6, color: "#414754", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "50%" }}>
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>close</span>
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: "16px 20px", display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Localização + modalidade */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 13, color: "#414754" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>location_on</span>
              {card.local}
            </span>
            <span style={{
              fontSize: 12, fontWeight: 500, padding: "2px 8px", borderRadius: 999, border: "1px solid",
              ...(card.modalidade === "Remoto"
                ? { background: "#ecfdf5", color: "#065f46", borderColor: "#a7f3d0" }
                : card.modalidade === "Híbrido"
                ? { background: "#fffbeb", color: "#92400e", borderColor: "#fcd34d" }
                : { background: "#f3f4f5", color: "#414754", borderColor: "#c1c6d7" })
            }}>
              {card.modalidade}
            </span>
          </div>

          {/* Link */}
          {card.link && (
            <a href={card.link} target="_blank" rel="noopener noreferrer" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "#0058c3", textDecoration: "none" }}>
              <span className="material-symbols-outlined" style={{ fontSize: 15 }}>open_in_new</span>
              Ver vaga original
            </a>
          )}

          {/* Notas */}
          {card.notas && (
            <div style={{ background: "#f3f4f5", borderRadius: 8, padding: "10px 12px", fontSize: 13, color: "#414754", lineHeight: 1.5 }}>
              {card.notas}
            </div>
          )}

          {/* Etapas */}
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "#191c1d", marginBottom: 10 }}>Etapas do processo</p>

            {card.etapas && card.etapas.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 10 }}>
                {card.etapas.map((etapa) => (
                  <div key={etapa.id} style={{ display: "flex", alignItems: "center", gap: 10, background: "#f9fafb", borderRadius: 8, padding: "8px 10px", border: "1px solid #e5e7eb" }}>
                    <button
                      onClick={() => onToggleEtapa(etapa.id)}
                      style={{
                        width: 16, height: 16, borderRadius: 4, border: "1px solid",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0, cursor: "pointer",
                        ...(etapa.feita
                          ? { background: "#10b981", borderColor: "#10b981", color: "#fff" }
                          : { background: "#fff", borderColor: "#c1c6d7", color: "transparent" })
                      }}
                    >
                      {etapa.feita && (
                        <svg viewBox="0 0 12 12" style={{ width: 10, height: 10 }} fill="none">
                          <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
                        </svg>
                      )}
                    </button>
                    <span style={{ fontSize: 13, flex: 1, color: etapa.feita ? "#9ca3af" : "#191c1d", textDecoration: etapa.feita ? "line-through" : "none" }}>
                      {etapa.titulo}
                    </span>
                    <button
                      onClick={() => onRemoveEtapa(etapa.id)}
                      style={{ background: "none", border: "none", cursor: "pointer", color: "#9ca3af", padding: 2, display: "flex" }}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 14 }}>close</span>
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
              <input
                value={novaEtapa}
                onChange={(e) => setNovaEtapa(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && novaEtapa.trim()) { onAddEtapa(novaEtapa); setNovaEtapa(""); }
                }}
                placeholder="Adicionar etapa..."
                style={{ flex: 1, fontSize: 13, padding: "8px 12px", borderRadius: 8, border: "1px solid #c1c6d7", outline: "none", background: "#fff" }}
              />
              <button
                onClick={() => { if (novaEtapa.trim()) { onAddEtapa(novaEtapa); setNovaEtapa(""); } }}
                style={{ padding: "8px 14px", borderRadius: 8, border: "1px solid #c1c6d7", background: "#f3f4f5", cursor: "pointer", fontSize: 16, color: "#414754" }}
              >
                +
              </button>
            </div>

            {sugestoesDisponiveis.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {sugestoesDisponiveis.slice(0, 5).map((s) => (
                  <button
                    key={s}
                    onClick={() => onAddEtapa(s)}
                    style={{ fontSize: 12, color: "#414754", border: "1px dashed #c1c6d7", background: "none", padding: "4px 10px", borderRadius: 999, cursor: "pointer" }}
                  >
                    + {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Mover para */}
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: "#191c1d", marginBottom: 10 }}>Mover para</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {COLUNAS.map((col) => {
                const isActive = card.status === col.id;
                const sc = statusColors[col.id] ?? { bg: "#f3f4f5", border: "#c1c6d7", text: "#414754" };
                return (
                  <button
                    key={col.id}
                    onClick={() => onMove(col.id)}
                    style={{
                      display: "flex", alignItems: "center", gap: 6,
                      fontSize: 12, fontWeight: 500,
                      padding: "6px 12px", borderRadius: 8,
                      border: `1px solid ${isActive ? sc.border : "#c1c6d7"}`,
                      background: isActive ? sc.bg : "#fff",
                      color: isActive ? sc.text : "#414754",
                      cursor: "pointer",
                    }}
                  >
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: sc.border, flexShrink: 0 }} />
                    {col.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", borderTop: "1px solid #e5e7eb" }}>
          <button
            onClick={onDelete}
            style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "none", cursor: "pointer", color: "#ba1a1a", fontSize: 13 }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
            Remover
          </button>
          <span style={{ fontSize: 12, color: "#727786" }}>Atualizado {daysAgo(card.updatedAt)}</span>
        </div>
      </div>
    </div>
  );
}
