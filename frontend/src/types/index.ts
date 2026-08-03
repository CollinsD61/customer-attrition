export interface Customer {
  customer_id: string;
  tenure: number;
  contract_type: string;
  monthly_spend: number;
  churn_risk_score: number;
  risk_status: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface CustomerDetail extends Customer {
  demographics: {
    age: number;
    gender: string;
    education: string;
    marital_status: string;
    dependents: number;
  };
  financials: {
    credit_score: number | null;
    annual_income: number;
    monthly_charges: number;
    total_charges: number;
    payment_method: string;
  };
  signup_date: string;
  paperless_billing: boolean;
  senior_citizen: boolean;
}

export interface ServiceSubscription {
  name: string;
  active: boolean;
}

export interface BehavioralKPI {
  label: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
}

export interface ShapDriver {
  feature: string;
  impact: number;
  direction: 'positive' | 'negative';
}

export interface RiskAnalysis {
  score: number;
  status: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
  shap_drivers: ShapDriver[];
  behavioral_kpis: BehavioralKPI[];
  services: ServiceSubscription[];
  metadata: {
    inference_latency_ms: number;
    model_version: string;
    feature_store: string;
    feature_freshness_minutes: number;
  };
}

export interface DashboardSummary {
  total_customers: number;
  churn_rate: number;
  at_risk_count: number;
  avg_risk_score: number;
}

export interface TrendPoint {
  date: string;
  churn_rate: number;
}

export interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CustomerFilters {
  risk_status?: string;
  contract_type?: string;
  tenure_min?: number;
  tenure_max?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}