import { BanIcon, LucideIcon } from 'lucide-react';

export function KpiCard({ label, value, icon: Icon = BanIcon, trend }: {
  label: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: { value: string; positive: boolean };
}) {
  return (
    <div className="bg-surface border border-border rounded-2xl p-6 cursor-pointer hover:border-primary/30 transition-colors duration-150">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[13px] font-medium text-text-muted uppercase tracking-wider">{label}</span>
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <div className="text-[36px] font-bold text-text leading-tight tracking-tight">{value}</div>
      {trend && (
        <div className={`flex items-center gap-1 mt-2 text-[13px] ${trend.positive ? 'text-risk-low' : 'text-risk-high'}`}>
          <span>{trend.positive ? '↑' : '↓'}</span>
          <span>{trend.value}</span>
        </div>
      )}
    </div>
  );
}