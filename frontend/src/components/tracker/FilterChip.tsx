import React from "react";

interface FilterChipProps {
  active: boolean;
  label: string;
  count: number;
  dot: string;
  onClick: () => void;
}

export default function FilterChip({ active, label, count, dot, onClick }: FilterChipProps) {
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
