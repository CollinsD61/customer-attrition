export type BadgeVariant = 'low' | 'medium' | 'high' | 'neutral';

const variants: Record<BadgeVariant, string> = {
  low: 'bg-risk-low-bg text-risk-low',
  medium: 'bg-risk-medium-bg text-risk-medium',
  high: 'bg-risk-high-bg text-risk-high',
  neutral: 'bg-surface-tertiary text-text-secondary',
};

export function Badge({ variant = 'neutral', children }: { variant?: BadgeVariant; children: React.ReactNode }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[12px] font-semibold tracking-wide ${variants[variant]}`}>
      {children}
    </span>
  );
}