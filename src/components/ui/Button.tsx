import React from 'react';
import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import { cn } from '../../utils/cn';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading,
  className,
  children,
  ...props
}) => {
  const variants = {
    primary: 'bg-blue-600 text-white shadow-lg shadow-blue-500/25 hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-slate-100 hover:bg-slate-300 dark:hover:bg-slate-700',
    outline: 'border-2 border-slate-200 dark:border-slate-800 bg-transparent hover:border-blue-500 dark:hover:border-blue-400 text-slate-700 dark:text-slate-300',
    ghost: 'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400',
    danger: 'bg-red-500 text-white hover:bg-red-600 shadow-lg shadow-red-500/20',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs rounded-lg',
    md: 'px-5 py-2.5 text-sm rounded-xl font-semibold',
    lg: 'px-8 py-4 text-lg rounded-2xl font-bold',
  };

  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      disabled={isLoading || props.disabled}
      className={cn(
        'inline-flex items-center justify-center gap-2 transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : null}
      {children}
    </motion.button>
  );
};
