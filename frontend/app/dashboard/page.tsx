"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import axios from "axios";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, RadialBarChart, RadialBar, Legend,
} from "recharts";
import { Brain, MessageCircle, TrendingUp, Activity, Star, ArrowLeft } from "lucide-react";

const API     = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const USER_ID = typeof window !== "undefined" ? (localStorage.getItem("mindcare_uid") || "guest_demo") : "guest_demo";

// No more hardcoded MOCK data. Using dynamic fallback empty states directly in components.

// ── Radial Gauge ──────────────────────────────────────────────────────────────
function BurnoutGauge({ score }: { score: number }) {
  const color =
    score > 65 ? "#ef4444" : score > 35 ? "#f59e0b" : "#3ecf8e";
  const r = 70, cx = 90, cy = 90;
  const circ = 2 * Math.PI * r;
  const dash = circ * 0.75;
  const filled = dash * (score / 100);
  const empty  = dash - filled;

  return (
    <div className="flex flex-col items-center">
      <svg width="180" height="150" viewBox="0 0 180 180">
        {/* Track */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none" stroke="var(--border)" strokeWidth="12"
          strokeDasharray={`${dash} ${circ - dash}`}
          strokeDashoffset={circ * 0.125}
          strokeLinecap="round"
        />
        {/* Fill */}
        <circle
          cx={cx} cy={cy} r={r}
          fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={`${filled} ${empty + circ * 0.25}`}
          strokeDashoffset={circ * 0.125}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 1s ease, stroke 0.5s ease" }}
        />
        <text x={cx} y={cy - 5} textAnchor="middle" fill={color} fontSize="26" fontWeight="700">
          {score.toFixed(0)}
        </text>
        <text x={cx} y={cy + 16} textAnchor="middle" fill="var(--text-secondary)" fontSize="12">
          / 100
        </text>
      </svg>
      <p className="text-sm font-medium" style={{ color }}>
        {score > 65 ? "High Burnout Risk" : score > 35 ? "Moderate Risk" : "Low Risk"}
      </p>
    </div>
  );
}

// ── Custom tooltip ────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-xl px-4 py-3 text-xs">
      <p className="font-semibold mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>
           {p.name}: {p.name === "stress" ? (p.value === 3 ? "High" : p.value === 2 ? "Moderate" : "Low") : p.value}
        </p>
      ))}
    </div>
  );
};

// ── Stat Card ─────────────────────────────────────────────────────────────────
function StatCard({
  icon: Icon, label, value, sub, color,
}: {
  icon: React.ElementType; label: string; value: string; sub?: string; color: string;
}) {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: `${color}20`, border: `1px solid ${color}40` }}
        >
          <Icon className="w-4.5 h-4.5" style={{ color, width: 18, height: 18 }} />
        </div>
        <span className="text-sm" style={{ color: "var(--text-secondary)" }}>{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>{sub}</p>}
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [burnout, setBurnout] = useState(0);
  const [stressLabel, setStressLabel] = useState("Unknown");
  const [trendData, setTrendData] = useState<any[]>([]);
  const [emotionsData, setEmotionsData] = useState<any[]>([]);
  const [totalSessions, setTotalSessions] = useState(0);
  const [avgMood, setAvgMood] = useState("Unknown");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [recRes, histRes] = await Promise.all([
          axios.get(`${API}/recommend?user_id=${USER_ID}`).catch(() => null),
          axios.get(`${API}/history/${USER_ID}`).catch(() => null)
        ]);

        if (recRes && recRes.data.recommendations?.length > 0) {
          setRecommendations(recRes.data.recommendations);
        } else {
          setRecommendations([]);
        }

        if (histRes && histRes.data) {
          const preds = histRes.data.predictions || [];
          const msgs = histRes.data.messages || [];

          if (preds.length > 0) {
            setBurnout(preds[0].burnout_score || 0);
            setStressLabel(preds[0].stress_level || "Unknown");
            
            const chartData = preds.slice(0, 7).reverse().map((p: any) => ({
              day: new Date(p.created_at).toLocaleDateString("en-US", { weekday: 'short' }),
              burnout: Math.round(p.burnout_score || 0),
              stress: p.stress_level === "High" ? 3 : p.stress_level === "Moderate" ? 2 : 1
            }));
            setTrendData(chartData);
          }

          if (msgs.length > 0) {
            setTotalSessions(msgs.length);
            const counts: Record<string, number> = { "Anxious": 0, "Neutral": 0, "Sad": 0, "Angry": 0, "Joy": 0 };
            let hasEmotions = false;
            
            msgs.forEach((m: any) => {
              if (m.emotion) {
                const cap = m.emotion.charAt(0).toUpperCase() + m.emotion.slice(1);
                if (counts[cap] !== undefined) {
                  counts[cap]++;
                  hasEmotions = true;
                }
              }
            });

            if (hasEmotions) {
              const topEmotion = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
              setAvgMood(topEmotion);
              
              setEmotionsData([
                { name: "Anxious", value: counts["Anxious"] || 0, fill: "#f59e0b" },
                { name: "Neutral", value: counts["Neutral"] || 0, fill: "#5b8dee" },
                { name: "Sad",     value: counts["Sad"] || 0,     fill: "#7c6fdf" },
                { name: "Angry",   value: counts["Angry"] || 0,   fill: "#ef4444" },
                { name: "Joy",     value: counts["Joy"] || 0,     fill: "#3ecf8e" },
              ]);
            }
          }
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (typeof window !== "undefined") {
      fetchData();
    }
  }, []);

  const catColors: Record<string, string> = {
    Breathing: "#5b8dee",
    Study:     "#7c6fdf",
    Mental:    "#3ecf8e",
    Physical:  "#f59e0b",
    Sleep:     "#a78bfa",
    Social:    "#ec4899",
    Lifestyle: "#6ee7b7",
  };



  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto" style={{ background: "var(--bg-primary)" }}>
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
            Wellness <span className="gradient-text">Dashboard</span>
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
            Your stress & burnout analytics at a glance
          </p>
        </div>
        <Link
          href="/chat"
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
          style={{ background: "linear-gradient(135deg, #7c6fdf, #5b8dee)" }}
        >
          <MessageCircle className="w-4 h-4" /> Open Chat
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard icon={Activity}   label="Stress Level"   value={stressLabel}  sub="Current session"    color="#f59e0b" />
        <StatCard icon={TrendingUp} label="Burnout Score"  value={`${Math.round(burnout)} / 100`}     sub="Latest tracked result" color="#ef4444" />
        <StatCard icon={Brain}      label="Sessions"       value={String(totalSessions)}            sub="All time messages"          color="#7c6fdf" />
        <StatCard icon={Star}       label="Avg. Mood"      value={avgMood}     sub="Based on emotions"  color="#3ecf8e" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
        {/* Burnout Gauge */}
        <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center">
          <h2 className="text-base font-semibold mb-4 self-start">Burnout Risk</h2>
          <BurnoutGauge score={burnout} />
        </div>

        {/* Trend Line */}
        <div className="glass rounded-2xl p-6 lg:col-span-2">
          <h2 className="text-base font-semibold mb-4">7-Day Burnout Trend</h2>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={trendData}>
                <defs>
                  <linearGradient id="burnoutGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"   stopColor="#7c6fdf" stopOpacity={0.4} />
                    <stop offset="95%"  stopColor="#7c6fdf" stopOpacity={0}   />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="day" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: "var(--text-secondary)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone" dataKey="burnout" stroke="#7c6fdf" strokeWidth={2.5}
                  dot={{ fill: "#7c6fdf", r: 4 }} activeDot={{ r: 6, stroke: "#fff" }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-sm" style={{ color: "var(--text-secondary)" }}>
              No history tracked yet. Chat with MindCare to start your chart!
            </div>
          )}
        </div>
      </div>

      {/* Emotion Bar + Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        {/* Emotion Distribution */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-base font-semibold mb-4">Emotion Distribution</h2>
          {emotionsData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={emotionsData} layout="vertical" barSize={14}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                <XAxis type="number" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} axisLine={false} tickLine={false} width={55} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]}>
                  {emotionsData.map((e, i) => (
                    <rect key={i} fill={e.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-sm" style={{ color: "var(--text-secondary)" }}>
              Not enough data yet.
            </div>
          )}
        </div>

        {/* Recommendations */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-base font-semibold mb-4">Recommended for You</h2>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-14 rounded-xl animate-pulse"
                  style={{ background: "var(--border)" }}
                />
              ))}
            </div>
          ) : recommendations.length > 0 ? (
            <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
              {recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 rounded-xl transition-colors"
                  style={{ background: "var(--bg-input)" }}
                >
                  <div
                    className="px-2 py-0.5 rounded-md text-xs font-medium flex-shrink-0 mt-0.5"
                    style={{
                      background: `${catColors[rec.category] || "#7c6fdf"}20`,
                      color: catColors[rec.category] || "#7c6fdf",
                    }}
                  >
                    {rec.category}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{rec.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>{rec.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm" style={{ color: "var(--text-secondary)" }}>No recommendations available yet. Chat with MindCare to get personalized suggestions.</div>
          )}
        </div>
      </div>

      {/* Real-time Monitoring Notice */}
      <div
        className="glass rounded-2xl p-5 flex items-center gap-4"
        style={{ border: "1px solid rgba(124,111,223,0.3)" }}
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: "rgba(124,111,223,0.15)" }}
        >
          <Activity className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <p className="text-sm font-semibold">Real-time Monitoring Active</p>
          <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
            Your stress and emotion data updates automatically as you chat. Charts refresh every session.
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2 flex-shrink-0">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>Live</span>
        </div>
      </div>
    </div>
  );
}
