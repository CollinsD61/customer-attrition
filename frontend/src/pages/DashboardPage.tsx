import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart as RePieChart, Pie, Cell, Legend,
} from 'recharts';
import { Users, TrendingUp, AlertTriangle, Activity } from 'lucide-react';

import type { DashboardSummary, TrendPoint, RiskDistribution, Customer } from '../types';
import { dashboardService } from '../services/dashboard';
import { customersService } from '../services/customers';
import { KpiCard } from '../components/dashboard/KpiCard';
import { Card } from '../components/ui/Card';
import { PageSpinner } from '../components/ui/Spinner';
import { RiskBadge } from '../components/customers/RiskBadge';

const RISK_COLORS: Record<string, string> = {
  HIGH: '#EF4444',
  MEDIUM: '#F59E0B',
  LOW: '#10B981',
};

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistribution | null>(null);
  const [topCustomers, setTopCustomers] = useState<Customer[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function fetchAll() {
      try {
        const [summaryData, trendData, distData, customersData] = await Promise.all([
          dashboardService.getSummary(),
          dashboardService.getTrend(),
          dashboardService.getRiskDistribution(),
          customersService.list({ sort_by: 'churn_risk_score', sort_order: 'desc', page_size: 10 }),
        ]);
        if (cancelled) return;
        setSummary(summaryData);
        setTrend(trendData);
        setRiskDist(distData);
        setTopCustomers(customersData.items);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchAll();
    return () => { cancelled = true; };
  }, []);

  const pieData = useMemo(() => {
    if (!riskDist) return [];
    return [
      { name: 'High', value: riskDist.high, color: RISK_COLORS.HIGH },
      { name: 'Medium', value: riskDist.medium, color: RISK_COLORS.MEDIUM },
      { name: 'Low', value: riskDist.low, color: RISK_COLORS.LOW },
    ];
  }, [riskDist]);

  if (loading) return <PageSpinner />;

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-text-muted">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-[24px] font-semibold text-text">Dashboard</h1>
        <p className="text-[14px] text-text-muted mt-0.5">Customer churn risk overview</p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        <KpiCard
          label="Total Customers"
          value={summary?.total_customers ?? 0}
          icon={Users}
        />
        <KpiCard
          label="Churn Rate"
          value={`${(summary?.churn_rate ?? 0).toFixed(1)}%`}
          icon={TrendingUp}
          trend={{ value: 'vs last month', positive: false }}
        />
        <KpiCard
          label="At Risk"
          value={summary?.at_risk_count ?? 0}
          icon={AlertTriangle}
        />
        <KpiCard
          label="Avg Risk"
          value={`${(summary?.avg_risk_score ?? 0).toFixed(1)}%`}
          icon={Activity}
        />
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <Card title="Churn Trend (30 Days)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="churn_rate" stroke="#3B82F6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="col-span-1">
          <Card title="Risk Distribution">
            <ResponsiveContainer width="100%" height={250}>
              <RePieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Legend />
              </RePieChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </div>

      <Card title="Top 10 Priority Customers">
        <div className="overflow-x-auto">
          <table className="w-full text-[14px]">
            <thead>
              <tr className="text-left text-text-muted border-b border-border">
                <th className="pb-3 font-medium">Customer ID</th>
                <th className="pb-3 font-medium">Tenure</th>
                <th className="pb-3 font-medium">Contract</th>
                <th className="pb-3 font-medium">Risk Score</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {topCustomers.map((c) => (
                <tr key={c.customer_id} className="border-b border-border/50 hover:bg-surface/50">
                  <td className="py-3 text-text">{c.customer_id}</td>
                  <td className="py-3 text-text-secondary">{c.tenure} mo</td>
                  <td className="py-3 text-text-secondary">{c.contract_type}</td>
                  <td className="py-3 text-text-secondary">{c.churn_risk_score.toFixed(1)}%</td>
                  <td className="py-3"><RiskBadge status={c.risk_status} /></td>
                  <td className="py-3 text-right">
                    <Link to={`/customers/${c.customer_id}`} className="text-primary hover:underline text-[13px]">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
              {topCustomers.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-text-muted">No customers found</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}