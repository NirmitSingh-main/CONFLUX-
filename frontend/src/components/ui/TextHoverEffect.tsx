import { useRef, useEffect, useState } from "react";
import { motion } from "motion/react";
import { cn } from "../../lib/utils";

export const TextHoverEffect = ({
  text,
  duration = 0.3,
  className,
}: {
  text: string;
  duration?: number;
  className?: string;
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [cursor, setCursor] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState(false);
  const [maskPosition, setMaskPosition] = useState({ cx: "50%", cy: "50%" });

  useEffect(() => {
    if (svgRef.current && cursor.x !== null && cursor.y !== null) {
      const svgRect = svgRef.current.getBoundingClientRect();
      const cxPercentage = ((cursor.x - svgRect.left) / svgRect.width) * 100;
      const cyPercentage = ((cursor.y - svgRect.top) / svgRect.height) * 100;
      setMaskPosition({
        cx: `${cxPercentage}%`,
        cy: `${cyPercentage}%`,
      });
    }
  }, [cursor]);

  return (
    <svg
      ref={svgRef}
      width="100%"
      height="100%"
      viewBox="0 0 450 90"
      xmlns="http://www.w3.org/2000/svg"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onMouseMove={(e) => setCursor({ x: e.clientX, y: e.clientY })}
      className={cn("select-none uppercase tracking-[0.25em]", className)}
    >
      <defs>
        <linearGradient
          id="textGradient"
          gradientUnits="userSpaceOnUse"
          cx="50%"
          cy="50%"
          r="25%"
        >
          {hovered && (
            <>
              <stop offset="0%" stopColor={"#06b6d4"} />
              <stop offset="25%" stopColor={"#38bdf8"} />
              <stop offset="50%" stopColor={"#60a5fa"} />
              <stop offset="75%" stopColor={"#06b6d4"} />
              <stop offset="100%" stopColor={"#0891b2"} />
            </>
          )}
        </linearGradient>

        <motion.radialGradient
          id="revealMask"
          gradientUnits="userSpaceOnUse"
          r="28%"
          animate={maskPosition}
          transition={{ duration, ease: "easeOut" }}
        >
          <stop offset="0%" stopColor="white" />
          <stop offset="100%" stopColor="black" />
        </motion.radialGradient>
        <mask id="textMask">
          <rect
            x="0"
            y="0"
            width="100%"
            height="100%"
            fill="url(#revealMask)"
          />
        </mask>
      </defs>

      {/* Background outline */}
      <text
        x="50%"
        y="55%"
        textAnchor="middle"
        dominantBaseline="middle"
        strokeWidth="0.8"
        className="font-mono font-black text-5xl fill-transparent stroke-slate-700/60 dark:stroke-slate-800 tracking-[0.2em]"
        style={{ opacity: hovered ? 0.7 : 0.4 }}
      >
        {text}
      </text>

      {/* Animated base stroke */}
      <motion.text
        x="50%"
        y="55%"
        textAnchor="middle"
        dominantBaseline="middle"
        strokeWidth="0.8"
        className="font-mono font-black text-5xl fill-transparent stroke-cyan-500/40 tracking-[0.2em]"
        initial={{ strokeDashoffset: 1000, strokeDasharray: 1000 }}
        animate={{
          strokeDashoffset: 0,
          strokeDasharray: 1000,
        }}
        transition={{
          duration: 3,
          ease: "easeInOut",
        }}
      >
        {text}
      </motion.text>

      {/* Hover reveal gradient text */}
      <text
        x="50%"
        y="55%"
        textAnchor="middle"
        dominantBaseline="middle"
        stroke="url(#textGradient)"
        strokeWidth="1.2"
        mask="url(#textMask)"
        className="font-mono font-black text-5xl fill-cyan-400/20 tracking-[0.2em]"
      >
        {text}
      </text>
    </svg>
  );
};
