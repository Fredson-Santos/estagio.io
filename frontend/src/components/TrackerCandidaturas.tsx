import { useState, useMemo } from "react";
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

  return (
    <div className="fixed inset-0 bg-on-surface/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-surface-container-lowest rounded-xl w-full max-w-md border border-outline-variant/30 shadow-lg">
        <div className="flex items-center justify-between px-5 py-4 border-b border-outline-variant/20">
          <h2 className="font-headline-sm text-headline-sm font-semibold text-on-surface">Nova candidatura</h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface rounded-full w-8 h-8 flex items-center justify-center hover:bg-surface-container-low transition-colors">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="px-5 py-4 flex flex-col gap-3.5">
          <Field label="Cargo">
            <input
              autoFocus
              value={form.cargo}
              onChange={(e) => setForm({ ...form, cargo: e.target.value })}
              placeholder="Ex: Estágio em Dados"
              className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none transition-all focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </Field>
          <Field label="Empresa">
            <input
              value={form.empresa}
              onChange={(e) => setForm({ ...form, empresa: e.target.value })}
              placeholder="Ex: Nubank"
              className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none transition-all focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Local">
              <input
                value={form.local}
                onChange={(e) => setForm({ ...form, local: e.target.value })}
                placeholder="Cidade ou Remoto"
                className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none transition-all focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </Field>
            <Field label="Modalidade">
              <div className="relative">
                <select
                  value={form.modalidade}
                  onChange={(e) => setForm({ ...form, modalidade: e.target.value })}
                  className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none transition-all focus:ring-2 focus:ring-primary/20 focus:border-primary appearance-none cursor-pointer"
                >
                  <option>Presencial</option>
                  <option>Remoto</option>
                  <option>Híbrido</option>
                </select>
                <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none text-[18px]">expand_more</span>
              </div>
            </Field>
          </div>
          <Field label="Link da vaga (opcional)">
            <input
              value={form.link}
              onChange={(e) => setForm({ ...form, link: e.target.value })}
              placeholder="https://..."
              className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none transition-all focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </Field>
        </div>

        <div className="px-5 py-4 border-t border-outline-variant/20 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="font-label-md text-label-sm text-on-surface-variant hover:text-on-surface px-4 py-2 rounded-lg hover:bg-surface-container-low transition-colors"
          >
            Cancelar
          </button>
          <button
            disabled={!canSave}
            onClick={() => onSave(form)}
            className="font-label-md text-label-sm text-on-primary bg-primary hover:brightness-110 disabled:bg-surface-container-high disabled:text-outline disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-all active:scale-95"
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

  return (
    <div className="fixed inset-0 bg-on-surface/15 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-surface-container-lowest rounded-xl w-full max-w-md border border-outline-variant/30 shadow-lg max-h-[85vh] overflow-y-auto">
        <div className="flex items-start justify-between px-5 py-4 border-b border-outline-variant/20">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary font-bold flex items-center justify-center flex-shrink-0">
              {initials(card.empresa)}
            </div>
            <div>
              <h2 className="font-headline-sm text-headline-sm font-semibold text-on-surface leading-snug">
                {card.cargo}
              </h2>
              <p className="font-body-sm text-on-surface-variant mt-0.5">{card.empresa}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface rounded-full w-8 h-8 flex items-center justify-center hover:bg-surface-container-low transition-colors">
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="px-5 py-4 flex flex-col gap-3.5">
          <div className="flex items-center gap-4 font-body-sm text-body-sm text-on-surface-variant">
            <span className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">location_on</span>
              {card.local}
            </span>
            <span
              className={`font-label-sm text-label-sm px-2 py-0.5 rounded-full border ${MODALIDADE_STYLE[card.modalidade]}`}
            >
              {card.modalidade}
            </span>
          </div>

          {card.link && (
            <a
              href={card.link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 font-body-sm text-body-sm text-primary hover:underline"
            >
              <span className="material-symbols-outlined text-[16px]">open_in_new</span>
              Ver vaga original
            </a>
          )}

          {card.notas && (
            <div className="bg-surface-container rounded-lg p-3 font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
              {card.notas}
            </div>
          )}

          <div>
            <p className="font-label-md text-label-sm font-medium text-on-surface mb-2">
              Etapas do processo
            </p>

            {card.etapas && card.etapas.length > 0 && (
              <div className="flex flex-col gap-1.5 mb-2.5">
                {card.etapas.map((etapa) => (
                  <div
                    key={etapa.id}
                    className="flex items-center gap-2.5 group bg-surface-container-lowest rounded-lg px-2.5 py-2 border border-outline-variant/20"
                  >
                    <button
                      onClick={() => onToggleEtapa(etapa.id)}
                      className={`w-4 h-4 rounded-md border flex items-center justify-center flex-shrink-0 transition-colors ${
                        etapa.feita
                          ? "bg-emerald-500 border-emerald-500 text-white"
                          : "border-outline-variant bg-surface-container-lowest"
                      }`}
                    >
                      {etapa.feita && (
                        <svg viewBox="0 0 12 12" className="w-2.5 h-2.5" fill="none">
                          <path
                            d="M2.5 6L5 8.5L9.5 3.5"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinejoin="round"
                            strokeLinecap="round"
                          />
                        </svg>
                      )}
                    </button>
                    <span
                      className={`font-body-sm flex-1 ${
                        etapa.feita ? "text-outline line-through" : "text-on-surface"
                      }`}
                    >
                      {etapa.titulo}
                    </span>
                    <button
                      onClick={() => onRemoveEtapa(etapa.id)}
                      className="opacity-0 group-hover:opacity-100 text-on-surface-variant hover:text-error transition-opacity"
                    >
                      <span className="material-symbols-outlined text-[15px]">close</span>
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-1.5 mb-2">
              <input
                value={novaEtapa}
                onChange={(e) => setNovaEtapa(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && novaEtapa.trim()) {
                    onAddEtapa(novaEtapa);
                    setNovaEtapa("");
                  }
                }}
                placeholder="Adicionar etapa"
                className="w-full font-body-sm text-body-sm px-3 py-2 rounded-lg border border-outline-variant bg-surface text-on-surface outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary flex-1"
              />
              <button
                onClick={() => {
                  if (novaEtapa.trim()) {
                    onAddEtapa(novaEtapa);
                    setNovaEtapa("");
                  }
                }}
                className="font-label-md bg-surface-container border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-high px-3 rounded-lg transition-colors"
              >
                +
              </button>
            </div>

            {sugestoesDisponiveis.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {sugestoesDisponiveis.slice(0, 5).map((s) => (
                  <button
                    key={s}
                    onClick={() => onAddEtapa(s)}
                    className="font-label-sm text-outline border border-dashed border-outline-variant/50 hover:border-outline-variant hover:bg-surface-container-lowest px-2 py-1 rounded-full transition-colors"
                  >
                    + {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <p className="font-label-md font-label-sm font-semibold text-on-surface mb-2">Mover para</p>
            <div className="flex flex-wrap gap-1.5">
              {COLUNAS.map((col) => (
                <button
                  key={col.id}
                  onClick={() => onMove(col.id)}
                  className={`flex items-center gap-1.5 font-label-sm text-label-sm px-2.5 py-1.5 rounded-lg border transition-colors ${
                    card.status === col.id
                      ? `${col.badge} ${col.headerBorder} border`
                      : "bg-surface-container-lowest text-on-surface-variant border-outline-variant/40 hover:border-outline-variant"
                  }`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${col.dot}`} />
                  {col.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-outline-variant/20 flex justify-between items-center">
          <button
            onClick={onDelete}
            className="flex items-center gap-1.5 font-label-md text-error hover:text-error/80 transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">delete</span>
            Remover
          </button>
          <span className="font-label-sm text-outline">
            Atualizado {daysAgo(card.updatedAt)}
          </span>
        </div>
      </div>
    </div>
  );
}