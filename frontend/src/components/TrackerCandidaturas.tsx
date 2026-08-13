import React from "react";
import { useTracker } from "../hooks/useTracker";
import { COLUNAS, CARD_BORDER_LEFT, statusDateLabel, formatPrazo, initials } from "../types/tracker";
import StatCard from "./tracker/StatCard";
import FilterChip from "./tracker/FilterChip";
import BoardColumn from "./tracker/BoardColumn";
import NewCardModal from "./tracker/NewCardModal";
import DetailModal from "./tracker/DetailModal";

export default function TrackerCandidaturas() {
  const tracker = useTracker();

  return (
    <>
      {/* Header com Breadcrumb + Título + Botão Nova Candidatura */}
      <div className="mb-6 px-4 md:px-6 max-w-container-max mx-auto">
        <nav className="flex items-center gap-2 font-body-sm text-body-sm text-on-surface-variant mb-2" aria-label="Breadcrumb">
          <a href="/" className="hover:text-primary transition-colors">Início</a>
          <span className="material-symbols-outlined text-[16px] text-outline">chevron_right</span>
          <a href="/vagas" className="hover:text-primary transition-colors">Vagas</a>
          <span className="material-symbols-outlined text-[16px] text-outline">chevron_right</span>
          <span className="text-on-surface truncate flex-1 min-w-0">Minhas candidaturas</span>
        </nav>

        <div className="flex items-end justify-between flex-wrap gap-4">
          <div>
            <h1 className="font-headline-lg text-headline-lg font-bold tracking-tight text-on-surface">
              Minhas candidaturas
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">
              Acompanhe cada processo, do salvamento à proposta.
            </p>
          </div>

          <button
            onClick={() => tracker.setModalOpen(true)}
            className="hidden md:inline-flex items-center gap-2 bg-primary text-on-primary font-label-md font-semibold px-4 py-2 rounded-lg border-none cursor-pointer whitespace-nowrap hover:brightness-110 active:scale-95 transition-all shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nova candidatura
          </button>
        </div>
      </div>

      {/* Stats bar */}
      <div className="px-4 md:px-6 max-w-container-max mx-auto mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <StatCard label="Total" value={tracker.stats.total} icon="apartment" />
          <StatCard label="Em andamento" value={tracker.stats.emAndamento} icon="schedule" />
          <StatCard label="Entrevistas" value={tracker.stats.entrevistas} icon="videocam" />
          <StatCard label="Taxa de resposta" value={`${tracker.stats.taxaResposta}%`} icon="trending_up" />
        </div>
      </div>

      {/* Board — desktop */}
      <div className="hidden md:block px-4 md:px-6 max-w-container-max mx-auto">
        <div
          className="flex gap-3.5 overflow-x-auto pb-6"
          style={{ scrollbarWidth: "thin", scrollbarColor: "#c1c6d7 transparent" }}
        >
          {COLUNAS.map((col) => (
            <BoardColumn
              key={col.id}
              col={col}
              items={tracker.byStatus(col.id)}
              dragId={tracker.dragId}
              isOver={tracker.dragOverCol === col.id}
              onDragStart={tracker.onDragStart}
              onDragEnd={tracker.onDragEnd}
              onDragOver={tracker.onDragOverCol}
              onDragLeave={tracker.onDragLeaveCol}
              onDrop={tracker.onDropCol}
              onCardClick={(id) => tracker.setDetailId(id)}
            />
          ))}
          {/* Spacer para garantir que a última coluna não seja cortada */}
          <div className="flex-shrink-0 w-1" />
        </div>
      </div>

      {/* Board — mobile */}
      <div className="md:hidden px-4">
        <div className="flex gap-1.5 overflow-x-auto pb-3 no-scrollbar">
          <FilterChip
            active={tracker.mobileFilter === "todos"}
            label="Todos"
            count={tracker.filtered.length}
            dot="bg-on-surface-variant"
            onClick={() => tracker.setMobileFilter("todos")}
          />
          {COLUNAS.map((col) => (
            <FilterChip
              key={col.id}
              active={tracker.mobileFilter === col.id}
              label={col.label}
              count={tracker.byStatus(col.id).length}
              dot={col.dot}
              onClick={() => tracker.setMobileFilter(col.id)}
            />
          ))}
        </div>

        <div className="flex flex-col gap-2 mt-2">
          {tracker.filtered
            .filter((c) => tracker.mobileFilter === "todos" || c.status === tracker.mobileFilter)
            .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
            .map((card) => {
              const prazoText = formatPrazo(card.prazo);

              return (
                <div
                  key={card.id}
                  onClick={() => tracker.setDetailId(card.id)}
                  className={`bg-surface-container-lowest dark:bg-[#242f44] rounded-lg border border-outline-variant/30 dark:border-slate-600/60 border-l-[3px] p-3 active:bg-surface-container-low dark:active:brightness-125 transition-all flex flex-col gap-2`}
                  style={{ borderLeftColor: CARD_BORDER_LEFT[card.status] }}
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-md bg-primary/10 dark:bg-primary/25 text-primary dark:text-primary-fixed-dim font-bold text-xs flex items-center justify-center flex-shrink-0">
                      {initials(card.empresa)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-[13px] leading-tight text-on-surface dark:text-white truncate">
                        {card.cargo}
                      </p>
                      <p className="text-[11px] text-on-surface-variant dark:text-slate-300 truncate mt-0.5">
                        {card.empresa}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-1.5 border-t border-outline-variant/15 dark:border-slate-600/60 text-[11px] text-on-surface-variant dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-[13px]">schedule</span>
                      <span>{statusDateLabel(card.status, card.updatedAt)}</span>
                    </div>

                    {prazoText ? (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-100 text-red-700 border border-red-200 dark:bg-[#3d1418] dark:text-[#f85149] dark:border-[#f85149]/30 leading-none">
                        {prazoText}
                      </span>
                    ) : card.etapas && card.etapas.length > 0 ? (
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] bg-surface-container-low dark:bg-slate-700 text-on-surface-variant dark:text-slate-200 leading-none">
                        <span className="material-symbols-outlined text-[11px]">checklist</span>
                        {card.etapas.filter((e) => e.feita).length}/{card.etapas.length}
                      </span>
                    ) : null}
                  </div>
                </div>
              );
            })}

          {tracker.filtered.filter(
            (c) => tracker.mobileFilter === "todos" || c.status === tracker.mobileFilter
          ).length === 0 && (
            <div className="text-center font-body-sm text-body-sm text-on-surface-variant dark:text-slate-400 py-16 border border-dashed border-outline-variant/30 dark:border-slate-700/60 rounded-lg bg-surface-container-low/30 dark:bg-[#161a22]/30">
              Nenhuma candidatura aqui ainda
            </div>
          )}
        </div>
      </div>

      {/* Botão flutuante — mobile */}
      <button
        onClick={() => tracker.setModalOpen(true)}
        className="md:hidden fixed bottom-5 right-5 w-14 h-14 rounded-full bg-primary text-on-primary shadow-lg flex items-center justify-center z-40 hover:brightness-110 active:scale-95 transition-all"
        aria-label="Nova candidatura"
      >
        <span className="material-symbols-outlined text-[24px]">add</span>
      </button>

      {/* Modal: nova candidatura */}
      {tracker.modalOpen && (
        <NewCardModal
          onClose={() => tracker.setModalOpen(false)}
          onSave={tracker.addCard}
        />
      )}

      {/* Modal: detalhe */}
      {tracker.detailCard && (
        <DetailModal
          card={tracker.detailCard}
          onClose={() => tracker.setDetailId(null)}
          onDelete={() => tracker.deleteCard(tracker.detailCard!.id)}
          onMove={(status) => tracker.moveCard(tracker.detailCard!.id, status)}
          onAddEtapa={(titulo) => tracker.addEtapa(tracker.detailCard!.id, titulo)}
          onToggleEtapa={(etapaId) => tracker.toggleEtapa(tracker.detailCard!.id, etapaId)}
          onRemoveEtapa={(etapaId) => tracker.removeEtapa(tracker.detailCard!.id, etapaId)}
        />
      )}

      <style>{`.no-scrollbar::-webkit-scrollbar { display: none; } .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }`}</style>
    </>
  );
}
