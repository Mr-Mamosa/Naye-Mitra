"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Scale, Mail, Lock, User, ArrowRight, Loader2, AlertCircle, Briefcase } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();

  // Form Toggle State
  const [isLogin, setIsLogin] = useState(true);

  // Input States
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [accountType, setAccountType] = useState("citizen"); // NEW: Role state

  // UI States
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Form Validation & Submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // 1. Basic Frontend Validation
    if (!email.includes("@") || !email.includes(".")) {
      setError("Please enter a valid email address.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }
    if (!isLogin) {
      if (name.trim().length < 2) {
        setError("Please enter your full name.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    setIsLoading(true);

    try {
      // 2. SIMULATED BACKEND CALL
      // In production, your FastAPI backend would return the user's role upon login.
      await new Promise(resolve => setTimeout(resolve, 1500));

      // 3. Set the LocalStorage Token
      // If logging in (simulation), we check the email to mock a role, otherwise use the signup role
      let assignedRole = accountType;
      if (isLogin) {
        assignedRole = email.includes("advocate") ? "admin" : "user";
      } else {
        assignedRole = accountType === "advocate" ? "admin" : "user";
      }

      localStorage.setItem("lawgpt_role", assignedRole);
      localStorage.setItem("lawgpt_user", isLogin ? email : name);

      // 4. Redirect to the main app
      router.push("/workspace");

    } catch (err) {
      setError("Failed to authenticate. Please check your network connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)] flex items-center justify-center p-4 overflow-hidden relative transition-colors duration-300">

      {/* Background Aesthetic */}
      <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[var(--primary)] opacity-10 dark:opacity-20 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[var(--primary)] opacity-5 dark:opacity-10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Main Auth Card */}
      <div className="w-full max-w-md bg-[var(--background)] border border-[var(--border-color)] rounded-2xl shadow-2xl overflow-hidden z-10">

        {/* Header Section */}
        <div className="p-8 border-b border-[var(--border-color)] text-center bg-white/50 dark:bg-black/20">
          <Link href="/" className="inline-flex items-center gap-2 mb-6 hover:opacity-80 transition-opacity">
            <Scale className="text-[var(--primary)]" size={28} />
            <span className="font-bold tracking-[0.2em] text-xl uppercase text-[var(--foreground)]">Law-GPT</span>
          </Link>
          <h2 className="text-2xl font-bold text-[var(--foreground)] tracking-tight">
            {isLogin ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="text-sm text-[var(--muted-foreground)] mt-2 leading-relaxed">
            {isLogin
              ? "Sign in to access your personal legal workspace and chat history."
              : "Join Law-GPT to access deterministic legal analysis and drafting tools."}
          </p>
        </div>

        {/* Form Section */}
        <div className="p-8">

          {/* Error Banner */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-6 overflow-hidden"
              >
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3 text-red-600 dark:text-red-400 text-sm font-medium">
                  <AlertCircle size={16} className="shrink-0" />
                  <p>{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">

            <AnimatePresence mode="popLayout">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-4"
                >
                  {/* NEW: Account Type Selector */}
                  <div>
                    <label className="block text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-1.5 ml-1">Profile Type</label>
                    <div className="relative">
                      <Briefcase size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] pointer-events-none" />
                      <select
                        value={accountType}
                        onChange={(e) => setAccountType(e.target.value)}
                        className="w-full bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all text-sm appearance-none cursor-pointer"
                      >
                        <option value="citizen">Citizen (General User)</option>
                        <option value="student">Law Student</option>
                        <option value="advocate">Verified Advocate</option>
                      </select>
                      {/* Custom dropdown arrow */}
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[var(--muted-foreground)] text-xs">▼</div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-1.5 ml-1">Full Name</label>
                    <div className="relative">
                      <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]" />
                      <input
                        type="text"
                        placeholder={accountType === "advocate" ? "Adv. Ramesh Kumar" : "Ramesh Kumar"}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all text-sm"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-1.5 ml-1">Email Address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]" />
                <input
                  type="email"
                  placeholder={!isLogin && accountType === "advocate" ? "advocate@lawfirm.com" : "user@example.com"}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all text-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-1.5 ml-1">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all text-sm"
                />
              </div>
            </div>

            <AnimatePresence mode="popLayout">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  <label className="block text-[10px] font-bold tracking-widest uppercase text-[var(--muted-foreground)] mb-1.5 ml-1">Confirm Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]" />
                    <input
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full bg-[var(--background)] border border-[var(--border-color)] text-[var(--foreground)] rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:border-[var(--primary)] focus:ring-1 focus:ring-[var(--primary)] transition-all text-sm"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 bg-[var(--primary)] hover:opacity-90 text-white rounded-xl py-3.5 text-xs font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-70"
            >
              {isLoading ? (
                <><Loader2 size={16} className="animate-spin" /> Authenticating...</>
              ) : (
                <>{isLogin ? "Secure Login" : "Create Account"} <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          {/* Toggle Login/Signup */}
          <div className="mt-8 text-center border-t border-[var(--border-color)] pt-6">
            <p className="text-xs text-[var(--muted-foreground)]">
              {isLogin ? "Don't have an account?" : "Already have an account?"}
            </p>
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError(null);
                setPassword("");
                setConfirmPassword("");
              }}
              className="mt-2 text-sm font-bold text-[var(--foreground)] hover:text-[var(--primary)] transition-colors"
            >
              {isLogin ? "Create a Workspace" : "Sign in instead"}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
