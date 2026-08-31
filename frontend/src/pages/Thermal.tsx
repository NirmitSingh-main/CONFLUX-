import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  Flame,
  Upload,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Image as ImageIcon,
  Crosshair,
  Database,
  Info,
} from "lucide-react";
import { analyzeImagery, getLatestImagery } from "../api/imagery";
import { useMission } from "../context/MissionContext";
import { ImageryResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";
import { ThermalImagePreview } from "../components/common/ThermalImagePreview";

export function Thermal() {
  const {
    activeMission,
    updateImageryResult,
    setInspectPayload,
  } = useMission();

  // Form State — always tracks active mission
  const [missionId, setMissionId] = useState<number>(activeMission?.id ?? 1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // UX State
  const [loading, setLoading] = useState(false);
  const [fetchingLatest, setFetchingLatest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImageryResponse | null>(null);
  const [hasLatest, setHasLatest] = useState<boolean | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Auto-fetch latest from DB on mission switch ───────────────────────
  const fetchLatest = useCallback(async (mid: number) => {
    setFetchingLatest(true);
    setResult(null);
    setError(null);
    setHasLatest(null);
    try {
      const data = await getLatestImagery(mid);
      setResult(data);
      updateImageryResult(data);
      setHasLatest(true);
    } catch (err: any) {
      if (err?.status === 404 || (err?.message || "").includes("404")) {
        setHasLatest(false);
      } else if (err?.status === 0 || (err?.message || "").toLowerCase().includes("network")) {
        setError(err.message);
      } else {
        setHasLatest(false);
      }
    } finally {
      setFetchingLatest(false);
    }
  }, [updateImageryResult]);

  // On mission change: update missionId, clear file selection, fetch latest
  useEffect(() => {
    const mid = activeMission?.id ?? 1;
    setMissionId(mid);
    setSelectedFile(null);
    setPreviewUrl(null);
    fetchLatest(mid);
  }, [activeMission?.id, fetchLatest]);

  const handleFileChange = (file: File) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setResult(null);
    setHasLatest(false);
    setError(null);
  };

  // Helper to generate a realistic sample infrared thermal canvas and convert to File
  const generateSampleInfraredImage = (hasAnomaly: boolean) => {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Background cold space / spacecraft skin (deep blue/purple gradient)
    const bgGrad = ctx.createLinearGradient(0, 0, 256, 256);
    bgGrad.addColorStop(0, "#030712");
    bgGrad.addColorStop(0.5, "#0f172a");
    bgGrad.addColorStop(1, "#1e1b4b");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, 256, 256);

    // Grid lines
    ctx.strokeStyle = "rgba(6, 182, 212, 0.15)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 256; i += 32) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, 256);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(256, i);
      ctx.stroke();
    }

    // Spacecraft Bus Silhouette
    ctx.fillStyle = "rgba(30, 41, 59, 0.8)";
    ctx.fillRect(64, 64, 128, 128);

    // Nominal radiators / thrusters
    const radGrad = ctx.createRadialGradient(128, 128, 10, 128, 128, 50);
    radGrad.addColorStop(0, "rgba(59, 130, 246, 0.6)");
    radGrad.addColorStop(1, "rgba(15, 23, 42, 0)");
    ctx.fillStyle = radGrad;
    ctx.fillRect(64, 64, 128, 128);

    if (hasAnomaly) {
      // Hotspot critical thermal plume
      const hotGrad = ctx.createRadialGradient(160, 100, 2, 160, 100, 35);
      hotGrad.addColorStop(0, "#ffffff");
      hotGrad.addColorStop(0.2, "#fde047");
      hotGrad.addColorStop(0.5, "#ea580c");
      hotGrad.addColorStop(0.8, "#dc2626");
      hotGrad.addColorStop(1, "rgba(220, 38, 38, 0)");
      ctx.fillStyle = hotGrad;
      ctx.beginPath();
      ctx.arc(160, 100, 35, 0, Math.PI * 2);
      ctx.fill();
    }

    canvas.toBlob((blob) => {
      if (blob) {
        const fileName = hasAnomaly ? "thermal_infrared_hotspot.png" : "thermal_infrared_nominal.png";
        const file = new File([blob], fileName, { type: "image/png" });
        handleFileChange(file);
      }
    }, "image/png");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError("Please select or generate an infrared/thermal image file first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await analyzeImagery(Number(missionId), selectedFile);
      setResult(response);
      updateImageryResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to analyze thermal imagery.");
    } finally {
      setLoading(false);
    }
  };

  // Helper to parse coordinates from hottest_location
  const parseCoordinates = (loc: any): { x: number; y: number } | null => {
    if (!loc) return null;
    if (Array.isArray(loc) && loc.length >= 2) {
      return { x: loc[0], y: loc[1] };
    }
    if (typeof loc === "object") {
      if (loc.x !== undefined && loc.y !== undefined) {
        return { x: loc.x, y: loc.y };
      }
      if (loc.col !== undefined && loc.row !== undefined) {
        return { x: loc.col, y: loc.row };
      }
    }
    if (typeof loc === "string") {
      const match = loc.match(/\(?\s*(\d+)\s*,\s*(\d+)\s*\)?/);
      if (match) {
        return { x: parseInt(match[1]), y: parseInt(match[2]) };
      }
    }
    return null;
  };

  const coords = result ? parseCoordinates(result.hottest_location) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Flame className="w-5 h-5 text-[#00D1FF]" />
            Thermal & Infrared Imagery Analysis
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Is there a thermal/infrared anomaly? Upload spacecraft radiometric frames to detect hotspots.
          </p>
        </div>

        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Target Endpoint: <code className="text-[#00D1FF]">POST /thermal/ (multipart)</code>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Upload & Form */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Upload className="w-4 h-4 text-[#00D1FF]" />
                Upload Radiometric Image
              </h3>
              <span className="text-[10px] font-mono text-[#00D1FF]/90">
                Mission #{missionId}
              </span>
            </div>

            {/* Quick Sample Generators */}
            <div className="mb-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Load Sample Infrared Test Frames:
              </span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => generateSampleInfraredImage(false)}
                  className="px-3 py-2 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-secondary border border-theme-subtle hover:border-[#00D1FF]/40 transition-colors text-left"
                >
                  <div className="text-emerald-500 font-semibold">• Nominal Bus</div>
                  <div className="text-[10px] text-theme-muted">Uniform Radiator</div>
                </button>
                <button
                  type="button"
                  onClick={() => generateSampleInfraredImage(true)}
                  className="px-3 py-2 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-secondary border border-theme-subtle hover:border-[#00D1FF]/40 transition-colors text-left"
                >
                  <div className="text-rose-500 font-semibold">• Thermal Plume</div>
                  <div className="text-[10px] text-theme-muted">Hotspot Anomaly</div>
                </button>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Error:</span> {error}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                  MISSION ID
                </label>
                <input
                  id="thermal-mission-id"
                  type="number"
                  value={missionId}
                  onChange={(e) => setMissionId(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              {/* Drag and Drop Zone */}
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                  INFRARED / THERMAL IMAGE FILE
                </label>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
                  className="hidden"
                />

                <div
                  id="dropzone-thermal"
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragOver(true);
                  }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragOver(false);
                    if (e.dataTransfer.files?.[0]) {
                      handleFileChange(e.dataTransfer.files[0]);
                    }
                  }}
                  onClick={() => fileInputRef.current?.click()}
                  className={`p-6 rounded-2xl border-2 border-dashed text-center cursor-pointer transition-all ${dragOver
                      ? "border-[#00D1FF] bg-[#00D1FF]/10"
                      : selectedFile
                        ? "border-theme-subtle bg-theme-input"
                        : "border-theme-subtle hover:border-[#00D1FF]/40 bg-theme-input"
                    }`}
                >
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="p-3 rounded-full bg-theme-card text-[#00D1FF]">
                      <ImageIcon className="w-6 h-6" />
                    </div>
                    {selectedFile ? (
                      <div className="space-y-1">
                        <span className="text-xs font-mono font-semibold text-theme-primary block truncate max-w-xs">
                          {selectedFile.name}
                        </span>
                        <span className="text-[11px] font-mono text-[#00D1FF] block">
                          {(selectedFile.size / 1024).toFixed(1)} KB · Ready to analyze
                        </span>
                      </div>
                    ) : (
                      <div>
                        <span className="text-xs font-mono text-theme-secondary block">
                          Click to browse or drop infrared image here
                        </span>
                        <span className="text-[10px] text-theme-muted font-mono mt-0.5 block">
                          PNG, JPG, TIFF, or Radiometric matrix
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <button
                  id="submit-thermal-btn"
                  type="submit"
                  disabled={loading || !selectedFile}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Processing Image Pixels...</span>
                  ) : (
                    <>
                       <Flame className="w-4 h-4 text-[#00D1FF]" />
                       <span>Analyze Infrared (POST /thermal/)</span>
                     </>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-4 p-3 rounded-xl bg-theme-card-sub border border-theme-subtle text-[11px] text-theme-muted flex items-start gap-2">
              <Info className="w-3.5 h-3.5 text-theme-muted shrink-0 mt-0.5" />
              <span>
                Note: Raw infrared intensity analysis is evaluated directly via the backend threshold algorithm. Uncalibrated imagery is evaluated on pixel relative intensities.
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Thermal Heatmap Preview & Hotspot Metrics */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Card Spotlight for Anomaly Status */}
              <CardSpotlight
                id="thermal-verdict-spotlight"
                variant={result.anomaly_detected ? "critical" : "nominal"}
                className="bg-theme-card border-theme-subtle"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2.5 rounded-xl border ${result.anomaly_detected ? "bg-rose-500/20 text-rose-500 border-rose-500/40" : "bg-emerald-500/20 text-emerald-500 border-emerald-500/40"}`}>
                      {result.anomaly_detected ? (
                        <AlertOctagon className="w-6 h-6 animate-pulse" />
                      ) : (
                        <CheckCircle2 className="w-6 h-6" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border ${result.anomaly_detected
                            ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                            : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                          }`}>
                          {result.anomaly_detected ? "THERMAL ANOMALY" : "THERMAL NOMINAL"}
                        </span>
                        <span className="text-xs font-mono text-theme-muted">
                          {result.filename}
                        </span>
                      </div>

                      <h3 className={`text-xl font-mono font-bold mt-1.5 ${result.anomaly_detected ? "text-rose-500" : "text-emerald-500"}`}>
                        {result.anomaly_detected ? "INFRARED HOTSPOT DETECTED" : "UNIFORM THERMAL DISTRIBUTION"}
                      </h3>

                      <p className="text-xs text-theme-secondary font-sans mt-1">
                        {result.anomaly_detected
                          ? `Hotspot pixels exceeded radiometric threshold with a ratio of ${(result.hotspot_ratio * 100).toFixed(2)}%.`
                          : "Radiometric pixel intensity variance remains within acceptable operating boundaries."}
                      </p>
                    </div>
                  </div>

                  <button
                    id="inspect-thermal-json-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: "Thermal Imagery Response",
                        data: result,
                      })
                    }
                    className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
                  >
                    Raw Output
                  </button>
                </div>
              </CardSpotlight>

              {/* Image Preview with Hotspot Crosshair Overlay */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-2">
                    RADIOMETRIC FRAME PREVIEW
                  </span>
                  <ThermalImagePreview
                    src={previewUrl}
                    hotspot={coords}
                  />
                </div>

                {/* Hotspot Target Details */}
                <div className="space-y-3">
                  <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block">HOTTEST INTENSITY</span>
                    <span className="text-2xl font-mono font-bold text-rose-500">
                      {result.hottest_intensity}
                    </span>
                    <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                      Threshold limit: {result.threshold}
                    </span>
                  </div>

                  <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block">HOTTEST LOCATION</span>
                    <div className="text-base font-mono font-bold text-[#00D1FF] flex items-center gap-1.5">
                      <Crosshair className="w-4 h-4 text-[#00D1FF]" />
                      <span>
                        {typeof result.hottest_location === "object"
                          ? JSON.stringify(result.hottest_location)
                          : String(result.hottest_location)}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                      Pixel coordinates
                    </span>
                  </div>

                  <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block">HOTSPOT PIXELS & RATIO</span>
                    <div className="text-base font-mono font-bold text-theme-primary">
                      {result.hotspot_pixels} px <span className="text-xs text-theme-muted font-normal">({(result.hotspot_ratio * 100).toFixed(2)}%)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Statistics Grid */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                    Radiometric Distribution Parameters
                  </h4>
                  <span className="text-[11px] font-mono text-theme-muted flex items-center gap-1">
                    <Database className="w-3 h-3 text-[#00D1FF]" />
                    <span>Database: {result.stored_in_database ? "Persisted" : "Evaluated"}</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">MEAN INTENSITY</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.mean_intensity === "number" ? result.mean_intensity.toFixed(2) : result.mean_intensity}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">STD DEVIATION</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.standard_deviation === "number" ? result.standard_deviation.toFixed(2) : result.standard_deviation}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">DETECTION THRESHOLD</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {result.threshold}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">HOTSPOT RATIO</span>
                    <span className="text-sm font-mono font-bold text-[#00D1FF]">
                      {typeof result.hotspot_ratio === "number" ? (result.hotspot_ratio * 100).toFixed(3) + "%" : result.hotspot_ratio}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : fetchingLatest ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
              <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
                <Flame className="w-4 h-4 animate-pulse text-[#00D1FF]" />
                <span>Loading latest thermal for Mission #{missionId}…</span>
              </div>
            </div>
          ) : hasLatest === false ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Flame className="w-8 h-8 text-theme-muted/40" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Not Analyzed — Mission #{missionId}
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                No thermal analysis found for this mission. Upload an infrared image and click <strong>Analyze Infrared</strong> to create one.
              </p>
            </div>
          ) : (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Flame className="w-8 h-8 text-[#00D1FF]/50" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Awaiting Infrared Frame
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                Upload a thermal imagery capture or select a sample frame and click &quot;Analyze Infrared&quot; to detect radiometric anomalies on the FastAPI backend.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
