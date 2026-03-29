import React, { useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "motion/react";
import { cn } from "../../lib/utils";

interface MagicCardProps {
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
  gradientSize?: number;
  gradientColor?: string;
  gradientOpacity?: number;
  key?: React.Key;
}

export function MagicCard({
  children,
  className,
  contentClassName,
  gradientSize = 200,
  gradientColor = "#6366f1",
  gradientOpacity = 0.2,
}: MagicCardProps) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  return (
    <div
      onMouseMove={handleMouseMove}
      className={cn(
        "group relative flex size-full overflow-hidden rounded-xl border border-white/10 bg-gray-950 text-white",
        className
      )}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px transition duration-300 group-hover:opacity-100"
        style={{
          background: useTransform(
            [mouseX, mouseY],
            ([x, y]) =>
              `radial-gradient(${gradientSize}px circle at ${x}px ${y}px, ${gradientColor}, transparent 100%)`
          ),
          opacity: gradientOpacity,
        }}
      />
      <div className={cn("relative z-10 w-full h-full", contentClassName)}>{children}</div>
    </div>
  );
}

export function MagicGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", className)}>
      {children}
    </div>
  );
}
