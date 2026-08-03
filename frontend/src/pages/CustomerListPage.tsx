import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Download, Filter, ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';
import type { Customer, CustomerFilters, PaginatedResponse } from '../types';
import { customersService } from '../services/customers';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { PageSpinner } from '../components/ui/Spinner';
import { RiskBadge } from '../components/customers/RiskBadge';

const PAGE_SIZE = 20;

const CONTRACT_OPTIONS = ['All', 'Month-to-month', 'One Year', 'Two Year'];
const RISK_OPTIONS = ['All', 'Low', 'Medium', 'High'];

export default function CustomerListPage() {
  const [data, setData] = useState<PaginatedResponse<Customer> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState('');
  const [riskStatus, setRiskStatus] = useState('All');
  const [contractType, setContractType] = useState('All');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<string>('churn_risk_score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const filters: CustomerFilters = {
      page,
      page_size: PAGE_SIZE,
      search: search || undefined,
      risk_status: riskStatus !== 'All' ? riskStatus.toUpperCase() : undefined,
      contract_type: contractType !== 'All' ? contractType : undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    };

    customersService
      .list(filters)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load customers');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [search, riskStatus, contractType, page, sortBy, sortOrder]);

  const toggleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setPage(1);
  };

  const handleExport = () => {
    customersService.export();
  };

  const totalPages = data?.total_pages ?? 1;
  const from = data ? (data.page - 1) * data.page_size + 1 : 0;
  const to = data ? Math.min(data.page * data.page_size, data.total) : 0;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-[24px] font-semibold text-text">Customers</h1>
        <p className="text-[14px] text-text-muted mt-1">Priority list for retention intervention</p>
      </div>

      <Card className="mb-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="text"
              placeholder="Search by Customer ID..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-64 pl-10 pr-4 py-2 border border-border rounded-xl text-[14px] text-text bg-surface placeholder:text-text-muted focus:outline-none focus:border-primary"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
            <select
              value={riskStatus}
              onChange={(e) => { setRiskStatus(e.target.value); setPage(1); }}
              className="pl-10 pr-4 py-2 border border-border rounded-xl text-[14px] text-text bg-surface appearance-none cursor-pointer focus:outline-none focus:border-primary"
            >
              {RISK_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt} Risk</option>
              ))}
            </select>
          </div>

          <select
            value={contractType}
            onChange={(e) => { setContractType(e.target.value); setPage(1); }}
            className="px-4 py-2 border border-border rounded-xl text-[14px] text-text bg-surface appearance-none cursor-pointer focus:outline-none focus:border-primary"
          >
            {CONTRACT_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt === 'All' ? 'All Contracts' : opt}</option>
            ))}
          </select>

          <div className="ml-auto">
            <Button variant="secondary" onClick={handleExport}>
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
        </div>
      </Card>

      {loading && <PageSpinner />}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-[14px]">
          {error}
        </div>
      )}

      {!loading && !error && data && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  {[
                    { key: 'customer_id', label: 'Customer ID' },
                    { key: 'tenure', label: 'Tenure (months)' },
                    { key: 'contract_type', label: 'Contract Type' },
                    { key: 'monthly_spend', label: 'Monthly Spend' },
                    { key: 'churn_risk_score', label: 'Risk Score' },
                    { key: 'risk_status', label: 'Risk Status' },
                  ].map((col) => (
                    <th
                      key={col.key}
                      className="text-[12px] font-semibold text-text-muted uppercase tracking-wider text-left pb-3 px-4"
                    >
                      <button
                        type="button"
                        className="inline-flex items-center gap-1 hover:text-text cursor-pointer"
                        onClick={() => toggleSort(col.key)}
                      >
                        {col.label}
                        <ArrowUpDown className="w-3 h-3" />
                      </button>
                    </th>
                  ))}
                  <th className="text-[12px] font-semibold text-text-muted uppercase tracking-wider text-left pb-3 px-4">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((customer) => (
                  <tr
                    key={customer.customer_id}
                    className="border-b border-border-light hover:bg-surface-tertiary transition-colors"
                  >
                    <td className="px-4 py-3 text-[14px] text-text font-medium">
                      {customer.customer_id}
                    </td>
                    <td className="px-4 py-3 text-[14px] text-text">
                      {customer.tenure}
                    </td>
                    <td className="px-4 py-3 text-[14px] text-text">
                      <Badge variant="neutral">{customer.contract_type}</Badge>
                    </td>
                    <td className="px-4 py-3 text-[14px] text-text font-medium">
                      ${customer.monthly_spend.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 text-[14px] text-text">
                      {(customer.churn_risk_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-3">
                      <RiskBadge status={customer.risk_status} />
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        as="link"
                        to={`/customers/${customer.customer_id}`}
                        variant="ghost"
                        size="sm"
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border-light">
            <p className="text-[14px] text-text-muted">
              Showing {from} to {to} of {data.total} customers
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-[14px] text-text px-2">
                {page} / {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}