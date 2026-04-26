"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import axios from "axios";
import { ArrowLeft, Clock, MessageCircle } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const USER_ID = typeof window !== "undefined" ? (localStorage.getItem("mindcare_uid") || "guest_demo") : "guest_demo";

const EMOTION_EMOJI: Record<string, string> = {
  anxious: "😰",
  sad:     "😔",
  angry:   "😤",
  neutral: "😐",
  joy:     "😊",
};

const STRESS_COLOR: Record<string, string> = {
  Low:      "stress-low",
  Moderate: "stress-moderate",
  High:     "stress-high",
};

export default function HistoryPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API}/history/${USER_ID}`);
        if (res.data?.messages) {
          const msgs = [...res.data.messages].reverse(); 
          setMessages(res.data.messages);
        }
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoading(false);
      }
    };
    if (typeof window !== "undefined") {
      fetchHistory();
    }
  }, []);

  return (
    <div className="min-h-screen p-6 max-w-4xl mx-auto" style={{ background: "var(--bg-primary)" }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link
            href="/"
            className="flex items-center gap-1.5 text-sm mb-2 transition-colors hover:text-white"
            style={{ color: "var(--text-secondary)" }}
          >
            <ArrowLeft className="w-4 h-4" /> Home
          </Link>
          <h1 className="text-3xl font-bold">
            Chat <span className="gradient-text">History</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
            Review past conversations and wellness tracking
          </p>
        </div>
        <Link
          href="/chat"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
          style={{ background: "linear-gradient(135deg, #7c6fdf, #5b8dee)" }}
        >
          <MessageCircle className="w-4 h-4" /> Return to Chat
        </Link>
      </div>

      {/* Timeline */}
      <div className="glass rounded-2xl p-6">
        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 rounded-xl animate-pulse" style={{ background: "var(--bg-input)" }} />
            ))}
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-12 text-sm" style={{ color: "var(--text-secondary)" }}>
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No chat history found for this session.</p>
            <Link href="/chat" className="text-purple-400 mt-2 block hover:underline">Start a conversation</Link>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl flex flex-col sm:flex-row gap-4"
                style={{ background: msg.role === 'user' ? "var(--bg-input)" : "rgba(124,111,223,0.1)", border: "1px solid var(--border)" }}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider" style={{ color: msg.role === 'user' ? "#3ecf8e" : "#5b8dee" }}>
                      {msg.role}
                    </span>
                    <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                      {new Date(msg.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--text-primary)" }}>
                    {msg.content}
                  </p>
                </div>
                {msg.role === 'user' && (msg.emotion || msg.stress_level) && (
                  <div className="flex sm:flex-col items-end justify-center gap-2 flex-shrink-0">
                    {msg.emotion && (
                      <span className="text-xs px-2.5 py-1 rounded-md glass font-medium capitalize flex items-center gap-1.5" style={{ color: "var(--text-secondary)" }}>
                        {EMOTION_EMOJI[msg.emotion] || "🔵"} {msg.emotion}
                      </span>
                    )}
                    {msg.stress_level && (
                      <span className={`text-xs px-2.5 py-1 rounded-md bg-stress-${msg.stress_level.toLowerCase()} ${STRESS_COLOR[msg.stress_level]} font-medium capitalize`}>
                         Stress: {msg.stress_level}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
