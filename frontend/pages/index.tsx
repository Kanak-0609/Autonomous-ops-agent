import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth, useUser, RedirectToSignIn, UserButton } from "@clerk/nextjs";
import Link from "next/link";

interface Metrics {
  total_processed: number;
  triaged: number;
  drafted: number;
  approved: number;
  sent: number;
  rejected: number;
  skipped: number;
  unique_senders: number;
  eval_accuracy: string;
}

interface Interaction {
  id: number;
  sender_email: string;
  subject: string;
  classification: string;
  outcome: string;
  summary: string;
  timestamp: string;
}

const API_BASE = "http://localhost:8000";

const GLOW = {
  violet: "#8B7CF7",
  cyan: "#4DD8E8",
  amber: "#FBBF3D",
  mint: "#4ADE80",
  coral: "#FB7185",
};

const CLASS_STYLES: Record<string, { text: string; bg: string; border: string }> = {
  billing_question: { text: "#4DD8E8", bg: "rgba(77,216,232,0.1)", border: "rgba(77,216,232,0.3)" },
  new_inquiry: { text: "#8B7CF7", bg: "rgba(139,124,247,0.1)", border: "rgba(139,124,247,0.3)" },
  spam: { text: "#9397AC", bg: "rgba(147,151,172,0.1)", border: "rgba(147,151,172,0.3)" },
  other: { text: "#FBBF3D", bg: "rgba(251,191,61,0.1)", border: "rgba(251,191,61,0.3)" },
};

const OUTCOME_STYLES: Record<string, { text: string; bg: string; border: string }> = {
  sent: { text: "#4ADE80", bg: "rgba(74,222,128,0.1)", border: "rgba(74,222,128,0.3)" },
  rejected: { text: "#FB7185", bg: "rgba(251,113,133,0.1)", border: "rgba(251,113,133,0.3)" },
  skipped: { text: "#9397AC", bg: "rgba(147,151,172,0.1)", border: "rgba(147,151,172,0.3)" },
};

const STACK = ["Gemini", "Neon Postgres", "Custom MCP Server", "LangSmith"];

export default function Dashboard() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-[#05050A] flex items-center justify-center">
        <span className="font-[family-name:var(--font-body)] text-[#9397AC] text-sm">
          Checking session...
        </span>
      </div>
    );
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  return <DashboardContent />;
}

function DashboardContent() {
  const { user } = useUser();
  const [orgId, setOrgId] = useState<number | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function ensureOrg() {
      try {
        const res = await fetch("/api/ensure-org");
        const org = await res.json();
        setOrgId(org.id);
      } catch {
        setError("Could not set up your organization. Check the API route logs.");
        setLoading(false);
      }
    }
    ensureOrg();
  }, []);

  useEffect(() => {
    if (!orgId) return;

    async function loadData() {
      try {
        const [m, i] = await Promise.all([
          fetch(`${API_BASE}/api/metrics?organization_id=${orgId}`).then((r) => r.json()),
          fetch(`${API_BASE}/api/interactions?organization_id=${orgId}`).then((r) => r.json()),
        ]);
        setMetrics(m);
        setInteractions(i);
      } catch {
        setError("Could not connect to backend. Is uvicorn running on port 8000?");
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 8000);
    return () => clearInterval(interval);
  }, [orgId]);

  const stages = [
    { label: "Fetched", value: metrics?.total_processed ?? 0, color: GLOW.violet },
    { label: "Triaged", value: metrics?.triaged ?? 0, color: GLOW.cyan },
    { label: "Drafted", value: metrics?.drafted ?? 0, color: GLOW.amber },
    { label: "Approved", value: metrics?.approved ?? 0, color: GLOW.mint },
    { label: "Sent", value: metrics?.sent ?? 0, color: GLOW.mint },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050A] flex items-center justify-center">
        <span className="font-[family-name:var(--font-body)] text-[#9397AC] text-sm">
          Setting up your workspace...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#05050A] flex items-center justify-center px-6">
        <div className="text-center">
          <div className="font-[family-name:var(--font-display)] text-[#FB7185] text-lg font-bold mb-2">
            Connection failed
          </div>
          <div className="font-[family-name:var(--font-body)] text-[#9397AC] text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050A] text-[#F2F2F8] font-[family-name:var(--font-body)] relative overflow-hidden">

      <div
        className="pointer-events-none fixed inset-0 opacity-[0.035] mix-blend-overlay z-10"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />

      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[550px] h-[550px] rounded-full opacity-25 blur-[130px]" style={{ background: GLOW.violet }} />
        <div className="absolute top-1/3 -right-40 w-[550px] h-[550px] rounded-full opacity-20 blur-[130px]" style={{ background: GLOW.cyan }} />
        <div className="absolute bottom-0 left-1/4 w-[450px] h-[450px] rounded-full opacity-15 blur-[130px]" style={{ background: GLOW.amber }} />
      </div>

      <div className="relative max-w-5xl mx-auto px-6 py-14 md:px-10">

        <div className="flex items-end justify-between mb-6 flex-wrap gap-6">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: GLOW.mint }} />
                <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: GLOW.mint }} />
              </span>
              <span className="text-xs tracking-[0.15em] text-[#9397AC] uppercase">Live</span>
              <Link href="/settings" className="text-xs text-[#9397AC] hover:text-[#F2F2F8] transition-colors underline underline-offset-4">
                Settings
              </Link>
            <UserButton />
            </div>
            <h1 className="font-[family-name:var(--font-display)] text-4xl md:text-5xl font-bold tracking-tight mb-4">
              {user?.firstName ? `${user.firstName}'s Ops Agent` : "Autonomous Ops Agent"}
            </h1>
            <div className="flex flex-wrap gap-2">
              {STACK.map((s) => (
                <span
                  key={s}
                  className="text-[10px] tracking-wide text-[#9397AC] uppercase px-2.5 py-1 rounded-full border border-white/[0.08] bg-white/[0.03]"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          <div className="text-right">
            <div className="text-[10px] tracking-wider text-[#9397AC] uppercase mb-1">Total Processed</div>
            <motion.div
              key={metrics?.total_processed}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="font-[family-name:var(--font-display)] text-6xl md:text-7xl font-bold leading-none"
              style={{
                background: `linear-gradient(135deg, #F2F2F8, ${GLOW.violet})`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              {metrics?.total_processed ?? 0}
            </motion.div>
          </div>
        </div>

        <div className="relative rounded-3xl mb-6 p-8 md:p-10 backdrop-blur-xl bg-white/[0.035] border border-white/[0.08] shadow-[0_8px_40px_rgba(0,0,0,0.3)]">
          <div className="text-xs tracking-[0.15em] text-[#9397AC] uppercase mb-8">Pipeline</div>
          <div className="flex items-center justify-between">
            {stages.map((stage, idx) => (
              <div key={stage.label} className="flex items-center flex-1">
                <div className="flex flex-col items-center gap-3">
                  <div className="relative flex items-center justify-center">
                    <div
                      className="absolute w-20 h-20 rounded-full blur-2xl opacity-60"
                      style={{ background: stage.color }}
                    />
                    <motion.div
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      whileHover={{ scale: 1.08 }}
                      transition={{ delay: idx * 0.08, type: "spring" }}
                      className="relative w-16 h-16 rounded-full flex items-center justify-center backdrop-blur-md border-2 cursor-default"
                      style={{
                        background: `${stage.color}2A`,
                        borderColor: `${stage.color}88`,
                        boxShadow: `0 0 24px ${stage.color}55`,
                      }}
                    >
                      <span className="font-[family-name:var(--font-display)] text-xl font-bold">
                        {stage.value}
                      </span>
                    </motion.div>
                  </div>
                  <div className="text-[10px] tracking-wider text-[#9397AC] uppercase">
                    {stage.label}
                  </div>
                </div>
                {idx < stages.length - 1 && (
                  <div
                    className="flex-1 h-[2px] mx-1 md:mx-3 relative top-[-28px] overflow-hidden rounded-full"
                    style={{ background: `linear-gradient(90deg, ${stage.color}44, ${stages[idx + 1].color}44)` }}
                  >
                    <motion.div
                      className="h-full w-12 rounded-full"
                      style={{ background: `linear-gradient(90deg, transparent, ${stage.color}, transparent)`, filter: "blur(1px)" }}
                      animate={{ x: ["-100%", "400%"] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: idx * 0.25 }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="md:col-span-2">
            <StatTile label="Rejected" value={metrics?.rejected ?? 0} color={GLOW.coral} />
          </div>
          <div className="md:col-span-1">
            <StatTile label="Senders" value={metrics?.unique_senders ?? 0} color={GLOW.violet} compact />
          </div>
          <div className="md:col-span-2">
            <StatTile label="Eval Accuracy" value={metrics?.eval_accuracy ?? "-"} color={GLOW.cyan} hero />
          </div>
        </div>

        <div className="text-xs tracking-[0.15em] text-[#9397AC] uppercase mb-4">Activity</div>
        <div className="rounded-3xl backdrop-blur-xl bg-white/[0.035] border border-white/[0.08] overflow-hidden shadow-[0_8px_40px_rgba(0,0,0,0.3)]">
          {interactions.length === 0 ? (
            <div className="p-10 text-center text-[#9397AC] text-sm">
              No activity yet. Run{" "}
              <code className="text-[#F2F2F8] bg-white/[0.06] px-1.5 py-0.5 rounded">python graph.py</code>{" "}
              to generate some.
            </div>
          ) : (
            <AnimatePresence>
              {interactions.map((i, idx) => {
                const cls = CLASS_STYLES[i.classification] ?? CLASS_STYLES.spam;
                const out = OUTCOME_STYLES[i.outcome] ?? OUTCOME_STYLES.skipped;
                return (
                  <motion.div
                    key={i.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    whileHover={{ x: 2 }}
                    transition={{ delay: idx * 0.03 }}
                    className="flex items-center gap-4 px-6 py-4 border-b border-white/[0.06] last:border-b-0 hover:bg-white/[0.03] transition-colors"
                  >
                    <div className="text-[11px] text-[#9397AC] w-28 shrink-0">
                      {new Date(i.timestamp).toLocaleString(undefined, {
                        month: "2-digit",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-[#F2F2F8] truncate">{i.subject}</div>
                      <div className="text-[11px] text-[#9397AC] truncate">{i.sender_email}</div>
                    </div>
                    <span
                      className="text-[10px] tracking-wide uppercase px-2.5 py-1 rounded-full border shrink-0"
                      style={{ color: cls.text, background: cls.bg, borderColor: cls.border }}
                    >
                      {i.classification}
                    </span>
                    <span
                      className="text-[10px] tracking-wide uppercase px-2.5 py-1 rounded-full border shrink-0"
                      style={{ color: out.text, background: out.bg, borderColor: out.border }}
                    >
                      {i.outcome}
                    </span>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          )}
        </div>

        <div className="mt-8 text-center text-[11px] text-[#9397AC] tracking-wide">
          Refreshes every 8s
        </div>
      </div>
    </div>
  );
}

function StatTile({
  label,
  value,
  color,
  hero,
  compact,
}: {
  label: string;
  value: string | number;
  color: string;
  hero?: boolean;
  compact?: boolean;
}) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="relative rounded-3xl backdrop-blur-xl bg-white/[0.035] border border-white/[0.08] p-6 overflow-hidden h-full shadow-[0_8px_40px_rgba(0,0,0,0.25)]"
    >
      <div
        className="absolute top-0 left-0 right-0 h-[2px]"
        style={{ background: `linear-gradient(90deg, transparent, ${color}, transparent)` }}
      />
      <div
        className="absolute -top-8 -right-8 w-24 h-24 rounded-full blur-2xl opacity-30"
        style={{ background: color }}
      />
      <div className="relative">
        <div className="text-[10px] tracking-wider text-[#9397AC] uppercase mb-2">{label}</div>
        <div
          className={`font-[family-name:var(--font-display)] font-bold ${hero ? "text-4xl" : compact ? "text-2xl" : "text-3xl"}`}
          style={{ color }}
        >
          {value}
        </div>
      </div>
    </motion.div>
  );
}