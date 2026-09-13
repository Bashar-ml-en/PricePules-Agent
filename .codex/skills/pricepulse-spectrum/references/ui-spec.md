# UI direction: analytical command centre

Build a high-trust, modern SaaS dashboard; do not imitate a shopping application, chatbot, or alarm system.

## Tokens

- Headings: Space Grotesk; body: Inter; metrics/dates: JetBrains Mono, each with system fallbacks.
- Shell `#F7F8FA`, surface `#FFFFFF`, dark surface `#101828`, verified blue `#155EEF`, pass `#067647`, limitation `#B54708`, reject `#B42318`, primary text `#101828`, secondary text `#475467`, border `#EAECF0`.
- Use an 8px spacing scale, 12px card/control radii, a 1440px content maximum, subtle borders, and restrained shadows for active overlays only.
- No gradients, glassmorphism, emoji UI icons, or excessive pill treatments. Do not rely on colour alone for status.

## Layout

On desktop, use a slim left rail, a command header, controls, evidence-summary cards, and a 8/4 main grid. Collapse the rail into a mobile top bar and stack the content on smaller screens.

Show: source freshness; validated item/unit; observed versus expected daily price; optional forecast band; anomaly markers; baseline/ML comparison; coverage chart; anomaly evidence table; specialist-agent timeline; critic decision; and an expandable provenance/methodology section.

The chart tooltip must include date, observed and expected price, residual, transaction count, premise count, and unit. Use visual treatments to distinguish unavailable or insufficient-coverage dates from anomalies.

Always state: "This tool does not determine inflation, causes of price changes, or wrongdoing."

## Interaction and accessibility

Do not enable analysis until valid selectors are chosen. Display a concise deterministic progress sequence: Data quality, Baseline, Forecast, Anomaly, Critic. Support focus styles, keyboard navigation, appropriate semantic elements, reduced motion, sufficient contrast, and responsive table-to-card behavior. Use skeletons only for an actual API request.
