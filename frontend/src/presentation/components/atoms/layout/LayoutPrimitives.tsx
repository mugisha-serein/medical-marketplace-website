import React from 'react';

/**
 * SECTION PRIMITIVE
 * Standardizes vertical rhythm and semantic sectioning.
 * Uses spacing tokens: py-16 (64px) -> py-24 (96px) -> py-32 (128px)
 */
interface SectionProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
  variant?: 'white' | 'slate' | 'primary' | 'transparent';
  noPadding?: boolean;
}

export const Section = ({
  children,
  className = '',
  id,
  variant = 'transparent',
  noPadding = false
}: SectionProps) => {
  const variants = {
    white: 'bg-white',
    slate: 'bg-surface-muted',
    primary: 'bg-primary text-text-inverse',
    transparent: 'bg-transparent'
  };

  const padding = noPadding ? '' : 'py-16 md:py-24 lg:py-32';

  return (
    <section
      id={id}
      className={`${variants[variant]} ${padding} ${className} relative overflow-hidden`}
    >
      {children}
    </section>
  );
};

/**
 * CONTAINER PRIMITIVE
 * Standardizes horizontal alignment and responsive width control.
 * Uses spacing tokens: px-4 (16px) -> px-12 (48px) -> px-24 (96px)
 */
interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  size?: 'default' | 'narrow' | 'full';
}

export const Container = ({
  children,
  className = '',
  size = 'default'
}: ContainerProps) => {
  const sizes = {
    default: 'max-w-screen-2xl mx-auto px-4 md:px-12 lg:px-24',
    narrow: 'max-w-4xl mx-auto px-4 md:px-12 lg:px-24',
    full: 'w-full px-4 md:px-12 lg:px-24'
  };

  return (
    <div className={`${sizes[size]} ${className}`}>
      {children}
    </div>
  );
};

/**
 * GRID PRIMITIVE
 * Standardizes responsive layout patterns with consistent gutters.
 */
interface GridProps {
  children: React.ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4 | 12;
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  alignItems?: 'start' | 'center' | 'end';
}

export const Grid = ({
  children,
  className = '',
  cols = 3,
  gap = 'lg',
  alignItems = 'start'
}: GridProps) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    12: 'grid-cols-1 lg:grid-cols-12'
  };

  const gaps = {
    sm: 'gap-4',
    md: 'gap-6 md:gap-8',
    lg: 'gap-8 lg:gap-12',
    xl: 'gap-12 lg:gap-24'
  };

  const alignments = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end'
  };

  return (
    <div className={`grid ${gridCols[cols]} ${gaps[gap]} ${alignments[alignItems]} ${className}`}>
      {children}
    </div>
  );
};

