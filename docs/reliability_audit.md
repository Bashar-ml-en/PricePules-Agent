# RetailOps ML Lifecycle Audit

Before a release or pilot, verify:

- every connector is authorised, read-only by default, tenant-scoped, and
  versioned;
- raw snapshots, mappings, features, model configurations, metrics, and agent
  decisions are reproducible;
- time splits and feature generation do not leak future data;
- the baseline is retained when no candidate meets promotion criteria;
- inventory and lead-time evidence is current enough for the proposed use;
- Policy Critic blocks unsupported recommendations and autonomous actions;
- demo, synthetic, and public benchmark data cannot be presented as customer
  results;
- reviewer decisions, overrides, monitoring, retraining, and rollback events
  are auditable;
- no customer credentials or personal data are exposed to browser or logs.
