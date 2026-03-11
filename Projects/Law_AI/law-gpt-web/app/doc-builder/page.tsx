"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, FileText, Download, Scale, CheckCircle, Loader2 } from "lucide-react";

export default function DocumentBuilder() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState("");

  // Form State
  const [formData, setFormData] = useState({
    docType: "legal_notice",
    clientName: "",
    recipientName: "",
    shortSubject: "", // --- NEW: Added a short subject line
    dateOfIncident: "",
    grievance: "",
  });

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    setTimeout(() => {
      // --- FIXED: Formatted the date nicely and fixed the Subject line injection ---
      const formattedDate = new Date(formData.dateOfIncident).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });

      const mockDocument = `REGISTERED A.D. / LEGAL NOTICE

To,
${formData.recipientName.toUpperCase() || "[RECIPIENT NAME]"}
[Recipient Address]

Subject: Legal Notice regarding ${formData.shortSubject || "[Short Subject of Dispute]"}

Under the instructions from and on behalf of my client, ${formData.clientName.toUpperCase() || "[CLIENT NAME]"}, I hereby serve upon you the following Legal Notice:

1. That my client is a peace-loving and law-abiding citizen of India.
2. That on or around ${formattedDate || "[DATE]"}, the following incident occurred: ${formData.grievance || "[Detailed Description of Grievance]"}.
3. That your actions constitute a severe breach of trust and violation of statutory obligations under the applicable provisions of the law.
4. That despite repeated requests and reminders by my client, you have failed to rectify the situation, causing immense mental agony and financial loss to my client.

I, therefore, call upon you through this Legal Notice to immediately cease and desist from your unlawful activities and compensate my client within 15 days of receiving this notice. Failing which, my client has given me clear instructions to initiate appropriate civil and/or criminal proceedings against you in a competent court of law, entirely at your own risk, cost, and consequence.

Copy Kept in Office for Record.

Yours sincerely,

[Advocate Signature]
Advocate for ${formData.clientName || "[CLIENT NAME]"}
Law-GPT Automated Drafting System`;

      setGeneratedDoc(mockDocument);
      setIsGenerating(false);
    }, 2500);
  };

  const handleExport = () => {
    if (!generatedDoc) return;
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    printWindow.document.write(`
      <html>
        <head>
          <title>Legal Document</title>
          <style>
            /* --- FIXED: This CSS hides the browser's default URLs and Timestamps! --- */
            @page { margin: 0; }
            body {
              font-family: 'Times New Roman', serif;
              line-height: 1.6;
              padding: 1in;
              max-width: 800px;
              margin: auto;
            }
            pre {
              font-family: 'Times New Roman', serif;
              white-space: pre-wrap;
              font-size: 12pt;
            }
          </style>
        </head>
        <body>
          <pre>${generatedDoc}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    setTimeout(() => printWindow.print(), 250);
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#1A1A1A] font-sans flex flex-col selection:bg-[#D34343] selection:text-white">

      {/* Top Navigation */}
      <nav className="w-full border-b border-black/5 bg-white px-6 h-16 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-6">
          <Link href="/workspace" className="text-black/50 hover:text-[#D34343] transition-colors flex items-center gap-2 text-[11px] font-bold tracking-widest uppercase">
            <ArrowLeft size={14} /> Back to Workspace
          </Link>
          <div className="h-4 w-px bg-black/10"></div>
          <div className="flex items-center gap-2">
            <FileText className="text-[#D34343]" size={16} />
            <span className="font-bold tracking-[0.2em] text-sm uppercase">Drafting Wizard</span>
          </div>
        </div>

        <button
          onClick={handleExport}
          disabled={!generatedDoc}
          className="px-4 py-2 bg-[#1A1A1A] text-white text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#D34343] transition-colors rounded-sm"
        >
          <Download size={14} /> Export to PDF
        </button>
      </nav>

      {/* Main Split Interface */}
      <div className="flex flex-1 overflow-hidden h-[calc(100vh-64px)]">

        {/* LEFT PANEL: The Intake Form */}
        <div className="w-1/3 border-r border-black/5 bg-white p-8 overflow-y-auto">
          <div className="mb-8">
            <h2 className="text-xl font-serif font-bold mb-2">Client Intake Form</h2>
            <p className="text-xs text-black/50 leading-relaxed">Provide the core facts of the case. The AI will format this into a structured, court-ready legal document.</p>
          </div>

          <form onSubmit={handleGenerate} className="space-y-5">
            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Document Type</label>
              <select
                value={formData.docType}
                onChange={(e) => setFormData({...formData, docType: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm"
              >
                <option value="legal_notice">Formal Legal Notice</option>
                <option value="divorce_mutual">Mutual Divorce Petition (Coming Soon)</option>
                <option value="bail_app">Bail Application (Coming Soon)</option>
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Your Client's Name (Sender)</label>
              <input
                type="text"
                required
                placeholder="e.g. Ramesh Kumar"
                value={formData.clientName}
                onChange={(e) => setFormData({...formData, clientName: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Opposing Party (Recipient)</label>
              <input
                type="text"
                required
                placeholder="e.g. Suresh Singh"
                value={formData.recipientName}
                onChange={(e) => setFormData({...formData, recipientName: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm"
              />
            </div>

            {/* --- NEW INPUT FIELD FOR THE SHORT SUBJECT --- */}
            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Short Subject</label>
              <input
                type="text"
                required
                placeholder="e.g. Dishonor of Cheque No. 884932"
                value={formData.shortSubject}
                onChange={(e) => setFormData({...formData, shortSubject: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Date of Incident</label>
              <input
                type="date"
                required
                value={formData.dateOfIncident}
                onChange={(e) => setFormData({...formData, dateOfIncident: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-black/60 mb-2">Core Grievance / Facts</label>
              <textarea
                required
                rows={4}
                placeholder="Briefly describe the breach of trust, unpaid dues, or other dispute..."
                value={formData.grievance}
                onChange={(e) => setFormData({...formData, grievance: e.target.value})}
                className="w-full bg-[#FDFBF7] border border-black/10 p-3 text-sm focus:outline-none focus:border-[#D34343] rounded-sm resize-none"
              />
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className="w-full mt-4 bg-[#D34343] hover:bg-[#1A1A1A] text-white font-bold tracking-widest uppercase text-[11px] py-4 rounded-sm transition-all flex justify-center items-center gap-2"
            >
              {isGenerating ? <><Loader2 size={14} className="animate-spin" /> Drafting...</> : <><Scale size={14} /> Generate Draft</>}
            </button>
          </form>
        </div>

        {/* RIGHT PANEL: The Document Editor/Preview */}
        <div className="w-2/3 bg-[#FDFBF7] p-8 overflow-y-auto flex justify-center">
          {generatedDoc ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              className="w-full max-w-3xl bg-white shadow-xl border border-black/5 p-12 min-h-[800px]"
            >
              <div className="flex items-center gap-2 mb-6 text-green-600 bg-green-50 px-3 py-2 text-[10px] font-bold uppercase tracking-widest w-max rounded-sm">
                <CheckCircle size={14} /> Document Drafted Successfully
              </div>

              <textarea
                value={generatedDoc}
                onChange={(e) => setGeneratedDoc(e.target.value)}
                className="w-full h-full min-h-[700px] font-serif text-[15px] leading-relaxed focus:outline-none resize-none bg-transparent"
              />
            </motion.div>
          ) : (
            <div className="w-full max-w-3xl border-2 border-dashed border-black/10 flex flex-col items-center justify-center text-center p-10 min-h-[800px]">
                <FileText size={48} className="text-black/10 mb-4" />
                <h3 className="text-lg font-serif font-bold text-black/40 mb-2">Document Preview</h3>
                <p className="text-sm text-black/30 max-w-md">Fill out the intake form on the left and click "Generate Draft" to create your formal legal document.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
