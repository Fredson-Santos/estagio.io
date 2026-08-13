import React from "react";
import type { Card, ColunaConfig } from "../../types/tracker";
import { CARD_BORDER_LEFT, statusDateLabel, formatPrazo, initials } from "../../types/tracker";

interface BoardColumnProps {
  col: ColunaConfig;
  items: Card[];
  dragId: string | null;
  isOver: boolean;
  onDragStart: (id: string) => void;
  onDragEnd: () => void;
  onDragOver: (colId: string) => void;
  onDragLeave: (colId: string) => void;
  onDrop: (colId: string) => void;
  onCardClick: (id: string) => void;
}

export default function BoardColumn({
  col,
  items,
  dragId,
  isOver,
  onDragStart,
  onDragEnd,
  onDragOver,
  onDragLeave,
  onDrop,
  onCardClick,
}: BoardColumnProps) {
  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        onDragOver(col.id);
      }}
      onDragLeave={() => onDragLeave(col.id)}
      onDrop={(e) => {
        e.preventDefault();
        onDrop(col.id);
      }}
      className={`flex-1 min-w-[210px] rounded-lg border transition-colors flex flex-col ${
        isOver ? col.dropActive : `${col.headerBorder} bg-surface-container-lowest`
      }`}
    >
      <div
        className={`px-3.5 pt-3 pb-2.5 flex items-center justify-between rounded-t-lg border-b ${col.header} ${col.headerBorder}`}
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
          className={`font-label-sm text-label-sm font-semibold rounded-md w-5 h-5 flex items-center justify-center text-xs ${col.badge}`}
        >
          {items.length}
        </span>
      </div>

      <div className="px-2 pb-2 flex flex-col gap-2 flex-1 min-h-[140px] pt-2">
        {items.length === 0 && (
          <div className="text-center font-body-sm text-body-sm text-outline/50 dark:text-slate-500 py-8 px-2 border border-dashed border-outline-variant/60 dark:border-slate-700/60 rounded-md mx-1 flex-1 flex items-center justify-center">
            Arraste um card pra cá
          </div>
        )}
        {items.map((card) => {
          const prazoText = formatPrazo(card.prazo);

          return (
            <div
              key={card.id}
              draggable
              onDragStart={() => onDragStart(card.id)}
              onDragEnd={onDragEnd}
              onClick={() => onCardClick(card.id)}
              className={`bg-surface-container-lowest dark:bg-[#242f44] rounded-lg border border-outline-variant/30 dark:border-slate-600/60 border-l-[3px] p-2.5 cursor-pointer hover:shadow-sm hover:border-primary/50 dark:hover:border-primary/60 dark:hover:shadow-md transition-all flex flex-col gap-1.5 ${
                dragId === card.id ? "opacity-40" : "opacity-100"
              }`}
              style={{ borderLeftColor: CARD_BORDER_LEFT[card.status] }}
            >
              {/* Header: Avatar + Cargo + Empresa */}
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-primary/10 dark:bg-primary/25 text-primary dark:text-primary-fixed-dim font-bold text-xs flex items-center justify-center flex-shrink-0">
                  {initials(card.empresa)}
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="font-semibold text-[13px] leading-tight text-on-surface dark:text-white truncate">
                    {card.cargo}
                  </h4>
                  <p className="text-[11px] text-on-surface-variant dark:text-slate-300 truncate leading-tight mt-0.5">
                    {card.empresa}
                  </p>
                </div>
              </div>

              {/* Divider + Footer */}
              <div className="border-t border-outline-variant/15 dark:border-slate-600/60 pt-1.5 flex items-center justify-between text-[11px] text-on-surface-variant dark:text-slate-300">
                <div className="flex items-center gap-1 leading-none">
                  <span className="material-symbols-outlined text-[13px]">schedule</span>
                  <span>{statusDateLabel(card.status, card.updatedAt)}</span>
                </div>

                {prazoText ? (
                  <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-100 text-red-700 border border-red-200 dark:bg-[#3d1418] dark:text-[#f85149] dark:border-[#f85149]/30 leading-none">
                    {prazoText}
                  </span>
                ) : card.etapas && card.etapas.length > 0 ? (
                  <span className="inline-flex items-center gap-0.5 px-1 py-0.5 rounded text-[10px] bg-surface-container-low dark:bg-slate-700 text-on-surface-variant dark:text-slate-200 leading-none">
                    <span className="material-symbols-outlined text-[11px]">checklist</span>
                    {card.etapas.filter((e) => e.feita).length}/{card.etapas.length}
                  </span>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
