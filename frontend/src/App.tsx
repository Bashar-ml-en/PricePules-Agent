import { FormEvent, type ReactNode, useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getItems, getLocations, runAnalysis } from "./api";
import type { AnalysisPayload, CatalogueItem, DecisionStatus, DailyPoint, ModelMetrics } from "./types";

const workflowSteps = ["Data quality", "Baseline", "Forecast", "Anomaly", "Critic"];

function App() {
  const today = new Date();
  const start = new Date(today);
  start.setDate(today.getDate() - 90);
  const [items, setItems] = useState<CatalogueItem[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [itemCode, setItemCode] = useState("");
  const [geographyType, setGeographyType] = useState<"national" | "state" | "district">("national");
  const [geographyValue, setGeographyValue] = useState("");
  const [startDate, setStartDate] = useState(toDateInput(start));
  const [endDate, setEndDate] = useState(toDateInput(today));
  const [analysis, setAnalysis] = useState<AnalysisPayload | null>(null);
  const [isLoadingCatalogue, setIsLoadingCatalogue] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedItem = useMemo(
    () => items.find((item) => item.item_code === Number(itemCode)),
    [itemCode, items],
  );
  const canRun = Boolean(
    itemCode && startDate && endDate && (geographyType === "national" || geographyValue),
  );

  useEffect(() => {
    void loadItems();
  }, []);

  useEffect(() => {
    if (geographyType === "national") {
      setLocations([]);
      setGeographyValue("");
      return;
    }
    setGeographyValue("");
    void loadLocations(geographyType);
  }, [geographyType]);

  async function loadItems() {
    try {
      setIsLoadingCatalogue(true);
      setError(null);
      setItems(await getItems());
    } catch (requestError) {
      setError(messageFor(requestError));
    } finally {
      setIsLoadingCatalogue(false);
    }
  }

  async function loadLocations(type: "state" | "district") {
    try {
      setError(null);
      setLocations(await getLocations(type));
    } catch (requestError) {
      setError(messageFor(requestError));
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canRun) return;
    try {
      setIsRunning(true);
      setError(null);
      const result = await runAnalysis({
        item_code: Number(itemCode),
        geography_type: geographyType,
        geography_value: geographyType === "national" ? null : geographyValue,
        start_date: startDate,
        end_date: endDate,
        min_transactions: 3,
        min_premises: 2,
        anomaly_threshold: 3.5,
      });
      setAnalysis(result);
    } catch (requestError) {
      setError(messageFor(requestError));
    } finally {
      setIsRunning(false);
    }
  }

  const points = analysis?.series?.points ?? [];
  const latest = points.at(-1);
  const latestExpected = latest?.baseline_expected ?? analysis?.forecast?.predictions.at(-1)?.baseline_expected;
  const unit = analysis?.series?.unit ?? selectedItem?.unit;

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <a className="brand" href="#analysis" aria-label="PricePulse MY home">
          <span className="brand-mark" aria-hidden="true">P</span>
          <span><strong>PricePulse</strong><small>MY · Evidence system</small></span>
        </a>
        <nav>
          <a className="nav-link is-active" href="#analysis"><NavGlyph path="M4 12h16M4 6h16M4 18h10" />Analysis</a>
          <a className="nav-link" href="#evidence"><NavGlyph path="M5 4h14v16H5zM8 8h8M8 12h8M8 16h4" />Evidence</a>
          <a className="nav-link" href="#methodology"><NavGlyph path="M12 3v18M3 12h18" />Methodology</a>
        </nav>
        <div className="sidebar-foot">
          <span className="eyebrow">Provenance</span>
          <p>Official Malaysian open data</p>
          <span className="tiny">Human review remains required.</span>
        </div>
      </aside>

      <main id="analysis" className="main-content">
        <header className="command-header">
          <div>
            <p className="eyebrow">Price intelligence / controlled workflow</p>
            <h1>Price shock analysis</h1>
            <p className="header-copy">Identify unusual local essential-goods price movements for human review.</p>
          </div>
          <div className="header-state">
            <span className="source-state"><span className="state-dot" /> Official PriceCatcher source</span>
            {analysis ? <StatusBadge status={analysis.report.critic_status} /> : null}
          </div>
        </header>

        <section className="control-card" aria-labelledby="controls-heading">
          <div className="section-heading"><div><p className="eyebrow">Analysis scope</p><h2 id="controls-heading">Define a comparable price series</h2></div><span className="scope-note">One verified item and unit per run</span></div>
          <form className="analysis-form" onSubmit={handleSubmit}>
            <label>
              <span>Essential item</span>
              <select value={itemCode} onChange={(event) => setItemCode(event.target.value)} disabled={isLoadingCatalogue} required>
                <option value="">{isLoadingCatalogue ? "Loading official catalogue…" : "Select an official item"}</option>
                {items.map((item) => <option value={item.item_code} key={item.item_code}>{item.item} · {item.unit}</option>)}
              </select>
            </label>
            <label>
              <span>Geography</span>
              <select value={geographyType} onChange={(event) => setGeographyType(event.target.value as typeof geographyType)}>
                <option value="national">National</option><option value="state">State</option><option value="district">District</option>
              </select>
            </label>
            {geographyType !== "national" ? <label>
              <span>{geographyType === "state" ? "State" : "District"}</span>
              <select value={geographyValue} onChange={(event) => setGeographyValue(event.target.value)} required>
                <option value="">Select a verified {geographyType}</option>
                {locations.map((location) => <option key={location} value={location}>{location}</option>)}
              </select>
            </label> : <div className="national-field"><span>Scope</span><strong>All verified premises</strong></div>}
            <label><span>From</span><input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} required /></label>
            <label><span>To</span><input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} required /></label>
            <button className="primary-action" type="submit" disabled={!canRun || isRunning}>
              {isRunning ? "Running controlled analysis…" : "Run analysis"}<ArrowGlyph />
            </button>
          </form>
          <div className="workflow-strip" aria-label="Workflow stages">
            {workflowSteps.map((step, index) => <div className={isRunning ? "workflow-step is-running" : "workflow-step"} key={step}><span>{String(index + 1).padStart(2, "0")}</span>{step}</div>)}
          </div>
        </section>

        {error ? <section className="message-card error-card" role="alert"><strong>Analysis unavailable</strong><p>{error}</p><button type="button" onClick={() => { void loadItems(); }}>Retry catalogue</button></section> : null}

        {analysis ? <>
          <section className="summary-grid" aria-label="Evidence summary">
            <MetricCard label="Data quality" value={<StatusBadge status={analysis.data_quality.status} />} detail={`${number(analysis.data_quality.row_count)} source rows profiled`} />
            <MetricCard label="Latest observed median" value={latest ? money(latest.observed_price, unit) : "Unavailable"} detail={latest ? `${number(latest.transaction_count)} observations · ${number(latest.premise_count)} premises` : "No qualified daily point"} />
            <MetricCard label="Latest expected price" value={latestExpected ? money(latestExpected, unit) : "Unavailable"} detail={analysis.forecast?.chosen_model ? `${analysis.forecast.chosen_model} selected by validation` : "Model not eligible"} />
            <MetricCard label="Review status" value={<StatusBadge status={analysis.report.critic_status} />} detail={analysis.report.recommendation ? "Human review may be warranted" : "No approved recommendation"} />
          </section>

          <section className="analysis-grid" id="evidence">
            <article className="panel chart-panel">
              <PanelHeading eyebrow="Daily evidence" title="Observed versus expected price" action={unit ? `RM / ${unit}` : "Unit pending"} />
              {points.length ? <PriceChart points={points} anomalies={analysis.anomalies} unit={unit} /> : <EmptyState text="No qualified daily series was produced for this scope." />}
            </article>
            <article className="panel verdict-panel">
              <PanelHeading eyebrow="Reliability assessment" title="Critic verdict" />
              <StatusBadge status={analysis.report.critic_status} large />
              <div className="claim-list"><h3>Approved claims</h3>{analysis.report.approved_claims.length ? analysis.report.approved_claims.map((claim) => <p key={claim}><CheckGlyph />{claim}</p>) : <p>No claim was approved.</p>}</div>
              {analysis.report.recommendation ? <div className="recommendation"><span>Approved next step</span><p>{analysis.report.recommendation}</p></div> : null}
              <p className="disclaimer">This tool does not determine inflation, causes of price changes, or wrongdoing.</p>
            </article>
          </section>

          <section className="secondary-grid">
            <article className="panel"><PanelHeading eyebrow="Model evidence" title="Baseline comparison" />
              <div className="model-grid"><ModelCard label="Historical baseline" metrics={analysis.forecast?.baseline_test ?? null} selected={analysis.forecast?.chosen_model === "baseline"} /><ModelCard label="Ridge regression" metrics={analysis.forecast?.ridge_test ?? null} selected={analysis.forecast?.chosen_model === "ridge"} /></div>
              <p className="panel-note">{analysis.forecast?.selection_reason ?? "No chronological model comparison was eligible."}</p>
            </article>
            <article className="panel"><PanelHeading eyebrow="Coverage gate" title="Data support" />
              <CoverageBars points={points} />
              <p className="panel-note">Dates below the configured transaction and premise thresholds are excluded from forecasting and anomaly scoring.</p>
            </article>
          </section>

          <section className="panel table-panel"><PanelHeading eyebrow="Held-out residuals" title="Anomaly evidence" action={analysis.anomaly_method ? `${analysis.anomaly_method} · threshold ${analysis.anomaly_threshold}` : undefined} />
            {analysis.anomalies.length ? <div className="table-wrap"><table><thead><tr><th>Date</th><th>Observed</th><th>Expected</th><th>Residual</th><th>Score</th><th>Transactions</th><th>Premises</th><th>Status</th></tr></thead><tbody>{analysis.anomalies.map((anomaly) => <tr key={`${anomaly.date}-${anomaly.anomaly_score}`}><td>{formatDate(anomaly.date)}</td><td>{money(anomaly.observed_price, unit)}</td><td>{money(anomaly.expected_price, unit)}</td><td>{signedMoney(anomaly.residual, unit)}</td><td className="mono">{anomaly.anomaly_score.toFixed(2)}</td><td>{number(anomaly.transaction_count)}</td><td>{number(anomaly.premise_count)}</td><td><span className="review-label">Requires review</span></td></tr>)}</tbody></table></div> : <EmptyState text="No coverage-qualified held-out residual crossed the configured anomaly threshold." />}
          </section>

          <section className="panel agent-panel"><PanelHeading eyebrow="Specialist workflow" title="Agent evidence trail" />
            <div className="agent-timeline">{analysis.agents.map((agent, index) => <article className="agent-step" key={agent.agent}><span className="agent-number">{String(index + 1).padStart(2, "0")}</span><div><div className="agent-title"><h3>{titleCase(agent.agent)}</h3><StatusBadge status={agent.status} /></div>{agent.findings[0] ? <p>{agent.findings[0].statement}</p> : <p>{agent.limitations[0] ?? "No additional evidence artifact was generated."}</p>}</div></article>)}</div>
          </section>

          <details className="methodology" id="methodology"><summary><span><span className="eyebrow">Methodology and provenance</span><strong>Inspect the evidence boundary and source references</strong></span><ChevronGlyph /></summary><div className="method-content"><div><h3>Method</h3><p>PricePulse aggregates a single official item and verified unit into daily median prices, gates weak coverage, evaluates chronological baseline and Ridge candidates, then scores held-out residuals using a robust MAD method.</p></div><div><h3>Source files</h3><ul>{analysis.data_quality.source_artifacts.map((source) => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.name}</a><span>{source.status} · {source.row_count ? number(source.row_count) + " rows" : "row count unavailable"}</span></li>)}</ul></div><div><h3>Limitations</h3><ul>{analysis.report.limitations.map((limit) => <li key={limit}>{limit}</li>)}</ul></div></div></details>
        </> : <section className="empty-workspace"><span className="empty-icon"><ChartGlyph /></span><h2>Start with a verified price series</h2><p>Select one official item, a geography, and an analysis window. The system will show only source-backed results after its data, model, anomaly, and critic gates complete.</p></section>}
      </main>
    </div>
  );
}

function PriceChart({ points, anomalies, unit }: { points: DailyPoint[]; anomalies: AnalysisPayload["anomalies"]; unit?: string }) {
  return <div className="chart-wrap"><ResponsiveContainer width="100%" height={332}><LineChart data={points} margin={{ top: 12, right: 18, bottom: 4, left: 4 }}><CartesianGrid stroke="#EAECF0" vertical={false} /><XAxis dataKey="date" tickFormatter={shortDate} minTickGap={34} tick={{ fill: "#667085", fontSize: 12 }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => `RM ${value}`} tick={{ fill: "#667085", fontSize: 12 }} axisLine={false} tickLine={false} width={58} /><Tooltip content={<PriceTooltip unit={unit} />} /><Line type="monotone" dataKey="observed_price" name="Observed median" stroke="#155EEF" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} connectNulls /><Line type="monotone" dataKey="baseline_expected" name="Expected value" stroke="#7F56D9" strokeWidth={2} strokeDasharray="5 5" dot={false} connectNulls />{anomalies.map((anomaly) => <ReferenceDot key={`${anomaly.date}-dot`} x={anomaly.date} y={anomaly.observed_price} r={5} fill="#D92D20" stroke="#fff" strokeWidth={2} />)}</LineChart></ResponsiveContainer><div className="chart-legend"><span><i className="legend-line observed" />Observed daily median</span><span><i className="legend-line expected" />Historical expectation</span><span><i className="legend-dot" />Qualified anomaly</span></div></div>;
}

function PriceTooltip({ active, payload, label, unit }: { active?: boolean; payload?: Array<{ name: string; value: number; payload: DailyPoint }>; label?: string; unit?: string }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return <div className="chart-tooltip"><strong>{formatDate(label ?? "")}</strong><p>Observed <span>{money(point.observed_price, unit)}</span></p><p>Expected <span>{point.baseline_expected ? money(point.baseline_expected, unit) : "Unavailable"}</span></p><p>Transactions <span>{number(point.transaction_count)}</span></p><p>Premises <span>{number(point.premise_count)}</span></p></div>;
}

function MetricCard({ label, value, detail }: { label: string; value: ReactNode; detail: string }) { return <article className="metric-card"><p>{label}</p><strong>{value}</strong><span>{detail}</span></article>; }
function PanelHeading({ eyebrow, title, action }: { eyebrow: string; title: string; action?: string }) { return <div className="panel-heading"><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div>{action ? <span className="panel-action">{action}</span> : null}</div>; }
function ModelCard({ label, metrics, selected }: { label: string; metrics: ModelMetrics | null | undefined; selected: boolean }) { return <article className={selected ? "model-card is-selected" : "model-card"}><div><span>{label}</span>{selected ? <em>Selected</em> : null}</div>{metrics ? <><strong className="mono">MAE {metrics.mae.toFixed(3)}</strong><p className="mono">RMSE {metrics.rmse.toFixed(3)} · n={metrics.sample_size}</p></> : <p>Not eligible or not selected for held-out evaluation.</p>}</article>; }
function CoverageBars({ points }: { points: DailyPoint[] }) { if (!points.length) return <EmptyState text="No daily coverage evidence is available." />; const max = Math.max(...points.map((point) => point.transaction_count), 1); return <div className="coverage-bars">{points.slice(-28).map((point) => <div key={point.date} title={`${point.date}: ${point.transaction_count} transactions`}><span style={{ height: `${Math.max(8, (point.transaction_count / max) * 100)}%` }} className={point.coverage_qualified ? "qualified-bar" : "unqualified-bar"} /></div>)}</div>; }
function EmptyState({ text }: { text: string }) { return <div className="empty-state"><p>{text}</p></div>; }
function StatusBadge({ status, large = false }: { status: DecisionStatus; large?: boolean }) { return <span className={`status-badge status-${status.toLowerCase()}${large ? " is-large" : ""}`}><i />{status.replaceAll("_", " ")}</span>; }
function NavGlyph({ path }: { path: string }) { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d={path} /></svg>; }
function ArrowGlyph() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" /></svg>; }
function CheckGlyph() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>; }
function ChevronGlyph() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>; }
function ChartGlyph() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19V5M4 19h16M8 16l3-4 3 2 5-7" /></svg>; }
function messageFor(error: unknown) { return error instanceof Error ? error.message : "An unexpected request error occurred."; }
function toDateInput(value: Date) { return value.toISOString().slice(0, 10); }
function money(value: number, unit?: string) { return `RM ${value.toFixed(2)}${unit ? ` / ${unit}` : ""}`; }
function signedMoney(value: number, unit?: string) { return `${value >= 0 ? "+" : "−"}${money(Math.abs(value), unit)}`; }
function number(value: number) { return new Intl.NumberFormat("en-MY").format(value); }
function shortDate(value: string) { return new Intl.DateTimeFormat("en-MY", { month: "short", day: "numeric" }).format(new Date(value)); }
function formatDate(value: string) { return new Intl.DateTimeFormat("en-MY", { year: "numeric", month: "short", day: "numeric" }).format(new Date(value)); }
function titleCase(value: string) { return value.split("_").map((word) => word[0].toUpperCase() + word.slice(1)).join(" "); }

export default App;
