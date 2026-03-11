"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Download, Moon, Sun, Database, Cpu, Clock, Lock, ShieldCheck, FileText, Menu, History, X, MoreVertical } from "lucide-react";
import Sidebar from "../components/Sidebar";
import Message from "../components/Message";
import ChatInput from "../components/ChatInput";

interface MessageData {
  role: "user" | "ai";
  content: string;
  status: string | null;
  confidence: number | null;
  sources?: string[];
  animate?: boolean;
}

export default function LawGPTInterface() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<MessageData[]>([
    {
      role: "ai",
      content: "Welcome to Law-GPT. Please describe your legal issue, and I will analyze it under Indian Law.",
      status: null,
      confidence: null,
      animate: true,
    },
  ]);

  const [cases, setCases] = useState<any[]>([]);
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // UI & Modal States
  const [showLibrary, setShowLibrary] = useState(false);
  const [showArchitecture, setShowArchitecture] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showMenuDropdown, setShowMenuDropdown] = useState(false);

  // Auth & Timer States
  const [timeLeft, setTimeLeft] = useState(300); // 300 seconds = 5 minutes
  const [isAdmin, setIsAdmin] = useState(false);
  const [isMounted, setIsMounted] = useState(false); // <--- ADD THIS LINE

  // Click outside listener for the dropdown menu
  const dropdownRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowMenuDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 1. Check if user is an Admin on load
  useEffect(() => {
    setIsMounted(true);
    const role = localStorage.getItem("lawgpt_role");
    if (role === "admin") {
      setIsAdmin(true);
    }
  }, []);

  // 2. ONLY tick the timer down if they are NOT an Admin
  useEffect(() => {
    if (!isAdmin && timeLeft > 0) {
      const timerId = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timerId);
    }
  }, [timeLeft, isAdmin]);

  const isTrialExpired = !isAdmin && timeLeft === 0;

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDarkMode]);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSidebarCases = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/cases/lawyer_1");
      if (response.ok) {
        const data = await response.json();
        setCases(data.cases);
      }
    } catch (error) {
      console.error("Failed to fetch cases:", error);
    }
  };

  useEffect(() => {
    fetchSidebarCases();
  }, []);

  const fetchCaseMessages = async (caseId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/case/${caseId}`);
      if (response.ok) {
        const data = await response.json();
        const historyMessages = data.messages.map((msg: any) => ({
          ...msg,
          animate: false,
        }));
        setMessages(historyMessages);
        setActiveCaseId(caseId);
      }
    } catch (error) {
      console.error("Failed to fetch case messages:", error);
    }
  };

  const handleNewCase = () => {
    setActiveCaseId(null);
    setMessages([
      {
        role: "ai",
        content: "Started a new case workspace.",
        status: null,
        confidence: null,
        animate: true,
      },
    ]);
  };

  const handleDeleteCase = async (caseId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const response = await fetch(`http://localhost:8000/api/v1/case/${caseId}`, { method: "DELETE" });
      if (response.ok) {
        setCases((prev) => prev.filter((c) => c.case_id !== caseId));
        if (activeCaseId === caseId) handleNewCase();
      }
    } catch (error) {
      console.error("Network error deleting case:", error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isTrialExpired) return;
    const userText = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userText, status: null, confidence: null }]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/consult", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userText,
          user_id: "lawyer_1",
          case_id: activeCaseId,
          title: userText.substring(0, 30) + "...",
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "ai",
            content: data.answer,
            status: data.status,
            confidence: data.confidence,
            sources: data.sources,
            animate: true,
          },
        ]);

        if (!activeCaseId) {
          setActiveCaseId(data.case_id);
          fetchSidebarCases();
        }
      }
    } catch (error) {
      console.error("Inference Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPDF = () => {
    const parseMarkdownForPDF = (text: string) => {
      if (!text) return "";
      return text
        .replace(/### (.*?)\n/g, '<h3 style="margin-top: 15px; margin-bottom: 5px; font-size: 13pt; border-bottom: 1px solid #eee; padding-bottom: 3px;">$1</h3>\n')
        .replace(/## (.*?)\n/g, '<h2 style="margin-top: 20px; margin-bottom: 8px; font-size: 14pt; border-bottom: 1px solid #ccc; padding-bottom: 4px;">$1</h2>\n')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
    };

    const exportableMessages = [];

    for (let i = 0; i < messages.length; i++) {
      const msg = messages[i];
      if (i === 0 && msg.role === "ai") continue;

      if (msg.role === "user") {
        const nextMsg = messages[i + 1];
        const isFallback = nextMsg && (
          nextMsg.content.includes("I could not find") ||
          nextMsg.content.includes("fall outside") ||
          nextMsg.status?.includes("ERROR")
        );
        if (nextMsg && !isFallback) exportableMessages.push(msg);
      } else if (msg.role === "ai") {
        const isFallback = msg.content.includes("I could not find") ||
                          msg.content.includes("fall outside") ||
                          msg.status?.includes("ERROR");
        if (!isFallback) exportableMessages.push(msg);
      }
    }

    if (exportableMessages.length === 0) {
      alert("No valid statutory analysis found to export. Please run a successful query first.");
      return;
    }

    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    let html = `
      <html>
      <head>
        <title>Legal Memorandum - Law-GPT</title>
        <style>
          @page { margin: 1in; }
          body { font-family: 'Times New Roman', Times, serif; color: #000; line-height: 1.6; font-size: 11pt; max-width: 8.5in; margin: 0 auto; padding: 20px;}
          .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }
          .header h1 { margin: 0; font-size: 18pt; text-transform: uppercase; letter-spacing: 2px; }
          .header p { margin: 5px 0 0 0; font-size: 10pt; color: #555; text-transform: uppercase; }
          .memo-block { margin-bottom: 30px; line-height: 1.8; }
          .memo-line { display: flex; border-bottom: 1px solid #ccc; padding: 5px 0; }
          .memo-label { font-weight: bold; width: 100px; text-transform: uppercase; }
          .message-block { margin-bottom: 30px; page-break-inside: avoid; }
          .section-title { font-weight: bold; text-decoration: underline; margin-bottom: 15px; text-transform: uppercase; font-size: 12pt; color: #000;}
          .content { text-align: justify; white-space: pre-wrap; margin-bottom: 15px; padding-left: 10px;}
          .sources { font-size: 10pt; font-style: italic; border-left: 3px solid #000; padding-left: 15px; margin-top: 15px; background: #f9f9f9; padding: 10px; color: #333;}
          .footer { margin-top: 50px; border-top: 1px solid #000; padding-top: 10px; font-size: 9pt; text-align: center; color: #777; }
          strong { color: #000; font-weight: 700; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Confidential Legal Memorandum</h1>
          <p>Generated via Law-GPT Artificial Intelligence Legal Engine</p>
        </div>

        <div class="memo-block">
          <div class="memo-line"><div class="memo-label">TO:</div><div>File / Lead Counsel</div></div>
          <div class="memo-line"><div class="memo-label">FROM:</div><div>Law-GPT Automated System</div></div>
          <div class="memo-line"><div class="memo-label">DATE:</div><div>${new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</div></div>
          <div class="memo-line"><div class="memo-label">REF ID:</div><div>${activeCaseId || 'DRAFT-UNSAVED'}</div></div>
        </div>

        <hr style="margin-bottom: 30px; border: 1px solid #000;"/>
    `;

    exportableMessages.forEach(msg => {
      if (msg.role === 'user') {
        html += `<div class="message-block"><div class="section-title">I. Factual Scenario / Query</div><div class="content">${msg.content}</div></div>`;
      } else {
        const formattedContent = parseMarkdownForPDF(msg.content);
        html += `<div class="message-block"><div class="section-title">II. Statutory Analysis & Opinion</div><div class="content">${formattedContent}</div>`;
        if (msg.sources && msg.sources.length > 0) {
          html += `<div class="sources"><strong>Authorities Cited:</strong><br/>${msg.sources.join('<br/>')}</div>`;
        }
        html += `</div>`;
      }
    });

    html += `<div class="footer">NOTICE: This memorandum was generated by an AI system operating on an indexed legal database. It is intended for preliminary research and does not constitute formal legal counsel.</div></body></html>`;

    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 350);
  };

  return (
    <div className="relative flex h-screen bg-[var(--background)] text-[var(--foreground)] font-sans overflow-hidden transition-colors duration-300">

      {/* BACKGROUND ORB */}
      <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[400px] bg-[var(--primary)] opacity-10 dark:opacity-20 rounded-full blur-[100px] pointer-events-none -z-10 animate-pulse" style={{ animationDuration: '6s' }}></div>

      {/* LIBRARY MODAL */}
      <AnimatePresence>
        {showLibrary && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => setShowLibrary(false)}>
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="bg-[var(--background)] border border-[var(--border-color)] p-10 max-w-lg w-full shadow-2xl relative" onClick={(e) => e.stopPropagation()}>
              <button onClick={() => setShowLibrary(false)} className="absolute top-6 right-6 text-[var(--muted-foreground)] hover:text-[var(--primary)]">✕</button>
              <h2 className="text-xl font-bold uppercase tracking-[0.2em] mb-8 border-l-4 border-[var(--primary)] pl-3">Knowledge Assets</h2>
              <div className="space-y-3">
                {[
                  { name: "BNS 2023", desc: "Bharatiya Nyaya Sanhita", status: "Connected", lat: "12ms" },
                  { name: "IPC 1860", desc: "Indian Penal Code", status: "Connected", lat: "8ms" },
                  { name: "SC Judgments", desc: "Precedent Database", status: "Syncing", lat: "45ms" }
                ].map((item, idx) => (
                  <div key={idx} className="border border-[var(--border-color)] p-4 flex justify-between items-center bg-[var(--glass-hover)]">
                    <div>
                      <h3 className="font-bold text-[12px] tracking-widest uppercase">{item.name}</h3>
                      <p className="text-[10px] text-[var(--muted-foreground)] font-mono">{item.desc}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-2 justify-end">
                        <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${item.status === 'Connected' ? 'bg-green-500' : 'bg-amber-500'}`}></span>
                        <span className="text-[10px] font-bold uppercase tracking-tighter">{item.status}</span>
                      </div>
                      <p className="text-[9px] text-[var(--muted-foreground)] font-mono mt-1">{item.lat}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ARCHITECTURE MODAL */}
      <AnimatePresence>
        {showArchitecture && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => setShowArchitecture(false)}>
            <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} className="bg-[var(--background)] border border-[var(--border-color)] p-10 max-w-lg w-full shadow-2xl relative" onClick={(e) => e.stopPropagation()}>
              <button onClick={() => setShowArchitecture(false)} className="absolute top-6 right-6 text-[var(--muted-foreground)] hover:text-[var(--primary)]">✕</button>
              <h2 className="text-xl font-bold uppercase tracking-[0.2em] mb-6 border-l-4 border-[var(--primary)] pl-3">System Architecture</h2>
              <div className="space-y-5 text-[13px] leading-relaxed font-mono">
                <div>
                  <strong className="text-[var(--primary)] uppercase tracking-widest text-[10px]">Inference Engine</strong>
                  <div className="mt-1 bg-[var(--glass-hover)] p-3 border border-[var(--border-color)]">
                    Llama-3.1-8B-Instruct<br/>
                    RTX 3050 (6GB VRAM)
                  </div>
                </div>
                <div>
                  <strong className="text-[var(--primary)] uppercase tracking-widest text-[10px]">Retrieval Pipeline</strong>
                  <div className="mt-1 bg-[var(--glass-hover)] p-3 border border-[var(--border-color)]">
                    ChromaDB + BM25<br/>
                    Cross-Encoder Re-ranker
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* MAIN LAYOUT */}
      <div className="flex w-full h-full max-w-[1600px] mx-auto z-10 p-0 md:p-4 overflow-hidden">

        {/* SIDEBAR WRAPPER (Smooth toggle animation) */}
        <div className={`${isSidebarOpen ? 'w-[260px] md:mr-6 opacity-100' : 'w-0 opacity-0'} shrink-0 transition-all duration-300 ease-in-out overflow-hidden h-full hidden md:block border-r md:border border-[var(--border-color)] bg-[var(--background)]`}>
          <Sidebar cases={cases} activeCaseId={activeCaseId} onNewCase={handleNewCase} onCaseClick={fetchCaseMessages} onDeleteCase={handleDeleteCase} />
        </div>

        <div className="flex-1 flex flex-col relative min-w-0 border md:border border-[var(--border-color)] bg-[var(--background)] overflow-hidden shadow-sm">

          {/* ================= PERFECTLY ALIGNED HEADER ================= */}
          <div className="flex justify-between items-center px-4 py-4 border-b border-[var(--border-color)] z-20 bg-[var(--background)]">

            {/* Left Controls: Sidebar Toggle & Title */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="hidden md:flex p-1.5 rounded-md hover:bg-[var(--glass-hover)] text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
              >
                <Menu size={18} />
              </button>
              <h2 className="text-[11px] font-bold tracking-[0.2em] uppercase text-[var(--muted-foreground)]">Workspace</h2>
            </div>

            {/* Right Controls: Clean, non-overlapping flexbox */}
            <div className="flex items-center gap-2 sm:gap-3">

              {/* Status Badge */}
              {!isMounted ? (
                // 1. Show a subtle loading pulse while checking local storage
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] w-24 h-8 bg-[var(--glass-hover)] animate-pulse border border-[var(--border-color)]"></div>
              ) : !isAdmin ? (
                // 2. Show the Timer for Guests
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] font-bold tracking-widest uppercase font-mono transition-colors bg-red-500/10 text-red-600 border border-red-500/20">
                  <Clock size={12} className={timeLeft < 60 ? 'animate-pulse' : ''} />
                  <span className="hidden sm:inline">{timeLeft > 0 ? `TRIAL: ${formatTime(timeLeft)}` : 'TRIAL EXPIRED'}</span>
                  <span className="sm:hidden">{formatTime(timeLeft)}</span>
                </div>
              ) : (
                // 3. Show Verified Badge for Admins
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] font-bold tracking-widest uppercase bg-[#D34343]/10 text-[#D34343] border border-[#D34343]/20">
                  <ShieldCheck size={12} /> <span className="hidden sm:inline">VERIFIED USER</span>
                </div>
              )}

              {/* Dark Mode Toggle */}
              <button onClick={() => setIsDarkMode(!isDarkMode)} className="flex items-center justify-center w-8 h-8 rounded-md border border-[var(--border-color)] text-[var(--foreground)] hover:bg-[var(--glass-hover)] transition-colors">
                {isDarkMode ? <Sun size={14} /> : <Moon size={14} />}
              </button>

              {/* Drafting Wizard Button */}
              <Link
                href="/doc-builder"
                className="flex items-center gap-2 px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest bg-[var(--primary)] text-white hover:opacity-90 transition-opacity rounded-md"
              >
                <FileText size={12} />
                <span className="hidden lg:inline">Drafting Wizard</span>
              </Link>

              {/* Export PDF Button */}
              <button
                onClick={isAdmin ? handleExportPDF : undefined}
                disabled={!isAdmin}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-colors ${
                  isAdmin
                    ? "text-[var(--primary)] border border-[var(--primary)]/30 hover:bg-[var(--primary)]/10 cursor-pointer"
                    : "text-[var(--muted-foreground)] border border-[var(--border-color)] opacity-60 cursor-not-allowed"
                }`}
                title={isAdmin ? "Export Legal Brief" : "Login to unlock PDF Export"}
              >
                {isAdmin ? <Download size={12} /> : <Lock size={12} />}
                <span className="hidden lg:inline">Export Brief</span>
              </button>

              {/* Dropdown Menu (Replaces floating absolute boxes) */}
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setShowMenuDropdown(!showMenuDropdown)}
                  className="flex items-center justify-center w-8 h-8 rounded-md hover:bg-[var(--glass-hover)] transition-colors border border-transparent hover:border-[var(--border-color)]"
                >
                  <MoreVertical size={16} />
                </button>

                <AnimatePresence>
                  {showMenuDropdown && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 5 }}
                      className="absolute right-0 top-full mt-2 w-48 bg-[var(--background)] border border-[var(--border-color)] rounded-md shadow-xl overflow-hidden z-50 flex flex-col"
                    >
                      <button onClick={() => { setShowLibrary(true); setShowMenuDropdown(false); }} className="flex items-center gap-3 px-4 py-3 text-[10px] font-bold uppercase tracking-widest hover:bg-[var(--glass-hover)] transition-colors text-[var(--foreground)] text-left border-b border-[var(--border-color)]">
                        <Database size={14} className="text-[var(--primary)]" />
                        Library
                      </button>
                      <button onClick={() => { setShowArchitecture(true); setShowMenuDropdown(false); }} className="flex items-center gap-3 px-4 py-3 text-[10px] font-bold uppercase tracking-widest hover:bg-[var(--glass-hover)] transition-colors text-[var(--foreground)] text-left">
                        <Cpu size={14} className="text-[var(--primary)]" />
                        System Arc
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 md:p-8 z-10">
            <div className="max-w-3xl mx-auto space-y-8">
              <AnimatePresence>
                {messages.map((msg, index) => (
                  <Message key={index} role={msg.role} content={msg.content} status={msg.status} confidence={msg.confidence} sources={msg.sources} animate={msg.animate} />
                ))}
              </AnimatePresence>

              {/* ================= GEMINI LOADING ANIMATION ================= */}
              {isLoading && (
                <div className="flex justify-start w-full">
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="relative overflow-hidden bg-[var(--background)] border border-[var(--border-color)] rounded-2xl rounded-tl-sm p-4 shadow-sm max-w-sm mt-4"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-[var(--primary)]/10 dark:via-[var(--primary)]/20 to-transparent z-0"
                      animate={{ x: ["-100%", "200%"] }}
                      transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    />
                    <div className="flex items-center gap-3 relative z-10">
                      <div className="w-8 h-8 rounded-full bg-[var(--primary)]/10 flex items-center justify-center">
                        <Cpu size={14} className="text-[var(--primary)] animate-pulse" />
                      </div>
                      <span className="text-xs tracking-widest uppercase font-bold text-[var(--muted-foreground)]">
                        Analyzing Context...
                      </span>
                    </div>
                  </motion.div>
                </div>
              )}
              <div ref={bottomRef} className="h-4" />
            </div>
          </div>

          <div className="z-20 relative pt-2 pb-4 px-4 md:px-6 max-w-4xl mx-auto w-full bg-[var(--background)]">
            {isTrialExpired ? (
              <div className="w-full bg-[var(--background)] border border-[var(--border-color)] p-4 text-center rounded-md shadow-lg flex flex-col items-center gap-3">
                <Lock className="text-[var(--primary)]" size={24} />
                <div>
                  <h3 className="text-sm font-bold text-[var(--foreground)] uppercase tracking-widest mb-1">Time Limit Reached</h3>
                  <p className="text-xs text-[var(--muted-foreground)]">Your 5-minute guest session has ended. Please log in to continue consulting Law-GPT.</p>
                </div>
                <button onClick={() => window.location.href='/login'} className="mt-2 px-6 py-2 bg-[var(--primary)] text-white text-[11px] font-bold uppercase tracking-widest rounded-md hover:opacity-90 transition-opacity">
                  Log In Now
                </button>
              </div>
            ) : (
              <ChatInput input={input} isLoading={isLoading} onInputChange={setInput} onSend={handleSend} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
