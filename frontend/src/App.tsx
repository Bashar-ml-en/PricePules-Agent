import { useEffect, useMemo, useState } from "react";

import { fetchSystemBlueprint, hasBlueprintApi } from "./api";
import { fallbackBlueprint } from "./blueprint";
import type { BlueprintState, SystemBlueprint } from "./types";

function displayState(state: BlueprintState): string {
  return state.replaceAll("_", " ").toLowerCase();
}

export default function App() {
  const [blueprint, setBlueprint] = useState<SystemBlueprint>(fallbackBlueprint);
  const [source, setSource] = useState(
    hasBlueprintApi ? "Connecting blueprint API" : "Embedded architecture blueprint",
  );
  const [selectedStageId, setSelectedStageId] = useState(fallbackBlueprint.stages[0].id);

  useEffect(() => {
    if (!hasBlueprintApi) {
      return;
    }

    let isCurrent = true;

    fetchSystemBlueprint()
      .then((nextBlueprint) => {
        if (isCurrent) {
          setBlueprint(nextBlueprint);
          setSource("API blueprint connected");
        }
      })
      .catch(() => {
        if (isCurrent) {
          setSource("Local foundation blueprint — API unavailable");
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  const selectedStage = useMemo(
    () => blueprint.stages.find((stage) => stage.id === selectedStageId) ?? blueprint.stages[0],
    [blueprint.stages, selectedStageId],
  );
  const parallelAgents = blueprint.agents.filter((agent) => agent.parallel_group === "evidence-review");
  const gateAgents = blueprint.agents.filter((agent) => agent.parallel_group === "release-gate");

  return (
    <main className="control-room">
      <header className="topbar">
        <a className="brand" href="#overview">RetailOps<span>ML</span></a>
        <p>System blueprint</p>
        <span className="api-source">{source}</span>
      </header>

      <section className="hero" id="overview">
        <div>
          <p className="eyebrow">Evidence-first retail operations</p>
          <h1>See the system before it runs.</h1>
          <p className="lede">
            This control room makes the intended multi-agent ML lifecycle inspectable:
            what is implemented, what is designed, and which gates must exist before a
            production decision can be trusted.
          </p>
        </div>
        <div className="run-truth" aria-label="Current execution state">
          <span className="signal" aria-hidden="true" />
          <div>
            <p>Live workloads</p>
            <strong>{blueprint.live_workloads === "NONE" ? "None" : blueprint.live_workloads}</strong>
            <small>This is an architecture explorer, not a simulated live run.</small>
          </div>
        </div>
      </section>

      <section className="reality-grid" aria-label="Current maturity">
        <article className="reality-card real">
          <p className="card-kicker">Implemented now</p>
          <h2>Foundation controls are real</h2>
          <ul>
            {blueprint.truthful_status.implemented_now.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </article>
        <article className="reality-card next">
          <p className="card-kicker">Requires the next build stages</p>
          <h2>Production workloads are not yet active</h2>
          <ul>
            {blueprint.truthful_status.not_running_yet.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </article>
      </section>

      <section className="architecture-section" aria-labelledby="flow-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">System flow</p>
            <h2 id="flow-heading">One traceable path from data to planner decision</h2>
          </div>
          <p>Choose a stage to inspect its owner and hand-off.</p>
        </div>

        <div className="flow-frame">
          <div className="stage-flow" aria-label="RetailOps system stages">
            {blueprint.stages.map((stage, index) => (
              <button
                className={`stage-node ${stage.id === selectedStage.id ? "is-selected" : ""}`}
                key={stage.id}
                onClick={() => setSelectedStageId(stage.id)}
                type="button"
              >
                <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>
                <strong>{stage.title}</strong>
                <em className={`state state-${stage.state.toLowerCase()}`}>{displayState(stage.state)}</em>
              </button>
            ))}
          </div>
          <aside className="stage-detail" aria-live="polite">
            <p className="card-kicker">Selected hand-off</p>
            <h3>{selectedStage.title}</h3>
            <dl>
              <div><dt>Owner</dt><dd>{selectedStage.owner}</dd></div>
              <div><dt>Required output</dt><dd>{selectedStage.output}</dd></div>
              <div><dt>Readiness</dt><dd>{displayState(selectedStage.state)}</dd></div>
            </dl>
          </aside>
        </div>
      </section>

      <section className="agents-section" aria-labelledby="agents-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Deterministic specialist layer</p>
            <h2 id="agents-heading">The evidence specialists can run in parallel</h2>
          </div>
          <p>Parallel work does not bypass the critic or a human approval.</p>
        </div>

        <div className="agent-orchestration">
          <div className="parallel-block">
            <div className="parallel-label"><span>Parallel review group</span><small>Same versioned input scope</small></div>
            <div className="agent-grid">
              {parallelAgents.map((agent) => (
                <article className="agent-card" key={agent.id}>
                  <div className="agent-card-head"><span className="agent-dot" /><em>{displayState(agent.state)}</em></div>
                  <h3>{agent.name}</h3>
                  <p>{agent.responsibility}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="convergence" aria-label="Evidence converges at policy gate">
            <span>Evidence bundles</span><b>↓</b><strong>Policy gate</strong>
          </div>

          <div className="gate-block">
            {gateAgents.map((agent) => (
              <article className="gate-card" key={agent.id}>
                <em className={`state state-${agent.state.toLowerCase()}`}>{displayState(agent.state)}</em>
                <h3>{agent.name}</h3>
                <p>{agent.responsibility}</p>
              </article>
            ))}
            <article className="human-card">
              <p className="card-kicker">Irreplaceable final authority</p>
              <h3>Retail planner approval</h3>
              <p>Only a human can approve or reject an operational action draft.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="lifecycle-section" aria-labelledby="lifecycle-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">ML lifecycle</p>
            <h2 id="lifecycle-heading">Training, testing, promotion, and learning are separate gates</h2>
          </div>
          <p>No future information enters a historical validation split.</p>
        </div>
        <ol className="lifecycle-steps">
          {blueprint.lifecycle.map((step, index) => (
            <li key={step}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{step}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="controls-section" aria-labelledby="controls-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Reliability envelope</p>
            <h2 id="controls-heading">The links that make a production system accountable</h2>
          </div>
          <p>Every release and retraining decision must leave an audit trail.</p>
        </div>
        <div className="controls-grid">
          {blueprint.controls.map((control) => (
            <article className="control-card" key={control.title}>
              <em className={`state state-${control.state.toLowerCase()}`}>{displayState(control.state)}</em>
              <h3>{control.title}</h3>
              <p>{control.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="impact-band">
        <div>
          <p className="eyebrow">Meaningful impact</p>
          <h2>Make better inventory decisions with proof, not automation theatre.</h2>
        </div>
        <p>
          A pilot must measure forecast error, qualified review cases, planner response time,
          stockout days, and excess inventory against a declared baseline. If the data or model
          proof is incomplete, the system returns an inconclusive result instead of an action.
        </p>
      </section>
    </main>
  );
}
