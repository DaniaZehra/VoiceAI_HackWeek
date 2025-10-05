'use client';

import { ButtonHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface GlowButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  loading?: boolean;
}

export default function GlowButton({ children, loading, className, disabled, ...rest }: GlowButtonProps) {
  const isDisabled = disabled || loading;
  return (
    <button
      disabled={isDisabled}
      className={clsx(
        'relative inline-flex items-center justify-center px-5 py-3 rounded-xl font-semibold',
        'bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-500 text-white',
        'shadow-glow hover:shadow-glow focus:outline-none focus:ring-2 focus:ring-blue-300',
        'transition-all duration-300 hover:-translate-y-0.5',
        'before:absolute before:inset-0 before:rounded-xl before:bg-[linear-gradient(110deg,rgba(255,255,255,.25),rgba(255,255,255,.1),rgba(255,255,255,.25))] before:bg-[length:200%_100%] before:animate-shimmer',
        'disabled:opacity-60 disabled:cursor-not-allowed',
        className,
      )}
      {...rest}
    >
      <span className="relative z-10 flex items-center gap-2">
        {loading && (
          <span className="inline-block h-4 w-4 rounded-full border-2 border-white border-r-transparent animate-spin" />
        )}
        {children}
      </span>
    </button>
  );
}


