import { useEffect, useRef, useState } from "react";
import { Image as ImageIcon } from "lucide-react";
import { cn } from "../../lib/utils";

interface HotspotCoordinate {
  x: number;
  y: number;
}

interface ThermalImagePreviewProps {
  src: string | null;
  hotspot?: HotspotCoordinate | null;
  alt?: string;
  className?: string;
}

interface ImageProjection {
  left: number;
  top: number;
}

export function ThermalImagePreview({
  src,
  hotspot,
  alt = "Thermal Frame",
  className,
}: ThermalImagePreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [projection, setProjection] = useState<ImageProjection | null>(null);

  useEffect(() => {
    if (!src || !hotspot) {
      setProjection(null);
      return;
    }

    const updateProjection = () => {
      const container = containerRef.current;
      const image = imageRef.current;
      if (!container || !image || !image.naturalWidth || !image.naturalHeight) {
        return;
      }

      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
      if (!containerWidth || !containerHeight) return;

      const scale = Math.min(
        containerWidth / image.naturalWidth,
        containerHeight / image.naturalHeight,
      );
      const renderedWidth = image.naturalWidth * scale;
      const renderedHeight = image.naturalHeight * scale;
      const offsetX = (containerWidth - renderedWidth) / 2;
      const offsetY = (containerHeight - renderedHeight) / 2;

      setProjection({
        left: ((offsetX + hotspot.x * scale) / containerWidth) * 100,
        top: ((offsetY + hotspot.y * scale) / containerHeight) * 100,
      });
    };

    updateProjection();
    const image = imageRef.current;
    image?.addEventListener("load", updateProjection);
    const observer = typeof ResizeObserver !== "undefined" && containerRef.current
      ? new ResizeObserver(updateProjection)
      : null;
    if (observer && containerRef.current) observer.observe(containerRef.current);

    return () => {
      image?.removeEventListener("load", updateProjection);
      observer?.disconnect();
    };
  }, [src, hotspot?.x, hotspot?.y]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative aspect-square w-full overflow-hidden rounded-xl border border-theme-subtle bg-theme-input",
        className,
      )}
    >
      {src ? (
        <>
          <img
            ref={imageRef}
            src={src}
            alt={alt}
            className="h-full w-full object-contain"
            onLoad={() => setProjection((current) => current ?? null)}
          />
          {hotspot && projection && (
            <div
              className="pointer-events-none absolute flex -translate-x-1/2 -translate-y-1/2 items-center justify-center"
              style={{ left: `${projection.left}%`, top: `${projection.top}%` }}
            >
              <div className="absolute h-10 w-10 animate-ping rounded-full border-2 border-rose-500" />
              <div className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-rose-400 bg-rose-500/20">
                <div className="h-1.5 w-1.5 rounded-full bg-rose-300" />
              </div>
              <span className="absolute -top-5 whitespace-nowrap rounded border border-rose-800 bg-rose-950 px-1 text-[9px] font-mono text-rose-200">
                HOTSPOT ({hotspot.x}, {hotspot.y})
              </span>
            </div>
          )}
        </>
      ) : (
        <div className="flex h-full w-full items-center justify-center">
          <ImageIcon className="h-12 w-12 text-theme-muted" />
        </div>
      )}
    </div>
  );
}
