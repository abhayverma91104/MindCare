"use client";

import Link from "next/link";
import { Brain, MessageCircle, BarChart3, Shield, Zap, Heart } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Stress Detection",
    desc: "ML models (Random Forest, SVM, LSTM) analyze your responses to detect stress and burnout with precision.",
    color: "text-purple-400",
    bg: "bg-purple-400/10",
  },
  {
    icon: MessageCircle,
    title: "Gemini-Powered Chatbot",
    desc: "Context-aware conversations with system-prompt engineering, rolling memory, and personality modes.",
    color: "text-blue-400",
    bg: "bg-blue-400/10",
  },
  {
    icon: BarChart3,
    title: "Burnout Dashboard",
    desc: "Real-time visualizations of stress levels, burnout risk scores, and emotional trends over time.",
    color: "text-green-400",
    bg: "bg-green-400/10",
  },
  {
    icon: Shield,
    title: "Crisis Safety Layer",
    desc: "Automatic detection of distress signals with instant crisis helpline routing and emergency override.",
    color: "text-red-400",
    bg: "bg-red-400/10",
  },
  {
    icon: Zap,
    title: "Personal Recommendations",
    desc: "Coping strategies tailored to your stress level, emotional state, and interaction history.",
    color: "text-amber-400",
    bg: "bg-amber-400/10",
  },
  {
    icon: Heart,
    title: "Multilingual Support",
    desc: "Seamless communication in your native language — MindCare adapts automatically.",
    color: "text-pink-400",
    bg: "bg-pink-400/10",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen" style={{ background: "var(--bg-primary)" }}>
      {/* Navbar */}
      <nav
        className="glass sticky top-0 z-50 px-8 py-5 flex items-center justify-between"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-purple-400" />
          <span className="text-2xl font-bold gradient-text">MindCare</span>
        </div>
        <div className="flex gap-4 items-center">
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:text-white"
            style={{ color: "var(--text-secondary)" }}
          >
            Dashboard
          </Link>
          <Link
            href="/chat"
            className="px-6 py-2.5 rounded-full text-sm font-semibold text-white transition-all duration-300 shadow-xl hover:-translate-y-0.5"
            style={{
              background: "linear-gradient(135deg, #7c6fdf, #5b8dee)",
            }}
          >
            Start Chat
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center px-6 pt-32 pb-24 text-center overflow-hidden">
        {/* Glow blobs */}
        <div
          className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: "radial-gradient(circle, #7c6fdf, transparent 70%)" }}
        />
        <div
          className="absolute top-40 right-1/4 w-[400px] h-[400px] rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: "radial-gradient(circle, #5b8dee, transparent 70%)" }}
        />

        <div
          className="mb-8 inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs font-semibold uppercase tracking-wider"
          style={{ background: "rgba(124,111,223,0.1)", border: "1px solid rgba(124,111,223,0.2)", color: "#a89ff0" }}
        >
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          AI-Powered Mental Wellness
        </div>

        <h1 className="text-6xl md:text-8xl font-bold tracking-tight leading-[1.1] mb-8 max-w-5xl">
          Detect Stress.{" "}
          <span className="gradient-text">Beat Burnout.</span>{" "}
          <br />Feel Better.
        </h1>
        <p
          className="text-xl md:text-2xl font-light max-w-3xl mb-12 leading-relaxed"
          style={{ color: "var(--text-secondary)" }}
        >
          MindCare combines machine learning stress analysis with an empathetic chatbot — your 24/7 mental health companion, built for{" "}
          <em>students, by AI</em>.
        </p>

        <div className="flex flex-col sm:flex-row gap-6 items-center justify-center">
          <Link
            href="/chat"
            className="px-10 py-5 rounded-2xl text-lg font-semibold text-white transition-transform duration-300 hover:scale-[1.02]"
            style={{
              background: "linear-gradient(135deg, #7c6fdf, #5b8dee)",
              boxShadow: "0 10px 40px rgba(124,111,223,0.4)",
            }}
          >
            Talk to MindCare →
          </Link>
          <Link
            href="/dashboard"
            className="px-10 py-5 rounded-2xl text-lg font-medium transition-all duration-300 hover:bg-white/5"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              color: "var(--text-primary)",
            }}
          >
            View Dashboard
          </Link>
        </div>

        {/* Stats */}
        <div className="mt-32 grid grid-cols-3 gap-12 max-w-3xl mx-auto items-center justify-center">
          {[
            { value: "5", label: "Emotion Classes" },
            { value: "3+", label: "ML Models" },
            { value: "100%", label: "Private & Secure" },
          ].map((s) => (
            <div key={s.label} className="flex flex-col items-center justify-center text-center space-y-2">
              <div className="text-4xl lg:text-5xl font-extrabold gradient-text">{s.value}</div>
              <div className="text-sm font-medium uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features - Symmetrical Layout */}
      <section className="px-8 py-32 max-w-7xl mx-auto flex flex-col items-center">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-6 tracking-tight">
          Everything you need to <span className="gradient-text">thrive</span>
        </h2>


        {/* Uniform Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full auto-rows-[280px]">
          {features.map((f) => (
            <div
              key={f.title}
              className="glass rounded-3xl p-10 flex flex-col justify-center items-center text-center transition-all duration-500 hover:-translate-y-2 group h-full"
              style={{ cursor: "default" }}
            >
              <div className={`w-16 h-16 rounded-2xl ${f.bg} flex items-center justify-center mb-6 shrink-0 transition-transform duration-500 group-hover:scale-110`}>
                <f.icon className={`w-8 h-8 ${f.color}`} />
              </div>
              <h3 className="font-bold text-2xl tracking-tight mb-3 text-white/95">{f.title}</h3>
              <p className="text-base font-light leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-8 py-32 flex flex-col items-center justify-center text-center w-full">
        <div
          className="glass rounded-[3rem] p-16 max-w-4xl w-full flex flex-col items-center justify-center mx-auto"
          style={{ background: "linear-gradient(135deg, rgba(124,111,223,0.08), rgba(91,141,238,0.08))" }}
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6 text-center tracking-tight">
            Ready to take care of your{" "}
            <span className="gradient-text">mind</span>?
          </h2>
          <p className="mb-12 text-lg text-center max-w-lg font-light" style={{ color: "var(--text-secondary)" }}>
            Start a natural conversation. It's completely free, highly private, and always available.
          </p>
          <Link
            href="/chat"
            className="px-12 py-8 rounded-full text-lg font-bold text-white inline-flex items-center justify-center transition-all duration-300 hover:scale-105"
            style={{
              background: "linear-gradient(135deg, #7c6fdf, #5b8dee)",
              boxShadow: "0 10px 40px rgba(124,111,223,0.4)",
            }}
          >
            Begin Your Journey →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="px-6 py-8 flex flex-col items-center justify-center text-center text-xs w-full"
        style={{ color: "var(--text-secondary)", borderTop: "1px solid var(--border)" }}
      >
        <p>MindCare © 2026 · Built with 🫶🏻 by Abhay and Guneet</p>
        <p className="mt-1">Not a substitute for professional mental health care. Crisis line: 9152987821</p>
      </footer>
    </main>
  );
}
