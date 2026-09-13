export type DecisionStatus =
  | "PASS"
  | "PASS_WITH_LIMITATIONS"
  | "REJECT"
  | "INCONCLUSIVE";

export type CatalogueItem = {
  item_code: number;
  item: string;
  unit: string;
  item_group?: string | null;
  item_category?: string | null;
};

export type SourceArtifact = {
  name: string;
  url: string;
  retrieved_at: string;
  status: string;
  row_count?: number | null;
  error?: string | null;
};

export type QualityIssue = {
  code: string;
  severity: "INFO" | "LIMITATION" | "BLOCKER";
  message: string;
  count?: number | null;
};

export type DailyPoint = {
  date: string;
  observed_price: number;
  q1_price: number;
  q3_price: number;
  transaction_count: number;
  premise_count: number;
  coverage_qualified: boolean;
  baseline_expected?: number | null;
  baseline_method?: string | null;
};

export type ModelMetrics = {
  mae: number;
  rmse: number;
  sample_size: number;
};

export type Forecast = {
  status: "PASS" | "INCONCLUSIVE";
  chosen_model: "baseline" | "ridge" | null;
  selection_reason: string;
  feature_names: string[];
  split_dates: Record<string, [string | null, string | null]>;
  baseline_validation?: ModelMetrics | null;
  baseline_test?: ModelMetrics | null;
  ridge_validation?: ModelMetrics | null;
  ridge_test?: ModelMetrics | null;
  limitations: string[];
  predictions: DailyPoint[];
};

export type Anomaly = {
  date: string;
  observed_price: number;
  expected_price: number;
  residual: number;
  anomaly_score: number;
  transaction_count: number;
  premise_count: number;
  selected_model: string;
  is_anomaly: boolean;
};

export type AgentDecision = {
  agent: string;
  status: DecisionStatus;
  findings: Array<{ statement: string; evidence_refs: string[] }>;
  limitations: string[];
};

export type AnalysisPayload = {
  run_id: string;
  created_at: string;
  scope: {
    item_code: number;
    geography_type: "national" | "state" | "district";
    geography_value?: string | null;
    start_date: string;
    end_date: string;
    min_transactions: number;
    min_premises: number;
    anomaly_threshold: number;
  };
  data_quality: {
    status: DecisionStatus;
    row_count: number;
    date_range: [string | null, string | null];
    source_artifacts: SourceArtifact[];
    issues: QualityIssue[];
  };
  series?: {
    item_code: number;
    item_name: string;
    unit: string;
    geography_type: string;
    geography_value?: string | null;
    status: "PASS" | "INCONCLUSIVE";
    exclusions: Record<string, number>;
    limitations: string[];
    points: DailyPoint[];
  } | null;
  forecast?: Forecast | null;
  anomalies: Anomaly[];
  anomaly_method?: string | null;
  anomaly_threshold?: number | null;
  agents: AgentDecision[];
  critic: {
    status: DecisionStatus;
    approved_claims?: string[];
    rejected_claims?: string[];
    limitations: string[];
  };
  report: {
    critic_status: DecisionStatus;
    approved_claims: string[];
    rejected_claims: string[];
    limitations: string[];
    recommendation?: string | null;
    agent_statuses: Record<string, DecisionStatus>;
  };
};
