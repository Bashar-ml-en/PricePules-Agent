# RetailOps Experience System

## Purpose

RetailOps is a decision-support control room, not an autonomous-agent demo.
Its interface must make evidence scope, lifecycle gates, delivery maturity, and
human authority clearer than its visual decoration.

## Evidence Grid visual language

- **Tone:** calm, technical, and accountable. Use deep navy surfaces, restrained
  electric-blue structure, amber for planned or cautionary states, and green
  only for policies that are actually enforced.
- **Typography:** a high-contrast, compact sans-serif hierarchy with
  monospace labels for identifiers, states, and release metadata.
- **Composition:** generous dark-space hero, a thin operational status rail,
  inspectable cards, and horizontal flow maps that become scrollable on small
  screens.
- **Motion:** short hover feedback only. Respect `prefers-reduced-motion`; never
  animate a status in a way that could imply a background workload is running.

## Content rules

- “Live”, “ready”, “running”, and success colors require a verified workload
  signal. The foundation uses `ARCHITECTURE_BLUEPRINT` and `Live workloads: None`.
- Every agent card names its deterministic responsibility and lifecycle state.
  It must not claim LLM reasoning, hidden analysis, or an unverified result.
- A planner is the final authority for every inventory, purchase, transfer,
  price, or supplier decision.
- Badges include text labels; color never carries a status meaning alone.

## Delivery checks

- Native controls are keyboard accessible with a visible focus state.
- Long labels, identifiers, and badges reflow at narrow widths.
- Contrast stays readable in dark mode and the layout works from 320px upward.
- The frontend production build and backend contract tests are required before
  a release. A visual refresh never bypasses the ML lifecycle gate.
