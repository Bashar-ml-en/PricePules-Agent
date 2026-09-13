const lifecycle = [
  ["01", "Authorised data", "A retailer connects read-only order, product, inventory, and supplier data."],
  ["02", "Evidence gates", "The connector validates identity, units, coverage, timestamps, and snapshot versions."],
  ["03", "Forecast lifecycle", "A baseline and eligible ML candidates are evaluated chronologically and registered."],
  ["04", "Decision review", "Specialists assess demand, inventory risk, impact, and policy before a planner sees a case."],
  ["05", "Measured learning", "Actual demand, reviewer outcomes, error, and drift guide controlled retraining."],
];

const questions = [
  ["Why", "Retail teams need a reliable way to prioritise stockout and excess-inventory risk from fragmented operational data."],
  ["What", "RetailOps ML will produce evidence-backed forecast and inventory-risk cases for human review."],
  ["How", "Versioned connector data moves through deterministic validation, time-safe modelling, specialist gates, and a policy critic."],
  ["Impact", "A pilot measures forecast error, qualified cases, planner response time, stockout days, and excess inventory against a declared baseline."],
];

export default function App() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">Retail demand and inventory decision support</p>
        <h1>RetailOps ML</h1>
        <p className="lede">
          A trustworthy multi-agent ML lifecycle for helping retail planners
          decide what demand and inventory case deserves attention next.
        </p>
        <div className="status">
          <span>Foundation stage</span>
          <p>No merchant connector, forecast, stockout score, or purchasing action is active yet.</p>
        </div>
      </section>

      <section className="question-grid" aria-label="Product questions">
        {questions.map(([title, detail]) => (
          <article className="question-card" key={title}>
            <p>{title}</p>
            <h2>{detail}</h2>
          </article>
        ))}
      </section>

      <section className="lifecycle">
        <div className="section-heading">
          <p className="eyebrow">Controlled lifecycle</p>
          <h2>From authorised data to human-approved action</h2>
        </div>
        <ol>
          {lifecycle.map(([number, title, detail]) => (
            <li key={number}>
              <span>{number}</span>
              <div>
                <h3>{title}</h3>
                <p>{detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="guardrails">
        <div>
          <p className="eyebrow">Non-negotiable guardrails</p>
          <h2>Evidence before automation</h2>
        </div>
        <ul>
          <li>Connector access is authorised, tenant-scoped, and read-only by default.</li>
          <li>Each model decision is reproducible from versioned snapshots and chronology-safe evaluation.</li>
          <li>Agents have narrow authority; the Policy Critic can stop an unsafe or unsupported case.</li>
          <li>Only a human can approve a purchase, transfer, or other operational action.</li>
        </ul>
      </section>
    </main>
  );
}
