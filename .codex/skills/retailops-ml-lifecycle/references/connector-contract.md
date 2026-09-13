# Connector contract

Before implementing a connector, define product, location, order-line,
inventory-snapshot, inbound-supply, and supplier-term mappings. Record tenant
scope, authorisation, retrieval time, source schema, mapping version, snapshot
hash, quality checks, exclusions, and permitted uses.

Reject unknown SKU/location/unit identities and cross-tenant data. Do not permit
a replenishment draft when current inventory or lead-time evidence is absent or
stale.
