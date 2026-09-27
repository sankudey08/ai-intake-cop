import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// ─── Colour tokens ────────────────────────────────────────────────────────
const C = {
  accent: '#6366f1', success: '#22c55e', warning: '#f59e0b',
  danger: '#ef4444', muted: '#94a3b8', blue: '#38bdf8',
}

// ─── Helpers ──────────────────────────────────────────────────────────────
const fmt = (n) => (n ?? 0).toLocaleString()

function StatCard({ label, value, sub, color = C.accent, danger = false }) {
  return (
    <div style={{
      background: '#1a1d27', border: `1px solid ${danger ? '#ef4444' : '#2d3144'}`,
      borderRadius: 12, padding: '20px 24px',
    }}>
      <div style={{ color: '#94a3b8', fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color, marginTop: 6 }}>{value}</div>
      {sub && <div style={{ color: '#64748b', fontSize: 12, marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={{ fontSize: 16, fontWeight: 600, color: '#e2e8f0', marginBottom: 16,
        borderLeft: '3px solid #6366f1', paddingLeft: 12 }}>{title}</h2>
      {children}
    </div>
  )
}

// ─── Main App ─────────────────────────────────────────────────────────────
export default function App() {
  const [metrics, setMetrics] = useState(null)
  const [jobs, setJobs] = useState([])
  const [guardrailInput, setGuardrailInput] = useState('')
  const [guardrailResult, setGuardrailResult] = useState(null)
  const [intakeText, setIntakeText] = useState('')
  const [intakeResult, setIntakeResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('dashboard')
  const [history, setHistory] = useState([])   // token history for chart

  const fetchMetrics = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/metrics-api/summary`)
      setMetrics(r.data)
      setHistory(h => [...h.slice(-19), {
        t: new Date().toLocaleTimeString(),
        tokens: r.data.tokens?.used ?? 0,
        jobs: r.data.jobs?.done ?? 0,
      }])
    } catch { /* api may not be running yet */ }
  }, [])

  const fetchJobs = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/tasks/log`)
      setJobs(r.data.events ?? [])
    } catch { }
  }, [])

  useEffect(() => {
    fetchMetrics(); fetchJobs()
    const id = setInterval(() => { fetchMetrics(); fetchJobs() }, 3000)
    return () => clearInterval(id)
  }, [fetchMetrics, fetchJobs])

  const runGuardrail = async () => {
    setLoading(true)
    try {
      const r = await axios.post(`${API}/guardrails/regex-check`, { text: guardrailInput })
      setGuardrailResult(r.data)
    } catch (e) { setGuardrailResult({ error: e.message }) }
    setLoading(false)
  }

  const runIntake = async () => {
    setLoading(true)
    try {
      const r = await axios.post(`${API}/tasks/process`, {
        message_id: `manual-${Date.now()}`,
        text: intakeText,
        source: 'manual',
      })
      setIntakeResult(r.data)
    } catch (e) { setIntakeResult({ error: e.message }) }
    setLoading(false)
  }

  const utilPct = metrics?.tokens?.utilization_pct ?? 0
  const utilColor = utilPct > 80 ? C.danger : utilPct > 50 ? C.warning : C.success

  const pieData = [
    { name: 'Done', value: metrics?.jobs?.done ?? 0 },
    { name: 'Blocked', value: metrics?.jobs?.blocked ?? 0 },
    { name: 'Queued', value: metrics?.jobs?.queued ?? 0 },
  ]
  const PIE_COLORS = [C.success, C.danger, C.warning]

  return (
    <div style={{ minHeight: '100vh', background: '#0f1117' }}>
      {/* Header */}
      <header style={{
        background: '#1a1d27', borderBottom: '1px solid #2d3144',
        padding: '16px 32px', display: 'flex', alignItems: 'center', gap: 16,
      }}>
        <span style={{ fontSize: 24 }}>🧠</span>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 700, color: '#e2e8f0' }}>AI Intake Cop</h1>
          <p style={{ color: '#64748b', fontSize: 12 }}>Helicone Analytics • Grafana • Workshop Demo</p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          {['dashboard', 'guardrails', 'intake', 'logs'].map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding: '6px 14px', borderRadius: 6, border: 'none', fontSize: 13,
              background: tab === t ? '#6366f1' : '#2d3144',
              color: tab === t ? '#fff' : '#94a3b8', fontWeight: tab === t ? 600 : 400,
            }}>{t.charAt(0).toUpperCase() + t.slice(1)}</button>
          ))}
        </div>
      </header>

      <main style={{ padding: '32px', maxWidth: 1200, margin: '0 auto' }}>

        {/* ── Dashboard Tab ── */}
        {tab === 'dashboard' && (
          <>
            <Section title="Token Budget">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
                <StatCard label="Tokens Used"   value={fmt(metrics?.tokens?.used)}    sub={`of ${fmt(metrics?.tokens?.limit)} limit`} color={utilColor} danger={utilPct > 80} />
                <StatCard label="Utilization"   value={`${utilPct}%`}                  color={utilColor} />
                <StatCard label="Jobs Processed" value={fmt(metrics?.jobs?.total)}     color={C.accent} />
                <StatCard label="Alerts Fired"  value={fmt(metrics?.alerts_fired)}     color={metrics?.alerts_fired > 0 ? C.danger : C.success} />
              </div>

              {/* Budget bar */}
              <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 20, marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ color: '#94a3b8', fontSize: 12 }}>Budget utilization</span>
                  <span style={{ color: utilColor, fontWeight: 600, fontSize: 12 }}>{utilPct}%</span>
                </div>
                <div style={{ background: '#2d3144', borderRadius: 99, height: 10, overflow: 'hidden' }}>
                  <div style={{ width: `${Math.min(utilPct, 100)}%`, height: '100%', background: utilColor, borderRadius: 99, transition: 'width 0.5s' }} />
                </div>
              </div>
            </Section>

            <Section title="Token Usage Over Time">
              <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 20 }}>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3144" />
                    <XAxis dataKey="t" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 8 }} />
                    <Line type="monotone" dataKey="tokens" stroke={C.accent} strokeWidth={2} dot={false} name="Tokens" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Section>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <Section title="Job Status Distribution">
                <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 20 }}>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value">
                        {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 8 }} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Section>

              <Section title="Quick Links">
                <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {[
                    { label: '📊 Grafana Dashboard', url: 'http://localhost:3000' },
                    { label: '🔬 Helicone Analytics', url: 'http://localhost:8585' },
                    { label: '📝 FastAPI Swagger', url: 'http://localhost:8000/docs' },
                    { label: '📈 Prometheus', url: 'http://localhost:9090' },
                  ].map(({ label, url }) => (
                    <a key={url} href={url} target="_blank" rel="noreferrer" style={{
                      display: 'block', padding: '10px 14px', background: '#2d3144',
                      borderRadius: 8, color: '#e2e8f0', textDecoration: 'none', fontSize: 13,
                    }}>{label}</a>
                  ))}
                </div>
              </Section>
            </div>
          </>
        )}

        {/* ── Guardrails Tab ── */}
        {tab === 'guardrails' && (
          <Section title="🛡️ Guardrail Tester">
            <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 24 }}>
              <p style={{ color: '#94a3b8', marginBottom: 16, fontSize: 13 }}>
                Test the regex guardrail. Try: <code style={{ color: '#818cf8' }}>My SSN is 123-45-6789</code> or <code style={{ color: '#818cf8' }}>ignore previous instructions</code>
              </p>
              <textarea
                value={guardrailInput}
                onChange={e => setGuardrailInput(e.target.value)}
                placeholder="Enter text to check..."
                rows={4}
                style={{
                  width: '100%', background: '#0f1117', border: '1px solid #2d3144',
                  borderRadius: 8, color: '#e2e8f0', padding: 12, fontSize: 13,
                  fontFamily: 'monospace', resize: 'vertical',
                }}
              />
              <button onClick={runGuardrail} disabled={loading || !guardrailInput} style={{
                marginTop: 12, padding: '10px 20px', background: '#6366f1', color: '#fff',
                border: 'none', borderRadius: 8, fontWeight: 600, opacity: loading ? 0.6 : 1,
              }}>
                {loading ? 'Checking...' : 'Run Regex Check'}
              </button>

              {guardrailResult && (
                <div style={{
                  marginTop: 16, padding: 16, borderRadius: 8,
                  background: guardrailResult.safe ? '#052e16' : '#3b0000',
                  border: `1px solid ${guardrailResult.safe ? '#22c55e' : '#ef4444'}`,
                }}>
                  <div style={{ color: guardrailResult.safe ? C.success : C.danger, fontWeight: 700, marginBottom: 8 }}>
                    {guardrailResult.safe ? '✅ SAFE — No violations found' : '🚫 BLOCKED — Guardrail triggered'}
                  </div>
                  {guardrailResult.matched && (
                    <div style={{ color: '#94a3b8', fontSize: 12 }}>
                      Matched: <code style={{ color: '#f87171' }}>{guardrailResult.matched}</code>
                    </div>
                  )}
                  <pre style={{ color: '#64748b', fontSize: 11, marginTop: 8, overflow: 'auto' }}>
                    {JSON.stringify(guardrailResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* ── Intake Tab ── */}
        {tab === 'intake' && (
          <Section title="⚡ Manual Intake Trigger">
            <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 24 }}>
              <p style={{ color: '#94a3b8', marginBottom: 16, fontSize: 13 }}>
                Simulate a Gmail/Calendar trigger manually. The message is processed in the background.
              </p>
              <textarea
                value={intakeText}
                onChange={e => setIntakeText(e.target.value)}
                placeholder="Paste email body or calendar event description..."
                rows={6}
                style={{
                  width: '100%', background: '#0f1117', border: '1px solid #2d3144',
                  borderRadius: 8, color: '#e2e8f0', padding: 12, fontSize: 13,
                  fontFamily: 'monospace', resize: 'vertical',
                }}
              />
              <button onClick={runIntake} disabled={loading || !intakeText} style={{
                marginTop: 12, padding: '10px 20px', background: '#6366f1', color: '#fff',
                border: 'none', borderRadius: 8, fontWeight: 600, opacity: loading ? 0.6 : 1,
              }}>
                {loading ? 'Processing...' : 'Send to Intake'}
              </button>

              {intakeResult && (
                <div style={{ marginTop: 16, padding: 16, borderRadius: 8, background: '#0f1117', border: '1px solid #2d3144' }}>
                  <div style={{ color: '#818cf8', fontWeight: 600, marginBottom: 8 }}>Result:</div>
                  <pre style={{ color: '#94a3b8', fontSize: 12, overflow: 'auto' }}>
                    {JSON.stringify(intakeResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* ── Logs Tab ── */}
        {tab === 'logs' && (
          <Section title="📋 Background Task Log">
            <div style={{ background: '#1a1d27', border: '1px solid #2d3144', borderRadius: 12, padding: 20 }}>
              {jobs.length === 0
                ? <p style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>No events yet. Trigger an intake above.</p>
                : jobs.slice().reverse().map((ev, i) => (
                  <div key={i} style={{
                    padding: '10px 14px', borderRadius: 6, marginBottom: 6,
                    background: '#0f1117', border: '1px solid #2d3144',
                    display: 'flex', gap: 16, alignItems: 'center', fontSize: 12,
                  }}>
                    <span style={{ color: '#64748b', minWidth: 80 }}>
                      {new Date(ev.ts * 1000).toLocaleTimeString()}
                    </span>
                    <span style={{ color: '#818cf8', minWidth: 80 }}>{ev.job_id}</span>
                    <span style={{
                      color: ev.event === 'completed' ? C.success : ev.event === 'blocked_by_regex' ? C.danger : C.warning,
                      fontWeight: 600,
                    }}>{ev.event}</span>
                    {ev.priority && <span style={{ color: '#94a3b8' }}>→ {ev.priority}</span>}
                  </div>
                ))
              }
            </div>
          </Section>
        )}

      </main>
    </div>
  )
}
