import React, { useState, useEffect, useCallback } from "react";
import {
  Eye,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Waves,
  Sparkles,
  Database,
  BarChart3,
  Sliders,
  Send,
} from "lucide-react";
import { analyzeWavefront, getLatestWavefront } from "../api/wavefront";
import { useMission } from "../context/MissionContext";
import { WavefrontResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

export function Wavefront() {
  const {
    activeMission,
    updateWavefrontResult,
    setInspectPayload,
  } = useMission();

  // Form State
  const [missionId, setMissionId] = useState<number>(activeMission?.id || 1);
  const [wavefrontRms, setWavefrontRms] = useState<number>(0.045);
  const [tipError, setTipError] = useState<number>(0.012);
  const [tiltError, setTiltError] = useState<number>(0.015);
  const [defocus, setDefocus] = useState<number>(0.020);
  const [astigmatism, setAstigmatism] = useState<number>(0.018);
  const [coma, setComa] = useState<number>(0.009);

  // UX State
  const [loading, setLoading] = useState(false);
  const [fetchingLatest, setFetchingLatest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WavefrontResponse | null>(null);
  const [hasLatest, setHasLatest] = useState<boolean | null>(null);

  // ── Auto-fetch latest from DB on mission switch ───────────────────────
  const fetchLatest = useCallback(async (mid: number) => {
    setFetchingLatest(true);
    setResult(null);
    setError(null);
    setHasLatest(null);
    try {
      const data = await getLatestWavefront(mid);
      setResult(data);
      updateWavefrontResult(data);
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
  }, [updateWavefrontResult]);

  useEffect(() => {
    const mid = activeMission?.id ?? 1;
    setMissionId(mid);
    fetchLatest(mid);
  }, [activeMission?.id, fetchLatest]);

  // Presets
  const presets = [
    {
      label: "Nominal Diffraction-Limited Optics",
      data: { rms: 0.035, tip: 0.008, tilt: 0.010, def: 0.015, ast: 0.012, com: 0.007 },
    },
    {
      label: "Severe Coma & Astigmatism Aberration (Anomaly)",
      data: { rms: 0.285, tip: 0.142, tilt: 0.165, def: 0.080, ast: 0.240, com: 0.310 },
    },
    {
      label: "Thermal Expansion Defocus (Anomaly)",
      data: { rms: 0.195, tip: 0.030, tilt: 0.025, def: 0.350, ast: 0.050, com: 0.040 },
    },
  ];

  const handleApplyPreset = (p: typeof presets[0]) => {
    setWavefrontRms(p.data.rms);
    setTipError(p.data.tip);
    setTiltError(p.data.tilt);
    setDefocus(p.data.def);
    setAstigmatism(p.data.ast);
    setComa(p.data.com);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        mission_id: Number(missionId),
        wavefront_rms_um: Number(wavefrontRms),
        tip_error_um: Number(tipError),
        tilt_error_um: Number(tiltError),
        defocus_um: Number(defocus),
        astigmatism_um: Number(astigmatism),
        coma_um: Number(coma),
      };

      const response = await analyzeWavefront(payload);
      setResult(response);
      updateWavefrontResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to analyze wavefront optical parameters.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Eye className="w-5 h-5 text-[#00D1FF]" />
            Optical Wavefront Intelligence
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Is the optical/wavefront system behaving normally? Zernike aberration coefficients & wavelet decomposition.
          </p>
        </div>

        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Target Endpoint: <code className="text-[#00D1FF]">POST /wavefront/</code>
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Sliders className="w-4 h-4 text-[#00D1FF]" />
                Aberration Vector Inputs (µm)
              </h3>
              <span className="text-[10px] font-mono text-[#00D1FF]/90">
                Mission #{missionId}
              </span>
            </div>

            {/* Presets */}
            <div className="mb-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Load Sample Optical States:
              </span>
              <div className="flex flex-col gap-1.5">
                {presets.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleApplyPreset(p)}
                    className="w-full text-left px-3 py-2 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-secondary border border-theme-subtle hover:border-[#00D1FF]/40 transition-colors flex items-center justify-between"
                  >
                    <span>{p.label}</span>
                    <span className="text-[10px] text-[#00D1FF]/80">Load</span>
                  </button>
                ))}
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

            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                  MISSION ID
                </label>
                <input
                  id="wavefront-mission-id"
                  type="number"
                  value={missionId}
                  onChange={(e) => setMissionId(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                  WAVEFRONT RMS (µm)
                </label>
                <input
                  id="wavefront-rms"
                  type="number"
                  step="0.001"
                  value={wavefrontRms}
                  onChange={(e) => setWavefrontRms(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    TIP ERROR (µm)
                  </label>
                  <input
                    id="wavefront-tip"
                    type="number"
                    step="0.001"
                    value={tipError}
                    onChange={(e) => setTipError(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    TILT ERROR (µm)
                  </label>
                  <input
                    id="wavefront-tilt"
                    type="number"
                    step="0.001"
                    value={tiltError}
                    onChange={(e) => setTiltError(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    DEFOCUS (µm)
                  </label>
                  <input
                    id="wavefront-defocus"
                    type="number"
                    step="0.001"
                    value={defocus}
                    onChange={(e) => setDefocus(Number(e.target.value))}
                    className="w-full px-2.5 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    ASTIGMATISM (µm)
                  </label>
                  <input
                    id="wavefront-astigmatism"
                    type="number"
                    step="0.001"
                    value={astigmatism}
                    onChange={(e) => setAstigmatism(Number(e.target.value))}
                    className="w-full px-2.5 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    COMA (µm)
                  </label>
                  <input
                    id="wavefront-coma"
                    type="number"
                    step="0.001"
                    value={coma}
                    onChange={(e) => setComa(Number(e.target.value))}
                    className="w-full px-2.5 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  id="submit-wavefront-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Decomposing Optical Wavefront...</span>
                  ) : (
                    <>
                      <Send className="w-4 h-4 text-[#00D1FF]" />
                      <span>Evaluate Wavefront (POST /wavefront/)</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column: Grouped Information Results */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Group 1: Overall Result Spotlight */}
              <CardSpotlight
                id="wavefront-verdict-spotlight"
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
                          {result.anomaly_detected ? "OPTICAL ANOMALY" : "OPTICAL NOMINAL"}
                        </span>
                        <span className="text-xs font-mono text-theme-muted">
                          Max Z-Score: {typeof result.max_z_score === "number" ? result.max_z_score.toFixed(3) : result.max_z_score}
                        </span>
                      </div>

                      <h3 className={`text-xl font-mono font-bold mt-1.5 ${result.anomaly_detected ? "text-rose-500" : "text-emerald-500"}`}>
                        {result.anomaly_detected ? "WAVEFRONT ABERRATION DETECTED" : "NOMINAL OPTICAL TRANSMISSION"}
                      </h3>

                      <p className="text-xs text-theme-secondary font-sans mt-1">
                        {result.anomaly_detected
                          ? `Wavefront anomaly score (${result.anomaly_score?.toFixed(3)}) exceeds tolerance limits.`
                          : "Optical wavefront features conform to diffraction-limited threshold."}
                      </p>
                    </div>
                  </div>

                  <button
                    id="inspect-wavefront-json-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: "Wavefront Analysis Output",
                        data: result,
                      })
                    }
                    className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
                  >
                    Raw Output
                  </button>
                </div>
              </CardSpotlight>

              {/* Group 2: Feature Analysis (6 Aberration Scores) */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-[#00D1FF]" />
                    Feature Z-Scores & Optical Vectors
                  </h4>
                  <span className="text-[11px] font-mono text-theme-muted">
                    Anomaly Score: <span className="text-[#00D1FF] font-bold">{result.anomaly_score?.toFixed(4)}</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { label: "Wavefront RMS", key: "wavefront_rms_um", fallback: wavefrontRms },
                    { label: "Tip Error", key: "tip_error_um", fallback: tipError },
                    { label: "Tilt Error", key: "tilt_error_um", fallback: tiltError },
                    { label: "Defocus", key: "defocus_um", fallback: defocus },
                    { label: "Astigmatism", key: "astigmatism_um", fallback: astigmatism },
                    { label: "Coma", key: "coma_um", fallback: coma },
                  ].map((feat) => {
                    const score = result.feature_scores?.[feat.key];
                    return (
                      <div key={feat.key} className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                        <span className="text-[10px] font-mono text-theme-muted block">{feat.label}</span>
                        <div className="text-base font-mono font-bold text-theme-primary mt-0.5">
                          {feat.fallback} µm
                        </div>
                        {score !== undefined && (
                          <div className="text-[11px] font-mono text-[#00D1FF] mt-1">
                            Z: {typeof score === "number" ? score.toFixed(3) : score}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Group 3: Wavelet Analysis */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                    <Waves className="w-4 h-4 text-[#00D1FF]" />
                    Wavelet Energy Decomposition
                  </h4>
                  <span className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full border ${result.wavelet_anomaly
                      ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                      : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                    }`}>
                    {result.wavelet_anomaly ? "WAVELET ANOMALY" : "WAVELET NOMINAL"}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">WAVELET ENERGY</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.wavelet_energy === "number" ? result.wavelet_energy.toFixed(4) : result.wavelet_energy}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">BASELINE ENERGY</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.baseline_energy === "number" ? result.baseline_energy.toFixed(4) : result.baseline_energy}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">ENERGY RATIO</span>
                    <span className="text-sm font-mono font-bold text-[#00D1FF]">
                      {typeof result.energy_ratio === "number" ? result.energy_ratio.toFixed(4) : result.energy_ratio}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">WAVELET / LEVEL</span>
                    <span className="text-sm font-mono font-bold text-theme-secondary">
                      {result.wavelet} (L{result.level})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : fetchingLatest ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
              <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
                <Eye className="w-4 h-4 animate-pulse text-[#00D1FF]" />
                <span>Loading latest wavefront for Mission #{missionId}…</span>
              </div>
            </div>
          ) : hasLatest === false ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Eye className="w-8 h-8 text-theme-muted/40" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Not Analyzed — Mission #{missionId}
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                No wavefront analysis found for this mission. Enter aberration values and click <strong>Evaluate Wavefront</strong>.
              </p>
            </div>
          ) : (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Eye className="w-8 h-8 text-[#00D1FF]/50" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Awaiting Wavefront Packet
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                Enter optical aberration measurements or load a preset and click &quot;Evaluate Wavefront&quot; to test with the FastAPI backend.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
