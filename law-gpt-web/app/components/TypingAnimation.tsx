"use client";

import { useState, useEffect } from "react";

// Native Markdown Parser (Zero NPM dependencies)
const parseMarkdown = (text: string) => {
  let html = text
    // Format ## and ### Headers
    .replace(/### (.*?)\n/g, '<h3 class="text-lg font-bold mt-4 mb-1 text-[var(--foreground)]">$1</h3>\n')
    .replace(/## (.*?)\n/g, '<h2 class="text-xl font-bold mt-5 mb-2 text-[var(--foreground)]">$1</h2>\n')
    // Format **Bold** text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[var(--foreground)]">$1</strong>')
    // Format *Italics*
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');

  return { __html: html };
};

export default function TypingAnimation({ text }: { text: string }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let i = 0;
    setDisplayedText("");
    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i));
      i++;
      if (i > text.length) clearInterval(interval);
    }, 15); // Adjust this number to make the typing faster or slower!
    return () => clearInterval(interval);
  }, [text]);

  return <span dangerouslySetInnerHTML={parseMarkdown(displayedText)} />;
}w
