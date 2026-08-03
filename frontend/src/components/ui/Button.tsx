import { Link, LinkProps } from 'react-router-dom';

type As = 'button' | 'link';

type ButtonBaseProps = {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children: React.ReactNode;
};

type ButtonAsButton = ButtonBaseProps & { as?: 'button' } & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'>;
type ButtonAsLink = ButtonBaseProps & { as: 'link' } & LinkProps;

type ButtonProps = ButtonAsButton | ButtonAsLink;

const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary-dark',
  secondary: 'border border-border text-text hover:bg-surface-tertiary',
  ghost: 'text-text-secondary hover:bg-surface-tertiary',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-[13px] rounded-lg',
  md: 'px-4 py-2 text-[14px] rounded-lg',
  lg: 'px-6 py-3 text-[15px] rounded-xl',
};

export function Button({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonProps) {
  const classes = `inline-flex items-center gap-2 font-medium transition-colors duration-150 cursor-pointer ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  if (props.as === 'link') {
    const { as, ...linkProps } = props;
    return <Link {...linkProps} className={classes}>{children}</Link>;
  }

  const { as, ...buttonProps } = props as ButtonAsButton;
  return <button {...buttonProps} className={classes}>{children}</button>;
}