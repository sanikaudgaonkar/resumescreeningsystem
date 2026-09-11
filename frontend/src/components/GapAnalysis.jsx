// Shows the gap_analysis object your backend already computes:
// how many CRITICAL / HIGH / MEDIUM / LOW requirement gaps there
// are, plus a 3-tier "what to fix first" roadmap.

export default function GapAnalysis({ gapAnalysis }) {
  if (!gapAnalysis) return null;

  const { summary, roadmap } = gapAnalysis;
  const totalGaps =
    summary.critical_gaps +
    summary.high_gaps +
    summary.medium_gaps +
    summary.low_gaps;

  return (
    <section className="gap-section">
      <div className="section-title">
        <h2>Gap Analysis & Roadmap</h2>
        <span>
          {summary.total_matched} matched · {totalGaps} gap
          {totalGaps === 1 ? "" : "s"}
        </span>
      </div>

      {/* SUMMARY TILES */}
      <div className="gap-summary-grid">
        <div className="gap-tile tile-critical">
          <strong>{summary.critical_gaps}</strong>
          <span>Critical</span>
        </div>
        <div className="gap-tile tile-high">
          <strong>{summary.high_gaps}</strong>
          <span>High</span>
        </div>
        <div className="gap-tile tile-medium">
          <strong>{summary.medium_gaps}</strong>
          <span>Medium</span>
        </div>
        <div className="gap-tile tile-low">
          <strong>{summary.low_gaps}</strong>
          <span>Low</span>
        </div>
        <div className="gap-tile tile-matched">
          <strong>{summary.total_matched}</strong>
          <span>Matched</span>
        </div>
      </div>

      {/* ROADMAP */}
      <div className="roadmap-grid">
        <RoadmapColumn
          title="Immediate Priority"
          subtitle="Critical gaps — address these first"
          items={roadmap.immediate}
          tone="critical"
        />
        <RoadmapColumn
          title="Next Steps"
          subtitle="High / medium priority gaps"
          items={roadmap.next}
          tone="medium"
        />
        <RoadmapColumn
          title="Nice to Have"
          subtitle="Low priority gaps"
          items={roadmap.optional}
          tone="low"
        />
      </div>
    </section>
  );
}

function RoadmapColumn({ title, subtitle, items, tone }) {
  return (
    <div className={`roadmap-column tone-${tone}`}>
      <h3>{title}</h3>
      <p className="roadmap-subtitle">{subtitle}</p>

      {!items || items.length === 0 ? (
        <p className="roadmap-empty">Nothing here — great job!</p>
      ) : (
        <ul>
          {items.map((req, i) => (
            <li key={i}>{req}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
