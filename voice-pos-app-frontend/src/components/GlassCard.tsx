'use client';

import { ReactNode } from 'react';
import clsx from 'clsx';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export default function GlassCard({ children, className }: GlassCardProps) {
  return (
    <div
      className={clsx(
        'glass gradient-border rounded-2xl shadow-soft-lg hover:shadow-glow transition-all duration-300',
        'hover:-translate-y-0.5 hover:scale-[1.01] animate-float',
        className,
      )}
    >
      {children}
    </div>
  );
}


