"use client";

import { MessageSquare, Plus, Trash2 } from "lucide-react";

export default function Sidebar({ cases, activeCaseId, onNewCase, onCaseClick, onDeleteCase }: any) {
  return (
    <div className="flex flex-col h-full bg-[var(--background)] border-r border-[var(--border-color)] transition-colors duration-300">

      {/* 1. LOGO SECTION */}
      <div className="px-6 py-6 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-8 bg-[var(--primary)]"></div>
          <h1 className="font-bold tracking-[0.2em] text-lg uppercase leading-tight text-[var(--foreground)]">
            LAW<br />GPT
          </h1>
        </div>
      </div>

      {/* 2. NEW CASE BUTTON */}
      <div className="px-6 py-5 border-b border-[var(--border-color)]">
        <button
          onClick={onNewCase}
          className="w-full py-3 px-4 flex items-center gap-3 text-[11px] font-bold uppercase tracking-widest border border-[var(--border-color)] hover:border-[var(--primary)]/50 bg-[var(--background)] text-[var(--foreground)] hover:text-[var(--primary)] hover:bg-[var(--glass-hover)] transition-all shadow-sm rounded-md"
        >
          <Plus size={14} /> NEW CASE
        </button>
      </div>

      {/* 3. INDEX LIST */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-2">
        <p className="text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-4">
          Index
        </p>

        {cases.map((c: any, idx: number) => (
          <div
            key={idx}
            onClick={() => onCaseClick(c.case_id)}
            className={`w-full group relative flex items-center gap-3 px-3 py-3 rounded-md transition-colors text-sm cursor-pointer ${
              activeCaseId === c.case_id
                ? 'bg-[var(--primary)]/10 text-[var(--primary)]'
                : 'hover:bg-[var(--glass-hover)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]'
            }`}
          >
            <MessageSquare size={14} className="opacity-70 shrink-0" />
            <span className="truncate pr-6">{c.title || "Untitled Document"}</span>

            <button
              onClick={(e) => onDeleteCase(c.case_id, e)}
              className="absolute right-3 opacity-0 group-hover:opacity-100 hover:text-red-500 transition-opacity"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}
