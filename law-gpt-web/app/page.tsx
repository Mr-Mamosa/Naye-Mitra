"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Scale, FileText, Search, ArrowRight, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    // FIX 1: Removed 'overflow-x-hidden' ·from this div to fix the scroll lock!
    <div className="bg-[#FDFBF7] text-[#1A1A1A] font-sans selection:bg-[#D34343] selection:text-white scroll-smooth min-h-screen flex flex-col">

      {/* Background Accent */}
      <div className="absolute top-[-10%] right-[-5%] w-[600px] h-[600px] bg-[#D34343]/5 rounded-full blur-[120px] pointer-events-none"></div>

      {/* ================= NAVBAR ================= */}
      <nav className="w-full border-b border-black/5 bg-white/70 backdrop-blur-md fixed top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-3 hover:opacity-70 transition-opacity"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            <Scale className="text-[#D34343]" size={24} />
            <span className="font-bold tracking-[0.2em] text-lg uppercase">
              Law-GPT
            </span>
          </Link>

          <div className="flex items-center gap-8 text-[11px] font-bold tracking-[0.15em] uppercase text-black/60">
            <a href="#features" className="hover:text-black transition-colors hidden md:block">
              Features
            </a>
            <Link href="/login" className="hover:text-black transition-colors">
              Sign In
            </Link>

            <Link
              href="/workspace"
              onClick={() => localStorage.setItem("lawgpt_role", "guest")}
              className="px-6 py-2.5 bg-[#1A1A1A] text-white hover:bg-[#D34343] transition-colors flex items-center gap-2 rounded-sm"
            >
              Try For Free <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </nav>

      {/* ================= HERO ================= */}
      <main className="max-w-7xl mx-auto px-6 pt-40 pb-20 relative z-10 flex-grow">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="inline-block py-1 px-3 border border-[#D34343]/30 bg-[#D34343]/5 text-[#D34343] text-[10px] font-bold uppercase tracking-widest rounded-full mb-8">
              The New Standard in Legal Tech
            </span>

            <h1 className="text-5xl md:text-7xl font-serif leading-[1.1] mb-8">
              Draft, Research, and Win with{" "}
              <span className="italic text-[#D34343]">Confidence.</span>
            </h1>

            <p className="text-lg text-black/60 leading-relaxed mb-12 max-w-2xl mx-auto font-medium">
              Law-GPT is an advanced AI assistant built exclusively for Indian Law.
              Instantly analyze case facts, retrieve relevant statutes, and draft
              court-ready legal notices.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center gap-4 justify-center"
          >
            <Link
              href="/workspace"
              onClick={() => localStorage.setItem("lawgpt_role", "guest")}
              className="px-8 py-4 bg-[#D34343] text-white font-bold uppercase tracking-widest text-xs hover:bg-[#1A1A1A] transition-colors shadow-lg rounded-sm"
            >
              Start 5-Minute Free Trial
            </Link>

            <p className="text-[10px] text-black/40 uppercase tracking-widest font-bold flex items-center gap-2">
              <ShieldCheck size={14} className="text-[#D34343]" />
              No Credit Card Required
            </p>
          </motion.div>
        </div>

        {/* ================= FEATURES ================= */}
        <section
          id="features"
          className="grid md:grid-cols-3 gap-8 mt-32 pt-20 border-t border-black/5 scroll-mt-32 mb-32"
        >
          <FeatureCard
            icon={<Search size={24} />}
            title="Instant Case Analysis"
            text="Upload client facts and let AI find statutory violations in seconds."
          />
          <FeatureCard
            icon={<FileText size={24} />}
            title="Automated Drafting"
            text="Generate Legal Notices, Petitions, and Applications formatted for Indian courts."
          />
          <FeatureCard
            icon={<Scale size={24} />}
            title="Supreme Court Precedents"
            text="Back your arguments with landmark judgments instantly retrieved."
          />
        </section>
      </main>

      {/* ================= FIX 2: THE RESTORED FOOTER ================= */}
      <footer className="w-full border-t border-black/5 bg-white pt-20 pb-16 mt-auto">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-12 text-[11px] font-bold uppercase tracking-widest text-black/60">

            {/* Logo/Identity */}
            <div className="flex flex-col gap-6 md:col-span-1">
              <div className="flex items-center gap-3">
                <Scale className="text-[#D34343]" size={20} />
                <span className="font-bold tracking-[0.2em] text-sm uppercase text-[#1A1A1A]">Law-GPT</span>
              </div>
              <p className="font-normal text-xs text-black/50 leading-relaxed font-sans normal-case tracking-normal">
                Generative Artificial Intelligence sovereign database for localized Indian legal analysis.
                Running locally on dedicated hardware.
              </p>
            </div>

            {/* Platform Links */}
            <div className="flex flex-col gap-3">
              <h4 className="text-[#1A1A1A] mb-3">Capabilities</h4>
              <Link href="#features" className="hover:text-[#D34343] transition-colors">Case Analysis</Link>
              <Link href="#features" className="hover:text-[#D34343] transition-colors">Drafting Wizard</Link>
              <Link href="#features" className="hover:text-[#D34343] transition-colors">RAG Telemetry</Link>
              <Link href="/workspace" className="hover:text-[#D34343] transition-colors">Workspace Trial</Link>
            </div>

            {/* Resources/Legal */}
            <div className="flex flex-col gap-3">
              <h4 className="text-[#1A1A1A] mb-3">Institutional Resources</h4>
              <Link href="#" className="hover:text-[#D34343] transition-colors">About the Project</Link>
              <Link href="/login" className="hover:text-[#D34343] transition-colors">Admin Login</Link>
              <Link href="#" className="hover:text-[#D34343] transition-colors">Terms of Service</Link>
              <Link href="#" className="hover:text-[#D34343] transition-colors">Privacy Policy (Local DB)</Link>
            </div>
          </div>

          {/* Copyright/Admin Bottom Bar */}
          <div className="mt-16 pt-8 border-t border-black/5 flex flex-col sm:flex-row justify-between items-center text-[10px] font-bold uppercase tracking-widest text-black/40 gap-4">
            <span>© {new Date().getFullYear()} LAW-GPT LEGAL ENGINE. A SOVEREIGN PROJECT.</span>

            <div className="flex items-center gap-3">
              <span>System Status</span>
              <div className="w-6 h-6 rounded-full border border-black/10 bg-white shadow flex items-center justify-center font-bold text-[10px] text-[#D34343]" title="All Systems Operational">
                ✓
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ChatGPT's Clean Feature Card Component
function FeatureCard({ icon, title, text }: any) {
  return (
    <div className="text-center flex flex-col items-center group">
      <div className="w-16 h-16 rounded-full bg-black/5 flex items-center justify-center mb-6 group-hover:bg-[#D34343]/10 transition-colors">
        <div className="text-[#1A1A1A] group-hover:text-[#D34343] transition-colors">
          {icon}
        </div>
      </div>
      <h3 className="text-sm font-bold tracking-widest uppercase mb-3">
        {title}
      </h3>
      <p className="text-black/60 text-sm leading-relaxed px-4">{text}</p>
    </div>
  );
}
