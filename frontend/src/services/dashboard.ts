import { api } from './api';
import type { DashboardSummary, TrendPoint, RiskDistribution } from '../types';

export const dashboardService = {
  getSummary: () => api.get<DashboardSummary>('/dashboard/summary'),
  getTrend: () => api.get<TrendPoint[]>('/dashboard/trend'),
  getRiskDistribution: () => api.get<RiskDistribution>('/dashboard/risk-distribution'),
};