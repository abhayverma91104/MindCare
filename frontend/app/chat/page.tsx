"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import axios from "axios";
import {
  Brain, Send, Settings, BarChart3, AlertTriangle,
  User, Bot, RefreshCw, Mic, Clock
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const USER_ID = typeof window !== "undefined"
  ? (localStorage.getItem("mindcare_uid") || (() => {
    const uid = "guest_" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("mindcare_uid", uid);
    return uid;
  })())
  : "guest_ssr";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  emotion?: string;
  stress_level?: string;
  crisis?: boolean;
  ts: number;
};

const EMOTION_EMOJI: Record<string, string> = {
  anxious: "😰",
  sad: "😔",
  angry: "😤",
  neutral: "😐",
  joy: "😚",
};

const STRESS_COLOR: Record<string, string> = {
  Low: "stress-low",
  Moderate: "stress-moderate",
  High: "stress-high",
};

const PERSONALITIES = [
  { value: "calm", label: "🧘 Calm", desc: "Gentle & grounding" },
  { value: "coach", label: "🏆 Coach", desc: "Motivational" },
  { value: "listener", label: "👂 Listener", desc: "Empathetic" },
];

const LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Bengali", "Tamil", "Telugu", "Marathi"];

function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 animate-fade-in-up">
      <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ background: "linear-gradient(135deg, #7c6fdf, #5b8dee)" }}>
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="glass rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}

function ChatBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex items-end gap-3 animate-fade-in-up ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{
          background: isUser
            ? "linear-gradient(135deg, #3ecf8e, #5b8dee)"
            : "linear-gradient(135deg, #7c6fdf, #5b8dee)",
        }}
      >
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      {/* Bubble */}
      <div className="max-w-[75%]">
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${isUser
              ? "rounded-br-sm text-white"
              : "glass rounded-bl-sm"
            } ${msg.crisis ? "border border-red-500/40" : ""}`}
          style={{
            background: isUser
              ? "linear-gradient(135deg, #7c6fdf, #5b8dee)"
              : undefined,
          }}
        >
          {msg.crisis && (
            <div className="flex items-center gap-1.5 mb-2 text-red-400 text-xs font-medium">
              <AlertTriangle className="w-3.5 h-3.5" />
              Crisis support activated
            </div>
          )}
          {msg.content}
        </div>

        {/* Meta */}
        {!isUser && (msg.emotion || msg.stress_level) && (
          <div className="flex gap-2 mt-1.5 ml-1">
            {msg.emotion && (
              <span
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ background: "var(--bg-input)", color: "var(--text-secondary)" }}
              >
                {EMOTION_EMOJI[msg.emotion] || "🔵"} {msg.emotion}
              </span>
            )}
            {msg.stress_level && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${STRESS_COLOR[msg.stress_level]} bg-stress-${msg.stress_level?.toLowerCase()}`}>
                {msg.stress_level} stress
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [personality, setPersonality] = useState("calm");
  const [language, setLanguage] = useState("English");
  const [showSettings, setShowSettings] = useState(false);
  const [stressLevel, setStressLevel] = useState<string>("");
  const [burnoutScore, setBurnoutScore] = useState<number | null>(null);
  const [currentEmotion, setCurrentEmotion] = useState<string>("");

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const greeting: Message = {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm MindCare 🌿 — your AI mental wellness companion. I'm here to listen, support, and help you navigate stress and burnout.\n\nHow are you feeling today?",
      ts: Date.now(),
    };

    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API}/history/${USER_ID}`);
        let loadedMsgs: Message[] = [];
        if (res.data?.messages?.length > 0) {
          loadedMsgs = res.data.messages.map((m: any) => ({
            id: String(m.id || Math.random()),
            role: m.role,
            content: m.content,
            emotion: m.emotion,
            stress_level: m.stress_level,
            crisis: m.crisis_flag,
            ts: new Date(m.created_at).getTime()
          }));
          const lastMsg = loadedMsgs[loadedMsgs.length - 1];
          if (lastMsg.emotion) setCurrentEmotion(lastMsg.emotion);
          if (lastMsg.stress_level) setStressLevel(lastMsg.stress_level);
        }

        if (loadedMsgs.length > 0) {
          setMessages([greeting, ...loadedMsgs]);
        } else {
          setMessages([greeting]);
        }

        if (res.data?.predictions?.length > 0) {
          const lastPred = res.data.predictions[0];
          if (lastPred.burnout_score !== undefined) setBurnoutScore(lastPred.burnout_score);
          if (lastPred.stress_level) setStressLevel(lastPred.stress_level);
        }
      } catch (err) {
        console.error("Failed to load history", err);
        setMessages([greeting]);
      }
    };

    if (typeof window !== "undefined") {
      fetchHistory();
    }
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userText = input.trim();
    setInput("");

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: userText,
      ts: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await axios.post(`${API}/chat`, {
        user_id: USER_ID,
        message: userText,
        personality,
        language,
      });
      const data = res.data;
      const botMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        emotion: data.emotion,
        stress_level: data.stress_level,
        crisis: data.crisis,
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, botMsg]);
      if (data.stress_level) setStressLevel(data.stress_level);
      if (data.burnout_score !== undefined) setBurnoutScore(data.burnout_score);
      if (data.emotion) setCurrentEmotion(data.emotion);
    } catch (err: unknown) {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "I'm having trouble connecting right now. Please check that the backend server is running and try again.",
        ts: Date.now(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, personality, language]);

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setStressLevel("");
    setBurnoutScore(null);
    setCurrentEmotion("");
  };

  return (
    <div className="flex h-screen" style={{ background: "var(--bg-primary)" }}>
      {/* ── Sidebar ──────────────────────────────────────────── */}
      <aside
        className="w-64 flex-shrink-0 flex flex-col glass"
        style={{ borderRight: "1px solid var(--border)" }}
      >
        {/* Logo */}
        <div className="p-5 flex items-center gap-2" style={{ borderBottom: "1px solid var(--border)" }}>
          <Brain className="w-6 h-6 text-purple-400" />
          <span className="font-semibold gradient-text">MindCare</span>
        </div>

        {/* Live Context */}
        <div className="p-4 space-y-4 flex-1">
          <p className="text-xs font-medium uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
            Live Context
          </p>

          {/* Stress */}
          <div className="glass rounded-xl p-3">
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Stress Level</p>
            <p className={`font-semibold text-lg ${stressLevel ? STRESS_COLOR[stressLevel] : ""}`}>
              {stressLevel || "—"}
            </p>
          </div>

          {/* Burnout */}
          <div className="glass rounded-xl p-3">
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Burnout Score</p>
            <div className="flex items-end gap-1">
              <span className="font-semibold text-lg">
                {burnoutScore !== null ? burnoutScore.toFixed(0) : "—"}
              </span>
              {burnoutScore !== null && (
                <span className="text-xs mb-0.5" style={{ color: "var(--text-secondary)" }}>/100</span>
              )}
            </div>
            {burnoutScore !== null && (
              <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
                <div
                  className="h-full rounded-full transition-all duration-1000"
                  style={{
                    width: `${burnoutScore}%`,
                    background:
                      burnoutScore > 65
                        ? "var(--accent-red)"
                        : burnoutScore > 35
                          ? "var(--accent-amber)"
                          : "var(--accent-green)",
                  }}
                />
              </div>
            )}
          </div>

          {/* Emotion */}
          <div className="glass rounded-xl p-3">
            <p className="text-xs mb-1" style={{ color: "var(--text-secondary)" }}>Emotion</p>
            <p className="font-semibold capitalize">
              {currentEmotion ? `${EMOTION_EMOJI[currentEmotion]} ${currentEmotion}` : "—"}
            </p>
          </div>

          {/* Personality */}
          <div>
            <p className="text-xs font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Personality Mode</p>
            <div className="space-y-1.5">
              {PERSONALITIES.map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPersonality(p.value)}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all duration-200"
                  style={{
                    background: personality === p.value ? "rgba(124,111,223,0.15)" : "transparent",
                    border: personality === p.value ? "1px solid rgba(124,111,223,0.4)" : "1px solid transparent",
                    color: personality === p.value ? "#a89ff0" : "var(--text-secondary)",
                  }}
                >
                  <span>{p.label}</span>
                  {personality === p.value && <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />}
                </button>
              ))}
            </div>
          </div>

          {/* Language */}
          <div>
            <p className="text-xs font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Language</p>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm chat-input"
            >
              {LANGUAGES.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Nav Links */}
        <div className="p-4 space-y-1" style={{ borderTop: "1px solid var(--border)" }}>
          <Link
            href="/history"
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors hover:text-white"
            style={{ color: "var(--text-secondary)" }}
          >
            <Clock className="w-4 h-4" /> History
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors hover:text-white"
            style={{ color: "var(--text-secondary)" }}
          >
            <BarChart3 className="w-4 h-4" /> Dashboard
          </Link>
          <button
            onClick={clearChat}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors w-full text-left hover:text-white"
            style={{ color: "var(--text-secondary)" }}
          >
            <RefreshCw className="w-4 h-4" /> New Chat
          </button>
        </div>
      </aside>

      {/* ── Main Chat Area ───────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div
          className="px-6 py-4 flex items-center justify-between glass"
          style={{ borderBottom: "1px solid var(--border)" }}
        >
          <div>
            <h1 className="font-semibold">Chat with MindCare</h1>
            <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
              Mode: {PERSONALITIES.find((p) => p.value === personality)?.label} · {language}
            </p>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Online</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {messages.map((msg) => (
            <ChatBubble key={msg.id} msg={msg} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="px-6 py-4 glass" style={{ borderTop: "1px solid var(--border)" }}>
          <div
            className="flex items-end gap-3 rounded-2xl p-3 pr-4"
            style={{ background: "var(--bg-input)", border: "1px solid var(--border)" }}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Share what's on your mind… (Enter to send, Shift+Enter for newline)"
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm outline-none leading-relaxed max-h-40"
              style={{ color: "var(--text-primary)", fontFamily: "inherit" }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 flex-shrink-0"
              style={{
                background:
                  input.trim() && !loading
                    ? "linear-gradient(135deg, #7c6fdf, #5b8dee)"
                    : "var(--border)",
                opacity: !input.trim() || loading ? 0.5 : 1,
              }}
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </div>
          <p className="text-xs mt-2 text-center" style={{ color: "var(--text-secondary)" }}>
            MindCare is not a substitute for professional medical advice. Crisis line: 9152987821
          </p>
        </div>
      </main>
    </div>
  );
}
