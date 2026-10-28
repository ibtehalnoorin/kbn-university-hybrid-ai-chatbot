import React from 'react';

export default function Button({
  children,
  onClick,
  variant = 'primary', // primary, secondary, danger, ghost
  size = 'md', // sm, md, lg
  disabled = false,
  className = '',
  type = 'button',
  icon: Icon
}) {
  const baseClasses =
    'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-electric disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-electric hover:bg-electric-bright text-white shadow-sm',
    secondary: 'bg-amethyst-deep hover:bg-surface text-primaryText border border-borderCol',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    ghost: 'bg-transparent hover:bg-amethyst-deep text-secondaryText hover:text-primaryText'
  };

  const sizes = {
    sm: 'px-2.5 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base'
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {Icon && <Icon className={`w-4 h-4 ${children ? 'mr-2' : ''}`} />}
      {children}
    </button>
  );
}
