import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Activity } from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/customers', icon: Users, label: 'Customers' },
  { to: '/predict', icon: Activity, label: 'Predict' },
];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 bottom-0 w-60 bg-surface border-r border-border flex flex-col z-30">
      <div className="px-6 py-5 border-b border-border">
        <span className="text-[18px] font-bold text-primary tracking-tight">RetentionPulse</span>
        <p className="text-[11px] text-text-muted mt-0.5 uppercase tracking-widest">Risk Intelligence</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-[14px] font-medium transition-colors duration-150 cursor-pointer ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-text-secondary hover:bg-surface-tertiary hover:text-text'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-6 py-4 border-t border-border">
        <div className="flex items-center gap-2 text-[12px] text-text-muted">
          <span className="w-2 h-2 rounded-full bg-risk-low animate-pulse" />
          Model: LightGBM v2.1
        </div>
      </div>
    </aside>
  );
}