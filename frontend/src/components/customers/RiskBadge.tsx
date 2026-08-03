import { Badge } from '../ui/Badge';
import type { BadgeVariant } from '../ui/Badge';

const riskVariant: Record<string, BadgeVariant> = {
  LOW: 'low', MEDIUM: 'medium', HIGH: 'high',
};

export function RiskBadge({ status }: { status: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`w-2 h-2 rounded-full ${status === 'LOW' ? 'bg-risk-low' : status === 'MEDIUM' ? 'bg-risk-medium' : 'bg-risk-high'}`} />
      <Badge variant={riskVariant[status] || 'neutral'}>
        {status} RISK
      </Badge>
    </span>
  );
}