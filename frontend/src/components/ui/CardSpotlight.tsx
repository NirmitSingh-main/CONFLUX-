import React, { useRef, useState } from "react";
import { cn } from "../../lib/utils";

export const CardSpotlight = ({
  children,
  radius = 300,
  color = "#00D1FF",
  className,
  id,
  variant = "default",
  ...props
}: {
  radius?: number;
  color?: string;
  children: React.ReactNode;
  className?: string;
  id?: string;
  variant?: "default" | "warning" | "critical" | "nominal";
} & React.HTMLAttributes<HTMLDivElement>) => {
  const divRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  // Variant color mapping for spotlight
  const effectiveColor =
    variant === "critical"
      ? "#f43f5e"
      : variant === "warning"
      ? "#f59e0b"
      : variant === "nominal"
      ? "#10b981"
      : color;

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current || isFocused) return;

    const div = divRef.current;
    const rect = div.getBoundingClientRect();

    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  const handleFocus = () => {
    setIsFocused(true);
    setOpacity(1);
  };

  const handleBlur = () => {
    setIsFocused(false);
    setOpacity(0);
  };

  const handleMouseEnter = () => {
    setOpacity(1);
  };

  const handleMouseLeave = () => {
    setOpacity(0);
  };

  return (
    <div
      ref={divRef}
      id={id}
      onMouseMove={handleMouseMove}
      onFocus={handleFocus}
      onBlur={handleBlur}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={cn(
        "relative rounded-2xl border border-theme-subtle bg-theme-card p-6 overflow-hidden backdrop-blur-md transition-all duration-200",
        variant === "critical" && "border-rose-500/40",
        variant === "warning" && "border-amber-500/40",
        variant === "nominal" && "border-emerald-500/40",
        className
      )}
      {...props}
    >
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition-opacity duration-300"
        style={{
          opacity,
          background: `radial-gradient(${radius}px circle at ${position.x}px ${position.y}px, ${effectiveColor}18, transparent 80%)`,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};
