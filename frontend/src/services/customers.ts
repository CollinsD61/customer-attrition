import { api } from './api';
import type { Customer, CustomerDetail, RiskAnalysis, CustomerFilters, PaginatedResponse } from '../types';

export const customersService = {
  list: (filters: CustomerFilters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== '') params.set(k, String(v));
    });
    return api.get<PaginatedResponse<Customer>>(`/customers?${params}`);
  },
  getById: (id: string) => api.get<CustomerDetail>(`/customers/${id}`),
  getRisk: (id: string) => api.get<RiskAnalysis>(`/customers/${id}/risk`),
  export: () => api.post<Blob>('/customers/export'),
};