import { useEffect, useRef, useState, useMemo } from "react";
import createGlobe from "cobe";
import type { COBEOptions, Marker, Arc } from "cobe";
import { cn } from "../../lib/utils";
import { useMission } from "../../context/MissionContext";

export interface GlobeMarker {
  location: [number, number]; // [lat, lon]
  size: number;
  color?: [number, number, number];
  id?: string;
  label?: string;
}

export interface GlobeArc {
  from: [number, number];
  to: [number, number];
  color?: [number, number, number];
  id?: string;
}

export interface GlobeConfig {
  dark?: number;
  scale?: number;
  diffuse?: number;
  mapSamples?: number;
  mapBrightness?: number;
  baseColor?: [number, number, number];
  markerColor?: [number, number, number];
  glowColor?: [number, number, number];
  arcColor?: [number, number, number];
  opacity?: number;
}

export interface GlobeProps {
  className?: string;
  config?: GlobeConfig;
  markers?: GlobeMarker[];
  arcs?: GlobeArc[];
  autoRotateSpeed?: number;
  interactive?: boolean;
}

// Major global aerospace telemetry stations & launch sites
export const DEFAULT_SPACEPORTS: GlobeMarker[] = [
  { location: [28.5721, -80.648], size: 0.08, label: "Kennedy Space Center", color: [0.0, 0.9, 1.0] },
  { location: [34.742, -120.572], size: 0.06, label: "Vandenberg Space Base", color: [0.0, 0.8, 1.0] },
  { location: [5.237, -52.768], size: 0.07, label: "Guiana Space Centre", color: [0.2, 0.7, 1.0] },
  { location: [45.965, 63.305], size: 0.07, label: "Baikonur Cosmodrome", color: [0.0, 0.9, 1.0] },
  { location: [30.400, 130.97], size: 0.06, label: "Tanegashima Space Center", color: [0.0, 0.8, 1.0] },
  { location: [13.733, 80.235], size: 0.06, label: "Satish Dhawan Centre", color: [0.0, 0.85, 1.0] },
  { location: [-35.401, 148.981], size: 0.06, label: "Canberra Deep Space", color: [0.1, 0.7, 1.0] },
  { location: [78.229, 15.407], size: 0.05, label: "Svalbard Ground Station", color: [0.3, 0.8, 1.0] },
];

// Orbital communication & downlink relay arcs
export const DEFAULT_ORBITAL_ARCS: GlobeArc[] = [
  { from: [28.5721, -80.648], to: [5.237, -52.768], color: [0.0, 0.82, 1.0] },
  { from: [5.237, -52.768], to: [78.229, 15.407], color: [0.0, 0.65, 0.95] },
  { from: [45.965, 63.305], to: [13.733, 80.235], color: [0.0, 0.82, 1.0] },
  { from: [13.733, 80.235], to: [-35.401, 148.981], color: [0.0, 0.75, 1.0] },
  { from: [30.400, 130.97], to: [34.742, -120.572], color: [0.0, 0.85, 1.0] },
  { from: [34.742, -120.572], to: [28.5721, -80.648], color: [0.0, 0.8, 1.0] },
];

export function Globe({
  className,
  config = {},
  markers: markersProp,
  arcs: arcsProp,
  autoRotateSpeed = 0.003,
  interactive = true,
}: GlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const pointerInteracting = useRef<number | null>(null);
  const pointerInteractionMovement = useRef(0);
  const [webglSupported, setWebglSupported] = useState(true);

  // Read theme and active mission from context
  const { theme, activeMission } = useMission();
  const isDark = theme !== "light";

  // Add a mission-specific accent marker when a mission is active
  const markers = useMemo<GlobeMarker[]>(() => {
    const base = markersProp ?? DEFAULT_SPACEPORTS;
    if (!activeMission) return base;
    // Deterministically pick a "mission home" spaceport based on mission id
    const missionIdx = (activeMission.id - 1) % DEFAULT_SPACEPORTS.length;
    return base.map((m, i) =>
      i === missionIdx
        ? { ...m, size: 0.13, color: [0.95, 0.55, 0.05] as [number, number, number] } // amber accent for active mission
        : m
    );
  }, [markersProp, activeMission?.id]);

  const arcs = arcsProp ?? DEFAULT_ORBITAL_ARCS;

  const {
    dark = isDark ? 1 : 0,
    diffuse = isDark ? 1.3 : 1.1,
    mapSamples = 16000,
    mapBrightness = isDark ? 6 : 4,
    baseColor = isDark ? [0.05, 0.08, 0.14] : [0.92, 0.94, 0.98],
    markerColor = isDark ? [0.0, 0.82, 1.0] : [0.02, 0.52, 0.85],
    glowColor = isDark ? [0.0, 0.35, 0.65] : [0.8, 0.88, 0.96],
    arcColor = isDark ? [0.0, 0.82, 1.0] : [0.05, 0.55, 0.9],
    opacity = isDark ? 0.95 : 0.9,
  } = config;

  useEffect(() => {
    let phi = 0;
    let width = 0;
    let globeInstance: { update: (opts: Partial<COBEOptions>) => void; destroy: () => void } | null = null;
    let animationFrameId: number;

    const updateSize = () => {
      if (containerRef.current) {
        width = containerRef.current.clientWidth || 360;
      } else if (canvasRef.current) {
        width = canvasRef.current.clientWidth || 360;
      } else {
        width = 360;
      }
    };

    updateSize();

    if (!canvasRef.current) return;

    try {
      const initialWidth = width > 0 ? width : 360;

      const opts: COBEOptions = {
        devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
        width: initialWidth * 2,
        height: initialWidth * 2,
        phi: 0,
        theta: 0.22,
        dark,
        diffuse,
        mapSamples,
        mapBrightness,
        baseColor,
        markerColor,
        glowColor,
        opacity,
        offset: [0, 0],
        markers: markers as Marker[],
        arcs: arcs as Arc[],
        arcColor,
        arcWidth: 0.6,
        arcHeight: 0.2,
      };

      globeInstance = createGlobe(canvasRef.current, opts);

      const render = () => {
        if (!pointerInteracting.current) {
          phi += autoRotateSpeed;
        }

        const currentPhi = phi + pointerInteractionMovement.current;

        // Smoothly decay drag momentum when released
        if (pointerInteracting.current === null && Math.abs(pointerInteractionMovement.current) > 0.0005) {
          phi += pointerInteractionMovement.current;
          pointerInteractionMovement.current *= 0.92;
        }

        if (globeInstance) {
          globeInstance.update({
            phi: currentPhi,
            width: (width > 0 ? width : 360) * 2,
            height: (width > 0 ? width : 360) * 2,
          });
        }

        animationFrameId = requestAnimationFrame(render);
      };

      animationFrameId = requestAnimationFrame(render);

      // Fade in smoothly once initialized
      if (canvasRef.current) {
        canvasRef.current.style.opacity = "1";
      }
    } catch (err) {
      console.warn("WebGL globe initialization exception:", err);
      setWebglSupported(false);
    }

    const handleResize = () => {
      updateSize();
    };

    window.addEventListener("resize", handleResize);

    let resizeObserver: ResizeObserver | null = null;
    if (typeof ResizeObserver !== "undefined" && containerRef.current) {
      resizeObserver = new ResizeObserver(() => {
        updateSize();
      });
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      window.removeEventListener("resize", handleResize);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      if (globeInstance) {
        globeInstance.destroy();
      }
    };
  }, [
    dark,
    diffuse,
    mapSamples,
    mapBrightness,
    autoRotateSpeed,
    markers,
    arcs,
    baseColor,
    markerColor,
    glowColor,
    arcColor,
    opacity,
  ]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative flex items-center justify-center w-full aspect-square max-w-[420px] mx-auto select-none",
        className
      )}
    >
      {/* Outer ambient glow halo behind the 3D globe */}
      <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_center,rgba(0,209,255,0.18)_0%,rgba(0,85,255,0.06)_50%,transparent_70%)] pointer-events-none blur-xl" />

      {webglSupported ? (
        <canvas
          ref={canvasRef}
          onPointerDown={(e) => {
            if (!interactive) return;
            pointerInteracting.current =
              e.clientX - pointerInteractionMovement.current;
            if (canvasRef.current) {
              canvasRef.current.style.cursor = "grabbing";
            }
          }}
          onPointerUp={() => {
            if (!interactive) return;
            pointerInteracting.current = null;
            if (canvasRef.current) {
              canvasRef.current.style.cursor = "grab";
            }
          }}
          onPointerOut={() => {
            if (!interactive) return;
            pointerInteracting.current = null;
            if (canvasRef.current) {
              canvasRef.current.style.cursor = "grab";
            }
          }}
          onMouseMove={(e) => {
            if (!interactive || pointerInteracting.current === null) return;
            const delta = e.clientX - pointerInteracting.current;
            pointerInteractionMovement.current = delta * 0.008;
          }}
          onTouchStart={(e) => {
            if (!interactive || !e.touches[0]) return;
            pointerInteracting.current =
              e.touches[0].clientX - pointerInteractionMovement.current;
          }}
          onTouchEnd={() => {
            if (!interactive) return;
            pointerInteracting.current = null;
          }}
          onTouchMove={(e) => {
            if (!interactive || pointerInteracting.current === null || !e.touches[0]) return;
            const delta = e.touches[0].clientX - pointerInteracting.current;
            pointerInteractionMovement.current = delta * 0.008;
          }}
          className={cn(
            "w-full h-full opacity-0 transition-opacity duration-700",
            interactive ? "cursor-grab" : "cursor-default"
          )}
          style={{
            width: "100%",
            height: "100%",
            contain: "layout paint size",
          }}
        />
      ) : (
        <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center border border-[#1F1F23] rounded-full bg-[#0D0D10]/80">
          <div className="w-32 h-32 rounded-full border border-[#00D1FF]/40 border-dashed animate-spin flex items-center justify-center">
            <div className="w-20 h-20 rounded-full bg-[#00D1FF]/10 border border-[#00D1FF]/60" />
          </div>
          <span className="mt-4 text-xs font-mono text-[#00D1FF] uppercase tracking-wider">
            Space Mission Context Grid
          </span>
        </div>
      )}
    </div>
  );
}

export const WorldGlobe = Globe;
export default Globe;
