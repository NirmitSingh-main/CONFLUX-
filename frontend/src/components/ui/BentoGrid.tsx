import React from "react";
import { cn } from "../../lib/utils";

export const BentoGrid = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <div
      className={cn(
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-w-7xl mx-auto auto-rows-[14rem]",
        className
      )}
    >
      {children}
    </div>
  );
};

export const BentoGridItem = ({
  className,
  title,
  description,
  header,
  icon,
  onClick,
  id,
  statusBadge,
  statusColor = "neutral",
}: {
  className?: string;
  title?: string | React.ReactNode;
  description?: string | React.ReactNode;
  header?: React.ReactNode;
  icon?: React.ReactNode;
  onClick?: () => void;
  id?: string;
  statusBadge?: string;
  statusColor?: "nominal" | "warning" | "critical" | "neutral" | "cyan";
}) => {
  const getBadgeStyle = () => {
    switch (statusColor) {
      case "nominal":
        return "bg-emerald-500/10 text-emerald-500 border-emerald-500/25";
      case "warning":
        return "bg-amber-500/10 text-amber-500 border-amber-500/25";
      case "critical":
        return "bg-rose-500/10 text-rose-500 border-rose-500/25";
      case "cyan":
        return "bg-theme-cyan-subtle text-[#00D1FF] border-theme-cyan";
      default:
        return "bg-theme-card-sub text-theme-muted border-theme-subtle";
    }
  };

  return (
    <div
      id={id}
      onClick={onClick}
      className={cn(
        "row-span-1 rounded-2xl group/bento transition duration-200 p-5 bg-theme-card border border-theme-subtle hover:border-theme-hover justify-between flex flex-col space-y-3 cursor-pointer relative overflow-hidden backdrop-blur-md",
        onClick && "hover:scale-[1.01] active:scale-[0.99]",
        className
      )}
    >
      <div className="flex items-start justify-between z-10">
        <div className="flex items-center gap-2.5">
          {icon && (
            <div className="p-2 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-secondary group-hover/bento:text-[#00D1FF] transition-colors">
              {icon}
            </div>
          )}
          <div>
            <div className="font-mono text-xs uppercase tracking-wider text-theme-muted">
              {title}
            </div>
          </div>
        </div>

        {statusBadge && (
          <span
            className={cn(
              "text-[10px] font-mono font-semibold px-2.5 py-0.5 rounded-full border tracking-wider",
              getBadgeStyle()
            )}
          >
            {statusBadge}
          </span>
        )}
      </div>

      <div className="flex-1 flex flex-col justify-center z-10">
        {header}
      </div>

      {description && (
        <div className="text-xs text-theme-muted font-sans tracking-wide z-10 border-t border-theme-subtle pt-2.5 flex items-center justify-between">
          <span>{description}</span>
          <span className="text-[10px] text-[#00D1FF] opacity-90 group-hover:opacity-100 font-mono transition-all">
            Inspect →
          </span>
        </div>
      )}
    </div>
  );
};
