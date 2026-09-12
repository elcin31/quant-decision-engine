import Link from "next/link";
import { METHODS } from "@/types/analysis";

const featured = ["risk", "monte_carlo", "correlation_matrix", "scenario", "backtest"];

const categoryLabels: Record<string, string> = {
  returns: "Returns",
  risk: "Risk",
  performance: "Performance",
  relationship: "Relationships",
  simulation: "Simulation",
  research: "Research",
};

export default function HomePage() {
  const featuredMethods = featured
    .map((id) => METHODS.find((m) => m.id === id))
    .filter(Boolean);

  return (
    <div className="research-home">
      <section className="hero">
        <div className="eyebrow"><span className="status-dot" /> QUANTITATIVE RESEARCH</div>
        <h1>Research before<br /><em>decision.</em></h1>
        <p className="hero-copy">
          A quantitative workspace for measuring risk, testing scenarios,
          running simulations, and turning market data into evidence.
        </p>
        <Link href="/analysis" className="btn btn-primary hero-cta">
          <span>+</span> New analysis
        </Link>
        <div className="hero-note">
          <span>PYTHON ENGINE</span>
          <span>•</span>
          <span>LOCAL DATA</span>
          <span>•</span>
          <span>NO BROKER CONNECTION</span>
        </div>
      </section>

      <section className="featured-section">
        <div className="section-head">
          <div>
            <div className="eyebrow">QUICK START</div>
            <h2>Research methods</h2>
          </div>
          <Link href="/analysis" className="text-link">View all →</Link>
        </div>

        <div className="featured-grid">
          {featuredMethods.map((m, i) => m && (
            <Link key={m.id} href={`/analysis?method=${m.id}`} className={`method-tile tile-${i + 1}`}>
              <div className="tile-index">{String(i + 1).padStart(2, "0")}</div>
              <div className="tile-content">
                <div className="tile-category">{categoryLabels[m.category]}</div>
                <h3>{m.label}</h3>
                <p>{m.description}</p>
              </div>
              <span className="tile-arrow">↗</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="principles">
        <div className="principle-label">WORKFLOW</div>
        <div className="workflow">
          {["Research", "Calculate", "Simulate", "Understand", "Decide"].map((item, i) => (
            <div className="workflow-step" key={item}>
              <span>{String(i + 1).padStart(2, "0")}</span>
              <strong>{item}</strong>
              {i < 4 && <i>→</i>}
            </div>
          ))}
        </div>
      </section>

      <section className="method-index">
        <div className="section-head">
          <div>
            <div className="eyebrow">LIBRARY</div>
            <h2>All methods</h2>
          </div>
          <span className="method-count">{METHODS.length} methods</span>
        </div>
        <div className="method-list">
          {METHODS.map((m) => (
            <Link key={m.id} href={`/analysis?method=${m.id}`} className="method-row">
              <span className="method-id">{m.id}</span>
              <strong>{m.label}</strong>
              <span className="method-description">{m.description}</span>
              <span className="method-arrow">→</span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
