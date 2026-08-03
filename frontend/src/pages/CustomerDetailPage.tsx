import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, User, CreditCard, Calendar, CheckCircle2, XCircle,
  Info, Zap, Database, Box,
} from 'lucide-react';
import type { CustomerDetail, RiskAnalysis, ServiceSubscription, BehavioralKPI, ShapDriver } from '../types';
import { customersService } from '../services/customers';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { PageSpinner } from '../components/ui/Spinner';
import { RiskBadge } from '../components/customers/RiskBadge';

const SERVICE_ITEMS = [
  'Phone Service', 'Internet Service', 'Online Security', 'Online Backup',
  'Device Protection', 'Tech Support', 'Streaming TV', 'Streaming Movies',
] as const;

function ServiceIcon({ service }: { service: ServiceSubscription }) {
  if (service.active) {
    return <CheckCircle2 size={18} className="text-[#10B981]" />;
  }
  return <XCircle size={18} className="text-[#EF4444]" />;
}

function ShapBar({ driver }: { driver: ShapDriver }) {
  const pct = Math.abs(driver.impact * 100);
  const color = driver.direction === 'positive' ? '#F59E0B' : '#10B981';
  return (
    <div className="flex items-center gap-3">
      <span className="text-[14px] text-text flex-1 truncate">{driver.feature}</span>
      <div className="flex items-center gap-2">
        <div className="w-20 h-1.5 bg-surface-tertiary rounded-full overflow-hidden">
          <div
            className="h-full rounded-full"
            style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }}
          />
        </div>
        <span className="text-[13px] text-text-secondary w-12 text-right">{pct.toFixed(1)}%</span>
      </div>
    </div>
  );
}

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [customer, setCustomer] = useState<CustomerDetail | null>(null);
  const [risk, setRisk] = useState<RiskAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    Promise.all([
      customersService.getById(id),
      customersService.getRisk(id),
    ])
      .then(([c, r]) => {
        setCustomer(c);
        setRisk(r);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load customer'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <PageSpinner />;

  if (error || !customer || !risk) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <p className="text-text-secondary text-[14px]">{error || 'Customer not found'}</p>
        <Link to="/customers" className="text-primary text-[14px] hover:underline">
          Back to Customer List
        </Link>
      </div>
    );
  }

  const serviceMap = new Map(risk.services.map((s) => [s.name, s]));

  return (
    <div className="space-y-6">
      <Link
        to="/customers"
        className="inline-flex items-center gap-1.5 text-text-secondary hover:text-text text-[14px] transition-colors"
      >
        <ArrowLeft size={16} />
        Back to Customer List
      </Link>

      <div className="grid grid-cols-3 gap-6">
        {/* LEFT COLUMN */}
        <div className="col-span-2 space-y-6">
          {/* Customer Profile */}
          <Card>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary text-[18px] font-semibold">
                {customer.customer_id.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="text-[18px] font-semibold text-text">Account {customer.customer_id}</h3>
                <p className="text-[13px] text-text-muted">Customer Profile</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-8 gap-y-4">
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-text-muted shrink-0" />
                <span className="text-[14px] text-text-muted">Tenure:</span>
                <span className="text-[14px] text-text font-semibold">{customer.tenure} months</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-text-muted shrink-0" />
                <span className="text-[14px] text-text-muted">Signup Date:</span>
                <span className="text-[14px] text-text font-semibold">{customer.signup_date}</span>
              </div>
              <div className="flex items-center gap-2">
                <Box size={16} className="text-text-muted shrink-0" />
                <span className="text-[14px] text-text-muted">Contract:</span>
                <span className="text-[14px] text-text font-semibold">{customer.contract_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[14px] text-text-muted">Paperless Billing:</span>
                <span className="text-[14px] text-text font-semibold">{customer.paperless_billing ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex items-center gap-2">
                <User size={16} className="text-text-muted shrink-0" />
                <span className="text-[14px] text-text-muted">Senior Citizen:</span>
                <span className="text-[14px] text-text font-semibold">{customer.senior_citizen ? 'Yes' : 'No'}</span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <h4 className="text-[14px] font-semibold text-text mb-3">Demographics</h4>
              <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Age:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.demographics.age}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Gender:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.demographics.gender}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Education:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.demographics.education}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Marital Status:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.demographics.marital_status}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Dependents:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.demographics.dependents}</span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <h4 className="text-[14px] font-semibold text-text mb-3">Financials</h4>
              <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                <div className="flex items-center gap-2">
                  <CreditCard size={16} className="text-text-muted shrink-0" />
                  <span className="text-[14px] text-text-muted">Credit Score:</span>
                  <span className="text-[14px] text-text font-semibold">
                    {customer.financials.credit_score ?? '—'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Annual Income:</span>
                  <span className="text-[14px] text-text font-semibold">
                    ${customer.financials.annual_income.toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Monthly Charges:</span>
                  <span className="text-[14px] text-text font-semibold">
                    ${customer.financials.monthly_charges.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[14px] text-text-muted">Total Charges:</span>
                  <span className="text-[14px] text-text font-semibold">
                    ${customer.financials.total_charges.toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center gap-2 col-span-2">
                  <span className="text-[14px] text-text-muted">Payment Method:</span>
                  <span className="text-[14px] text-text font-semibold">{customer.financials.payment_method}</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Active Service Subscriptions */}
          <Card title="Active Service Subscriptions">
            <div className="grid grid-cols-4 gap-4">
              {SERVICE_ITEMS.map((name) => {
                const svc = serviceMap.get(name);
                const active = svc?.active ?? false;
                return (
                  <div
                    key={name}
                    className="p-3 rounded-xl border border-border bg-surface-tertiary flex flex-col items-center gap-2 text-center"
                  >
                    {active ? (
                      <CheckCircle2 size={20} className="text-[#10B981]" />
                    ) : (
                      <XCircle size={20} className="text-[#EF4444]" />
                    )}
                    <span className="text-[13px] text-text font-medium leading-tight">{name}</span>
                    <span className={`text-[12px] font-semibold ${active ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                      {active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          {/* Risk Score */}
          <Card>
            <div className="text-center">
              <div className="text-[48px] font-bold text-text">{risk.score}%</div>
              <div className="mt-2 flex justify-center">
                <RiskBadge status={risk.status} />
              </div>
              <p className="mt-3 text-[14px] text-text-secondary">{risk.description}</p>
              <div className="mt-4 flex items-center justify-center gap-1.5 text-[12px] text-text-muted">
                <Info size={14} />
                Real-time inference via KServe
              </div>
            </div>
          </Card>

          {/* Behavioral Indicators */}
          <Card title="Behavioral Indicators">
            <div className="space-y-3">
              {risk.behavioral_kpis.map((kpi) => (
                <div key={kpi.label} className="flex items-center justify-between">
                  <span className="text-[14px] text-text-muted">{kpi.label}</span>
                  <span className="text-[14px] text-text font-semibold">
                    {kpi.value}{kpi.unit ? ` ${kpi.unit}` : ''}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Top Prediction Drivers (SHAP) */}
          <Card title="Top Prediction Drivers (SHAP)">
            <div className="space-y-4">
              {risk.shap_drivers.map((driver) => (
                <ShapBar key={driver.feature} driver={driver} />
              ))}
            </div>
          </Card>

          {/* Footer Metadata */}
          <div className="bg-surface border border-border rounded-2xl p-4 space-y-2 text-[13px] text-text-muted">
            <div className="flex items-center gap-2">
              <Zap size={14} />
              <span>Inference Latency: {risk.metadata.inference_latency_ms}ms</span>
            </div>
            <div className="flex items-center gap-2">
              <Database size={14} />
              <span>
                Feature Store: {risk.metadata.feature_store}
                {' '}(Freshness: {risk.metadata.feature_freshness_minutes}m)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Box size={14} />
              <span>Model: {risk.metadata.model_version}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}