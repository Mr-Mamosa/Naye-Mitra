"use client";

import { Send } from "lucide-react";

interface ChatInputProps {
  input: string;
  isLoading: boolean;
  onInputChange: (val: string) => void;
  onSend: () => void;
}

export default function ChatInput({ input, isLoading, onInputChange, onSend }: ChatInputProps) {
  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSend(); }}
      className="relative flex items-end gap-3 w-full"
    >
      <textarea
        value={input}
        onChange={(e) => onInputChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        placeholder="Message Law-GPT..."
        className="w-full bg-[var(--background)] text-[var(--foreground)] border border-[var(--border-color)] rounded-xl p-4 pr-14 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] resize-none min-h-[56px] max-h-[200px] shadow-sm text-sm transition-colors"
        rows={1}
        disabled={isLoading}
      />

      <button
        type="submit"
        disabled={!input.trim() || isLoading}
        className="absolute right-2 bottom-2 p-2.5 bg-[var(--foreground)] text-[var(--background)] rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50 shadow-sm"
      >
        <Send
          size={16}
          className={input.trim() ? "translate-x-0.5 -translate-y-0.5 transition-transform" : ""}
        />
      </button>
    </form>
  );
}
