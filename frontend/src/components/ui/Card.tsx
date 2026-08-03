export function Card({ title, subtitle, className = '', children, action }: {
  title?: string;
  subtitle?: string;
  className?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className={`bg-surface border border-border rounded-2xl p-6 ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && <h3 className="text-[18px] font-semibold text-text">{title}</h3>}
            {subtitle && <p className="text-[13px] text-text-muted mt-0.5">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}