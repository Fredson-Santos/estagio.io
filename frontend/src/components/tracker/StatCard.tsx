import React from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  accent?: boolean;
}

export default function StatCard({ label, value, icon, accent }: StatCardProps) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/30 rounded-lg px-4 py-3 flex items-center gap-3">
      <div
        className={`w-9 h-9 rounded-md flex items-center justify-center flex-shrink-0 ${
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
