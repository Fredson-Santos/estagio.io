import React, { useState } from "react";
import type { NewCardData } from "../../types/tracker";

interface NewCardModalProps {
  onClose: () => void;
  onSave: (data: NewCardData) => void;
}

export default function NewCardModal({ onClose, onSave }: NewCardModalProps) {
  const [form, setForm] = useState({
    cargo: "",
    empresa: "",
    local: "",
    modalidade: "Presencial" as string,
    link: "",
    prazo: "",
  });

  const canSave = form.cargo.trim() && form.empresa.trim();

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-surface-container-lowest dark:bg-slate-800 text-on-surface dark:text-slate-100 rounded-xl w-full max-w-[460px] border border-outline-variant/40 dark:border-slate-700 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 pb-4 border-b border-outline-variant/20 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-on-surface dark:text-white">
            Nova candidatura
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-full text-on-surface-variant dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-slate-700 transition-colors"
            aria-label="Fechar"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-5 flex flex-col gap-3.5">
          <label className="flex flex-col gap-1">
            <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
              Cargo *
            </span>
            <input
              autoFocus
              value={form.cargo}
              onChange={(e) => setForm({ ...form, cargo: e.target.value })}
              placeholder="Ex: Estágio em Dados"
              className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white placeholder:text-outline dark:placeholder:text-slate-500 focus:border-primary focus:outline-none"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
              Empresa *
            </span>
            <input
              value={form.empresa}
              onChange={(e) => setForm({ ...form, empresa: e.target.value })}
              placeholder="Ex: Nubank"
              className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white placeholder:text-outline dark:placeholder:text-slate-500 focus:border-primary focus:outline-none"
            />
          </label>

          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
                Local
              </span>
              <input
                value={form.local}
                onChange={(e) => setForm({ ...form, local: e.target.value })}
                placeholder="Cidade ou Remoto"
                className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white placeholder:text-outline dark:placeholder:text-slate-500 focus:border-primary focus:outline-none"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
                Modalidade
              </span>
              <div className="relative">
                <select
                  value={form.modalidade}
                  onChange={(e) => setForm({ ...form, modalidade: e.target.value })}
                  className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white appearance-none cursor-pointer pr-8 focus:border-primary focus:outline-none"
                >
                  <option value="Presencial">Presencial</option>
                  <option value="Remoto">Remoto</option>
                  <option value="Híbrido">Híbrido</option>
                </select>
                <span className="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-[18px] text-outline dark:text-slate-400 pointer-events-none">
                  expand_more
                </span>
              </div>
            </label>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
                Link da vaga (opcional)
              </span>
              <input
                value={form.link}
                onChange={(e) => setForm({ ...form, link: e.target.value })}
                placeholder="https://..."
                className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white placeholder:text-outline dark:placeholder:text-slate-500 focus:border-primary focus:outline-none"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-on-surface-variant dark:text-slate-300">
                Prazo (opcional)
              </span>
              <input
                type="date"
                value={form.prazo}
                onChange={(e) => setForm({ ...form, prazo: e.target.value })}
                className="w-full text-sm px-3 py-2 rounded-lg bg-surface-container-lowest dark:bg-slate-900 border border-outline-variant dark:border-slate-700 text-on-surface dark:text-white focus:border-primary focus:outline-none"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 px-5 py-3 border-t border-outline-variant/20 dark:border-slate-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-on-surface-variant dark:text-slate-300 hover:bg-surface-container-low dark:hover:bg-slate-700/60 border border-outline-variant dark:border-slate-700 rounded-lg transition-colors cursor-pointer"
          >
            Cancelar
          </button>
          <button
            disabled={!canSave}
            onClick={() => onSave(form as NewCardData)}
            className="px-4 py-2 text-xs font-medium rounded-lg bg-primary text-on-primary hover:brightness-110 disabled:bg-surface-container dark:disabled:bg-slate-700/60 disabled:text-outline dark:disabled:text-slate-500 disabled:cursor-not-allowed transition-all cursor-pointer shadow-sm"
          >
            Salvar
          </button>
        </div>
      </div>
    </div>
  );
}
