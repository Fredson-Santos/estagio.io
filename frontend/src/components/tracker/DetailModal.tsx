import React, { useState } from "react";
import type { Card } from "../../types/tracker";
import { COLUNAS, SUGESTOES_ETAPAS, daysAgo, initials } from "../../types/tracker";

interface DetailModalProps {
  card: Card;
  onClose: () => void;
  onDelete: () => void;
  onMove: (status: string) => void;
  onAddEtapa: (titulo: string) => void;
  onToggleEtapa: (etapaId: string) => void;
  onRemoveEtapa: (etapaId: string) => void;
  onArchive?: () => void;
}

const STATUS_CONFIG: Record<string, { bg: string; border: string; text: string; dot: string }> = {
  salvo: {
    bg: "bg-surface-container-low dark:bg-slate-700/60",
    border: "border-outline-variant dark:border-slate-600",
    text: "text-on-surface dark:text-slate-200",
    dot: "bg-outline-variant",
  },
  enviado: {
    bg: "bg-blue-50 dark:bg-blue-950/40",
    border: "border-blue-500/50 dark:border-blue-500/60",
    text: "text-blue-700 dark:text-blue-300",
    dot: "bg-primary",
  },
  entrevista: {
    bg: "bg-amber-50 dark:bg-amber-950/40",
    border: "border-amber-500/50 dark:border-amber-500/60",
    text: "text-amber-700 dark:text-amber-300",
    dot: "bg-amber-500",
  },
  oferta: {
    bg: "bg-emerald-50 dark:bg-emerald-950/40",
    border: "border-emerald-500/50 dark:border-emerald-500/60",
    text: "text-emerald-700 dark:text-emerald-300",
    dot: "bg-emerald-500",
  },
  recusado: {
    bg: "bg-red-50 dark:bg-red-950/40",
    border: "border-red-500/50 dark:border-red-500/60",
    text: "text-red-700 dark:text-red-300",
    dot: "bg-red-500",
  },
};

export default function DetailModal({
  card,
  onClose,
  onDelete,
  onMove,
  onAddEtapa,
  onToggleEtapa,
  onRemoveEtapa,
  onArchive,
}: DetailModalProps) {
  const [novaEtapa, setNovaEtapa] = useState("");
  const sugestoesDisponiveis = SUGESTOES_ETAPAS.filter(
    (s) => !card.etapas?.some((e) => e.titulo === s)
  );

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-surface-container-lowest dark:bg-slate-800 text-on-surface dark:text-slate-100 rounded-xl w-full max-w-[480px] border border-outline-variant/40 dark:border-slate-700 shadow-2xl max-h-[88vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-5 pb-4 border-b border-outline-variant/20 dark:border-slate-700">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary-fixed-dim font-bold text-sm flex items-center justify-center flex-shrink-0">
              {initials(card.empresa)}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-on-surface dark:text-white leading-snug">
                {card.cargo}
              </h2>
              <p className="text-xs text-on-surface-variant dark:text-slate-400 mt-0.5">
                {card.empresa}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full text-on-surface-variant dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-slate-700 transition-colors"
            aria-label="Fechar"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-5 flex flex-col gap-4">
          {/* Localização + modalidade */}
          <div className="flex items-center gap-3 text-xs text-on-surface-variant dark:text-slate-300">
            {card.local && (
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[15px]">location_on</span>
                {card.local}
              </span>
            )}
            {card.modalidade && (
              <span
                className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${
                  card.modalidade === "Remoto"
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800/60"
                    : card.modalidade === "Híbrido"
                    ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800/60"
                    : "bg-surface-container text-on-surface-variant border-outline-variant/40 dark:bg-slate-700 dark:text-slate-300 dark:border-slate-600"
                }`}
              >
                {card.modalidade}
              </span>
            )}
          </div>

          {/* Link e Prazo */}
          <div className="flex items-center justify-between flex-wrap gap-2">
            {card.link && (
              <a
                href={card.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-primary dark:text-[#58a6ff] hover:underline"
              >
                <span className="material-symbols-outlined text-[15px]">open_in_new</span>
                Ver vaga original
              </a>
            )}
            {card.prazo && (
              <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-md bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800/50">
                <span className="material-symbols-outlined text-[14px]">event</span>
                Prazo: {card.prazo}
              </span>
            )}
          </div>

          {/* Notas */}
          {card.notas && (
            <div className="bg-surface-container-low dark:bg-slate-900/60 text-on-surface-variant dark:text-slate-300 rounded-lg p-3 text-xs leading-relaxed border border-outline-variant/20 dark:border-slate-700/60">
              {card.notas}
            </div>
          )}

          {/* Etapas */}
          <div>
            <p className="text-xs font-semibold text-on-surface dark:text-white mb-2">
              Etapas do processo
            </p>

            {card.etapas && card.etapas.length > 0 && (
              <div className="flex flex-col gap-1.5 mb-2.5">
                {card.etapas.map((etapa) => (
                  <div
                    key={etapa.id}
                    className="flex items-center gap-2.5 bg-surface-container-low/60 dark:bg-slate-900/60 border border-outline-variant/30 dark:border-slate-700 rounded-lg px-2.5 py-1.5"
                  >
                    <button
                      onClick={() => onToggleEtapa(etapa.id)}
                      className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 cursor-pointer transition-colors ${
                        etapa.feita
                          ? "bg-emerald-600 border-emerald-600 text-white"
                          : "bg-surface-container-lowest dark:bg-slate-800 border-outline-variant dark:border-slate-600 text-transparent"
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
                      className={`text-xs flex-1 ${
                        etapa.feita
                          ? "text-on-surface-variant/60 dark:text-slate-500 line-through"
                          : "text-on-surface dark:text-slate-200"
                      }`}
                    >
                      {etapa.titulo}
                    </span>
                    <button
                      onClick={() => onRemoveEtapa(etapa.id)}
                      className="text-outline dark:text-slate-400 hover:text-error dark:hover:text-red-400 p-0.5"
                      aria-label={`Remover etapa ${etapa.titulo}`}
                    >
                      <span className="material-symbols-outlined text-[14px]">close</span>
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
                placeholder="Adicionar etapa..."
                className="flex-1 text-xs px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white placeholder:text-outline dark:placeholder:text-slate-500 focus:border-primary focus:outline-none"
              />
              <button
                onClick={() => {
                  if (novaEtapa.trim()) {
                    onAddEtapa(novaEtapa);
                    setNovaEtapa("");
                  }
                }}
                className="px-3 py-2 rounded-lg bg-surface-container dark:bg-slate-700 border border-outline-variant dark:border-slate-600 text-on-surface-variant dark:text-slate-200 hover:bg-surface-container-high dark:hover:bg-slate-600 cursor-pointer font-bold text-sm"
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
                    className="text-[11px] text-on-surface-variant dark:text-slate-300 border border-dashed border-outline-variant dark:border-slate-700 hover:bg-surface-container-low dark:hover:bg-slate-700/60 px-2.5 py-1 rounded-full cursor-pointer transition-colors"
                  >
                    + {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Mover para */}
          <div>
            <p className="text-xs font-semibold text-on-surface dark:text-white mb-2">Mover para</p>
            <div className="flex flex-wrap gap-1.5">
              {COLUNAS.map((col) => {
                const isActive = card.status === col.id;
                const sc = STATUS_CONFIG[col.id] ?? STATUS_CONFIG.salvo;
                return (
                  <button
                    key={col.id}
                    onClick={() => onMove(col.id)}
                    className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg border transition-colors cursor-pointer ${
                      isActive
                        ? `${sc.bg} ${sc.border} ${sc.text}`
                        : "bg-surface-container-lowest dark:bg-slate-900/80 border-outline-variant/50 dark:border-slate-700 text-on-surface-variant dark:text-slate-400 hover:border-outline dark:hover:border-slate-500"
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${sc.dot}`} />
                    {col.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-outline-variant/20 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <button
              onClick={onDelete}
              className="inline-flex items-center gap-1 text-xs text-error dark:text-red-400 hover:underline cursor-pointer font-medium"
            >
              <span className="material-symbols-outlined text-[16px]">delete</span>
              Remover
            </button>
            {card.status === "recusado" && onArchive && (
              <button
                onClick={onArchive}
                className="inline-flex items-center gap-1 text-xs text-on-surface-variant dark:text-slate-400 hover:text-primary dark:hover:text-primary-fixed-dim hover:underline cursor-pointer font-medium transition-colors"
              >
                <span className="material-symbols-outlined text-[16px]">archive</span>
                Arquivar
              </button>
            )}
          </div>
          <span className="text-[11px] text-outline dark:text-slate-500">
            Atualizado {daysAgo(card.updatedAt)}
          </span>
        </div>
      </div>
    </div>
  );
}
