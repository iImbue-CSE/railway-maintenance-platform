import React, { useState, useMemo } from "react";

// Local SVG icons replacing lucide-react to avoid React version mismatch errors
const AlertTriangle = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#E8A33D" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
    <line x1="12" y1="9" x2="12" y2="13"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
);

const Zap = ({ color }) => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>
);

const Radio = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4A90D9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginTop: 2 }}>
    <circle cx="12" cy="12" r="2"/>
    <path d="M16.24 7.76a6 6 0 0 1 0 8.49"/>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
    <path d="M7.76 16.24a6 6 0 0 1 0-8.49"/>
    <path d="M4.93 19.07a10 10 0 0 1 0-14.14"/>
  </svg>
);

// MOCK DATA
const MOCK_SECTIONS = [
  { id: "S1", label: "Corridor S1 · Ch 12–18" },
  { id: "S2", label: "Corridor S2 · Ch 18–24" },
  { id: "S3", label: "Corridor S3 · Yard Loop" },
];

const MOCK_SCHEDULE = [
  { task_id: "T1", block: 1, duration: 1, track_section: "S1", defect_type: "Rail crack", urgency_score: 92, est_repair_hours: 4, days_overdue: 5, requires_power_block: true },
  { task_id: "T2", block: 0, duration: 1, track_section: "S1", defect_type: "Ballast wear", urgency_score: 60, est_repair_hours: 6, days_overdue: 2, requires_power_block: false },
  { task_id: "T3", block: 0, duration: 1, track_section: "S2", defect_type: "Signal fault", urgency_score: 88, est_repair_hours: 3, days_overdue: 10, requires_power_block: true },
  { task_id: "T4", block: 0, duration: 1, track_section: "S3", defect_type: "Fastener loose", urgency_score: 30, est_repair_hours: 2, days_overdue: 1, requires_power_block: false },
  { task_id: "T5", block: 3, duration: 1, track_section: "S2", defect_type: "Overhead wear", urgency_score: 45, est_repair_hours: 5, days_overdue: 3, requires_power_block: false },
  { task_id: "T6", block: 5, duration: 1, track_section: "S3", defect_type: "Point failure", urgency_score: 71, est_repair_hours: 3, days_overdue: 6, requires_power_block: true },
];

const WEEK_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const MONTH_LABELS = Array.from({ length: 28 }, (_, i) => `${i + 1}`);

function urgencyColor(score) {
  if (score >= 80) return { bg: "#3A1712", border: "#E4483A", text: "#F4A89C", dot: "#E4483A" };
  if (score >= 50) return { bg: "#3A2A10", border: "#E8A33D", text: "#F2CE93", dot: "#E8A33D" };
  return { bg: "#12301E", border: "#4CAF6D", text: "#9FD9B4", dot: "#4CAF6D" };
}

export default function App() {
  const [view, setView] = useState("week"); // "week" | "month"
  const [selected, setSelected] = useState(MOCK_SCHEDULE[0]);
  const [sectionFilter, setSectionFilter] = useState("all");

  const labels = view === "week" ? WEEK_LABELS : MONTH_LABELS;
  const numBlocks = labels.length;

  const visibleSections =
    sectionFilter === "all" ? MOCK_SECTIONS : MOCK_SECTIONS.filter((s) => s.id === sectionFilter);

  const tasksBySection = useMemo(() => {
    const map = {};
    for (const sec of MOCK_SECTIONS) map[sec.id] = [];
    for (const t of MOCK_SCHEDULE) {
      if (t.block < numBlocks && map[t.track_section]) map[t.track_section].push(t);
    }
    return map;
  }, [numBlocks]);

  const visibleTasks = MOCK_SCHEDULE.filter((t) => t.block < numBlocks);
  const summary = {
    total: visibleTasks.length,
    urgent: visibleTasks.filter((t) => t.urgency_score >= 80).length,
    powerBlock: visibleTasks.filter((t) => t.requires_power_block).length,
  };

  return (
    <div
      style={{
        fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
        background: "#10151C",
        color: "#E8ECF1",
        minHeight: "100vh",
        padding: "0",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        .mono { font-family: 'IBM Plex Mono', monospace; }
        .rs-btn { transition: background 0.15s ease, color 0.15s ease; cursor: pointer; }
        .rs-bar { transition: transform 0.12s ease, box-shadow 0.12s ease; cursor: pointer; }
        .rs-bar:hover { transform: translateY(-1px); }
        select.rs-select { appearance: none; -webkit-appearance: none; }
      `}</style>

      {/* Header */}
      <div style={{ padding: "20px 24px 16px", borderBottom: "1px solid #232B36" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
            <Radio />
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, letterSpacing: 0.2 }}>
                Track Maintenance Schedule
              </div>
              <div style={{ fontSize: 12.5, color: "#8B96A5", marginTop: 3, maxWidth: 420, lineHeight: 1.4 }}>
                Every colored block below is one repair job the system has scheduled. Click any block to see its details.
              </div>
            </div>
          </div>

          <div style={{ display: "flex", background: "#1A212B", borderRadius: 6, padding: 3, border: "1px solid #2A323D", flexShrink: 0 }}>
            {["week", "month"].map((v) => (
              <button
                key={v}
                className="rs-btn"
                onClick={() => setView(v)}
                style={{
                  border: "none",
                  borderRadius: 4,
                  padding: "6px 14px",
                  fontSize: 12.5,
                  fontWeight: 500,
                  background: view === v ? "#4A90D9" : "transparent",
                  color: view === v ? "#0D1218" : "#8B96A5",
                }}
              >
                {v === "week" ? "This week" : "This month"}
              </button>
            ))}
          </div>
        </div>

        {/* Summary strip */}
        <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6, background: "#1A212B", border: "1px solid #2A323D", borderRadius: 6, padding: "8px 14px" }}>
            <span style={{ fontSize: 18, fontWeight: 600 }}>{summary.total}</span>
            <span style={{ fontSize: 12, color: "#8B96A5" }}>repairs planned</span>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6, background: "#1A212B", border: "1px solid #3A1712", borderRadius: 6, padding: "8px 14px" }}>
            <span style={{ fontSize: 18, fontWeight: 600, color: "#E4483A" }}>{summary.urgent}</span>
            <span style={{ fontSize: 12, color: "#8B96A5" }}>need urgent attention</span>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 6, background: "#1A212B", border: "1px solid #2A323D", borderRadius: 6, padding: "8px 14px" }}>
            <Zap color="#E8A33D" />
            <span style={{ fontSize: 18, fontWeight: 600, color: "#E8A33D" }}>{summary.powerBlock}</span>
            <span style={{ fontSize: 12, color: "#8B96A5" }}>need power shutdown</span>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          {[
            { label: "Urgent — fix ASAP", color: "#E4483A" },
            { label: "Moderate — schedule soon", color: "#E8A33D" },
            { label: "Low — can wait", color: "#4CAF6D" },
          ].map((l) => (
            <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 9, height: 9, borderRadius: 2, background: l.color }} />
              <span style={{ fontSize: 11.5, color: "#8B96A5" }}>{l.label}</span>
            </div>
          ))}
          <div style={{ width: 1, height: 12, background: "#2A323D" }} />
          <div style={{ display: "flex", gap: 6 }}>
            {["all", ...MOCK_SECTIONS.map((s) => s.id)].map((id) => (
              <button
                key={id}
                className="rs-btn"
                onClick={() => setSectionFilter(id)}
                style={{
                  border: "1px solid " + (sectionFilter === id ? "#4A90D9" : "#2A323D"),
                  borderRadius: 5,
                  background: sectionFilter === id ? "#1A2530" : "transparent",
                  color: sectionFilter === id ? "#9FC5EE" : "#8B96A5",
                  fontSize: 11.5,
                  padding: "4px 10px",
                }}
              >
                {id === "all" ? "All corridors" : id}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "flex", flex: 1, minHeight: 420 }}>
        {/* Timeline */}
        <div style={{ flex: 1, padding: "20px 24px", overflowX: "auto" }}>
          <div style={{ minWidth: numBlocks * (view === "week" ? 130 : 34) + 150 }}>
            {/* Column headers */}
            <div style={{ display: "flex", marginBottom: 8 }}>
              <div style={{ width: 150, flexShrink: 0 }} />
              {labels.map((l, i) => (
                <div
                  key={i}
                  className="mono"
                  style={{
                    width: view === "week" ? 130 : 34,
                    flexShrink: 0,
                    fontSize: 11,
                    color: "#7A8494",
                    textAlign: "center",
                  }}
                >
                  {l}
                </div>
              ))}
            </div>

            {/* Rows */}
            {visibleSections.map((sec) => (
              <div key={sec.id} style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                <div style={{ width: 150, flexShrink: 0, paddingRight: 12 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 500, color: "#C4CCD6" }}>{sec.id}</div>
                  <div style={{ fontSize: 10.5, color: "#5E6773" }}>{sec.label.split("·")[1]}</div>
                </div>
                <div style={{ display: "flex", position: "relative", height: 38 }}>
                  {labels.map((_, b) => (
                    <div
                      key={b}
                      style={{
                        width: view === "week" ? 130 : 34,
                        flexShrink: 0,
                        height: 38,
                        borderLeft: "1px solid #1D2430",
                        boxSizing: "border-box",
                      }}
                    />
                  ))}
                  {tasksBySection[sec.id].map((t) => {
                    const c = urgencyColor(t.urgency_score);
                    const colWidth = view === "week" ? 130 : 34;
                    const isSel = selected?.task_id === t.task_id;
                    return (
                      <div
                        key={t.task_id}
                        className="rs-bar"
                        onClick={() => setSelected(t)}
                        style={{
                          position: "absolute",
                          left: t.block * colWidth + 4,
                          width: colWidth * t.duration - 8,
                          top: 4,
                          height: 30,
                          background: c.bg,
                          border: `1px solid ${isSel ? c.border : c.border + "88"}`,
                          borderRadius: 5,
                          boxShadow: isSel ? `0 0 0 1px ${c.border}` : "none",
                          display: "flex",
                          alignItems: "center",
                          gap: 5,
                          padding: "0 8px",
                          overflow: "hidden",
                        }}
                      >
                        {t.requires_power_block && <Zap color={c.text} />}
                        <span
                          style={{ fontSize: 11, fontWeight: 500, color: c.text, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}
                        >
                          {view === "week" ? t.defect_type : t.task_id}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail panel */}
        <div
          style={{
            width: 260,
            flexShrink: 0,
            borderLeft: "1px solid #232B36",
            padding: "20px",
            background: "#141A22",
          }}
        >
          {selected ? (
            <>
              <div style={{ fontSize: 11, color: "#7A8494", marginBottom: 2 }}>Task</div>
              <div className="mono" style={{ fontSize: 16, fontWeight: 500, marginBottom: 14 }}>
                {selected.task_id}
              </div>

              {[
                ["Defect", selected.defect_type],
                ["Corridor", selected.track_section],
                ["Days overdue", selected.days_overdue],
                ["Est. repair", `${selected.est_repair_hours} hrs`],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #1D2430" }}>
                  <span style={{ fontSize: 12, color: "#7A8494" }}>{k}</span>
                  <span className="mono" style={{ fontSize: 12, color: "#C4CCD6" }}>{v}</span>
                </div>
              ))}

              <div style={{ marginTop: 16 }}>
                <div style={{ fontSize: 11, color: "#7A8494", marginBottom: 6 }}>Urgency score</div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ flex: 1, height: 6, background: "#1D2430", borderRadius: 3, overflow: "hidden" }}>
                    <div
                      style={{
                        width: `${selected.urgency_score}%`,
                        height: "100%",
                        background: urgencyColor(selected.urgency_score).border,
                      }}
                    />
                  </div>
                  <span className="mono" style={{ fontSize: 12, fontWeight: 500 }}>{selected.urgency_score}</span>
                </div>
              </div>

              {selected.requires_power_block && (
                <div
                  style={{
                    marginTop: 16,
                    display: "flex",
                    gap: 8,
                    padding: "9px 10px",
                    background: "#241A10",
                    border: "1px solid #4A3419",
                    borderRadius: 6,
                  }}
                >
                  <AlertTriangle />
                  <span style={{ fontSize: 11.5, color: "#D6B87F", lineHeight: 1.4 }}>
                    Requires power block. Adjacent-corridor jobs are held clear by the solver's headway constraint.
                  </span>
                </div>
              )}
            </>
          ) : (
            <div style={{ fontSize: 12.5, color: "#5E6773" }}>Select a task on the timeline</div>
          )}
        </div>
      </div>
    </div>
  );
}
