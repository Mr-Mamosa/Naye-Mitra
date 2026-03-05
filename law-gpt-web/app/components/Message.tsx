"use client";

import { motion } from "framer-motion";
import TypingAnimation from "./TypingAnimation";

interface MessageProps {
  role: "user" | "ai";
  content: string;
  status?: string | null;
  confidence?: number | null;
  sources?: string[];
  animate?: boolean;
}

const getStatusColor = (status: string) => {
  if (status.includes("LOW")) return "text-green-600 border-green-600/30 bg-green-500/10";
  if (status.includes("MEDIUM")) return "text-amber-600 border-amber-600/30 bg-amber-500/10";
  return "text-red-600 border-red-600/30 bg-red-500/10";
};

const parseMarkdown = (text: string) => {
  let html = text
    .replace(/### (.*?)\n/g, '<h3 class="text-lg font-bold mt-4 mb-1 text-[var(--foreground)]">$1</h3>\n')
    .replace(/## (.*?)\n/g, '<h2 class="text-xl font-bold mt-5 mb-2 text-[var(--foreground)]">$1</h2>\n')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[var(--foreground)]">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  return { __html: html };
};

export default function Message({ role, content, status, confidence, sources, animate = true }: MessageProps) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
    >
      <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[var(--muted-foreground)] mb-2 px-1">
        {isUser ? "Query" : "Analysis"}
      </span>

      <div
        className={`max-w-[85%] px-6 py-5 transition-colors ${
          isUser
            ? "bg-[var(--foreground)] text-[var(--background)] rounded-none shadow-md"
            : "border border-[var(--border-color)] text-[var(--foreground)] bg-[var(--background)] rounded-sm"
        }`}
      >
        <div className="leading-relaxed whitespace-pre-wrap text-[15px] font-serif">
          {isUser ? (
            // Keep user queries as raw text for security
            content
          ) : !animate ? (
            // Parse static AI history with our custom Markdown engine
            <span dangerouslySetInnerHTML={parseMarkdown(content)} />
          ) : (
            // Use the animated Markdown parser for new queries
            <TypingAnimation text={content} />
          )}
        </div>

        {status && (
          <div className="mt-6 flex flex-col gap-3 border-t border-[var(--border-color)] pt-4">
            <div className={`inline-flex self-start items-center gap-1.5 text-[10px] font-bold tracking-widest uppercase px-2 py-1 border ${getStatusColor(status)}`}>
              {status} ({confidence}%)
            </div>

            {sources && sources.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-1">
                {sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="inline-flex items-center gap-1.5 text-[11px] px-2 py-1 text-[var(--foreground)] opacity-70 bg-[var(--glass-hover)] transition-colors cursor-default"
                  >
                    {source}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
