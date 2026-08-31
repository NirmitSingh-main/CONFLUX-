import { useEffect, useCallback } from "react";
import {
  Rocket,
  Activity,
  Flame,
  Eye,
  Orbit,
  SunMedium,
  Layers,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  ShieldCheck,
  Info,
  Globe as GlobeIcon,
  ArrowRight,
} from "lucide-react";
import { BentoGrid, BentoGridItem } from "../components/ui/BentoGrid";
import { TextHoverEffect } from "../components/ui/TextHoverEffect";
import { Globe } from "../components/ui/globe";
import { CardSpotlight } from "../components/ui/CardSpotlight";
import { useMission } from "../context/MissionContext";
import { getLatestTelemetry } from "../api/telemetry";
import { getLatestImagery } from "../api/imagery";
import { getLatestWavefront } from "../api/wavefront";
import { getLatestOrbital } from "../api/orbital";
import { getLatestSpaceWeather } from "../api/spaceWeather";

export function Dashboard() {
  const {
    setActivePage,
    activeMission,
    modalityState,
    healthStatus,
    setInspectPayload,
    updateTelemetryResult,
    updateImageryResult,
    updateWavefrontResult,
    updateOrbitalResult,
    updateWeatherResult,
  } = useMission();

  // ── Fetch all modality latest from DB whenever mission changes ──────────
  // This populates modalityState from DB, not just from this session's POST calls.
  const fetchAllLatest = useCallback(async (missionId: number, isCurrent: () => boolean) => {
    const safe = async <T,>(fn: () => Promise<T>): Promise<T | null> => {
      try { return await fn(); } catch { return null; }
    };
    const [tel, img, wav, orb, wea] = await Promise.all([
      safe(() => getLatestTelemetry(missionId)),
      safe(() => getLatestImagery(missionId)),
      safe(() => getLatestWavefront(missionId)),
      safe(() => getLatestOrbital(missionId)),
      safe(() => getLatestSpaceWeather(missionId)),
    ]);
    if (!isCurrent()) return;
    if (tel) updateTelemetryResult(tel);
    if (img) updateImageryResult(img);
    if (wav) updateWavefrontResult(wav);
    if (orb) updateOrbitalResult(orb);
    if (wea) updateWeatherResult(wea);
  }, [updateTelemetryResult, updateImageryResult, updateWavefrontResult, updateOrbitalResult, updateWeatherResult]);

  useEffect(() => {
    let cancelled = false;
    if (activeMission?.id) fetchAllLatest(activeMission.id, () => !cancelled);
    return () => { cancelled = true; };
  }, [activeMission?.id, fetchAllLatest]);

  // ── Compute summary stats from DB-backed modality state ─────────────────
  // Only count backend-confirmed anomalies (responses that actually exist in DB)
  const anomaliesCount = [
    modalityState.lastTelemetryResponse != null ? modalityState.telemetryAnomaly : null,
    modalityState.lastImageryResponse != null ? modalityState.thermalAnomaly : null,
    modalityState.lastWavefrontResponse != null ? modalityState.wavefrontAnomaly : null,
    modalityState.lastOrbitalResponse != null
      ? (modalityState.orbitalStatus === "CRITICAL" || modalityState.orbitalStatus === "WARNING")
      : null,
    modalityState.lastWeatherResponse != null ? modalityState.spaceWeatherAnomaly : null,
  ].filter((v) => v === true).length;

  const analyzedCount = [
    modalityState.lastTelemetryResponse,
    modalityState.lastImageryResponse,
    modalityState.lastWavefrontResponse,
    modalityState.lastOrbitalResponse,
    modalityState.lastWeatherResponse,
  ].filter(Boolean).length;

  const orbitalRiskLevel = modalityState.orbitalStatus || "NOMINAL";

  return (
    <div className="space-y-6">
      {/* Top Hero Section with TextHoverEffect & Aceternity 3D Globe */}
      <div className="relative rounded-2xl bg-theme-card border border-theme-subtle p-6 md:p-8 backdrop-blur-md overflow-hidden">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6 relative z-10">
          {/* Left Hero info */}
          <div className="w-full lg:w-3/5 space-y-4">
            <div className="h-20 w-full max-w-sm">
              <TextHoverEffect text="CONFLUX" />
            </div>

            <div className="space-y-1.5">
              <h2 className="text-xl md:text-2xl font-mono font-semibold tracking-tight text-theme-primary flex items-center gap-2.5">
                Multimodal Mission Intelligence
                <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-theme-cyan-subtle border border-theme-cyan text-[#00D1FF] tracking-wider uppercase">
                  REAL-TIME
                </span>
              </h2>
              <p className="text-xs text-theme-muted font-sans max-w-xl leading-relaxed">
                Centralized decision-support synthesizing subsystem telemetry, infrared radiometric imagery, optical wavefront dynamics, orbital safety conjunctions, and space weather disturbances.
              </p>
            </div>

            {/* Metrics Ticker Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono">
              <div className="p-2.5 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <div className="text-[9px] uppercase tracking-wider text-theme-muted mb-0.5">Uptime</div>
                <div className="text-sm font-semibold text-[#00D1FF]">99.982%</div>
              </div>
              <div className="p-2.5 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <div className="text-[9px] uppercase tracking-wider text-theme-muted mb-0.5">Data Ingest</div>
                <div className="text-sm font-semibold text-theme-primary">1.2 GB/s</div>
              </div>
              <div className="p-2.5 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <div className="text-[9px] uppercase tracking-wider text-theme-muted mb-0.5">Anomalies</div>
                <div className={`text-sm font-semibold ${anomaliesCount > 0 ? "text-amber-500" : "text-emerald-500"}`}>
                    {anomaliesCount} / {analyzedCount} analyzed
                  </div>
              </div>
              <div className="p-2.5 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <div className="text-[9px] uppercase tracking-wider text-theme-muted mb-0.5">Orbital Risk</div>
                <div className={`text-sm font-semibold ${orbitalRiskLevel === "CRITICAL" ? "text-rose-500" : orbitalRiskLevel === "WARNING" ? "text-amber-500" : "text-emerald-500"}`}>
                  {orbitalRiskLevel}
                </div>
              </div>
            </div>

            {/* Active Mission Banner */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <div className="flex items-center gap-3 px-3.5 py-2 rounded-xl bg-theme-card-sub border border-theme-subtle font-mono text-xs text-theme-primary">
                <Rocket className="w-4 h-4 text-[#00D1FF]" />
                <div>
                  <span className="text-[9px] text-theme-muted block uppercase tracking-wider">ACTIVE MISSION</span>
                  <span className="font-semibold text-theme-primary">
                    {activeMission ? `${activeMission.mission_name} (${activeMission.spacecraft_name})` : "No Mission Selected"}
                  </span>
                </div>
                {activeMission && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/30">
                    {activeMission.status}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-theme-card-sub border border-theme-subtle font-mono text-xs text-theme-secondary">
                <span className="text-[9px] text-theme-muted block uppercase tracking-wider">GATEWAY</span>
                <div className="flex items-center gap-1.5 font-semibold">
                  <span className={`w-2 h-2 rounded-full ${healthStatus === "healthy" ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
                  <span className={healthStatus === "healthy" ? "text-emerald-500" : "text-rose-500"}>
                    {healthStatus === "healthy" ? "ONLINE" : "OFFLINE"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Visual Aceternity 3D Globe with Ground Station Telemetry */}
          <div className="w-full lg:w-2/5 flex flex-col items-center justify-center relative">
            <div className="w-full max-w-[320px] sm:max-w-[340px] aspect-square relative flex items-center justify-center">
              <Globe className="w-full h-full" />
            </div>
            <div className="flex items-center justify-between w-full max-w-[320px] px-2 mt-1">
              <p className="text-[10px] font-mono text-theme-muted flex items-center gap-1.5 uppercase tracking-wider">
                <GlobeIcon className="w-3 h-3 text-[#00D1FF]" />
                <span>Planetary Telemetry Mesh</span>
              </p>
              <span className="text-[9px] font-mono text-theme-muted uppercase tracking-widest">
                Drag to rotate
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Multimodal Agreement Spotlight (If Anomalies or Agreement present) */}
      {anomaliesCount > 0 && (
        <CardSpotlight
          id="fusion-alert-spotlight"
          variant={anomaliesCount >= 3 ? "critical" : "warning"}
          className="border-theme-subtle bg-theme-card"
        >
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-xl ${anomaliesCount >= 3 ? "bg-rose-500/15 text-rose-500 border border-rose-500/30" : "bg-amber-500/15 text-amber-500 border border-amber-500/30"}`}>
                <AlertTriangle className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                  {anomaliesCount >= 3 ? "CRITICAL MULTIMODAL ELEVATION DETECTED" : "MODALITY ANOMALIES ACTIVE"}
                </h3>
                <p className="text-xs text-theme-muted font-sans mt-0.5">
                  {anomaliesCount} of 5 modalities currently indicate anomalous telemetry or environmental conditions.
                </p>
              </div>
            </div>

            <button
              id="goto-fusion-spotlight-btn"
              onClick={() => setActivePage("fusion")}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle font-mono text-xs font-semibold shrink-0 transition-all"
            >
              <span>Run Multimodal Fusion</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#00D1FF]" />
            </button>
          </div>
        </CardSpotlight>
      )}

      {/* Bento Grid for Modality Status Cards */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-[#00D1FF] rounded-full animate-pulse" />
            <h3 className="font-mono text-[11px] uppercase tracking-widest text-theme-muted font-semibold">
              Mission Modality Intelligence Overview
            </h3>
          </div>
          <span className="text-[10px] font-mono text-theme-muted uppercase tracking-wider">
            Click modality to inspect
          </span>
        </div>

        <BentoGrid className="max-w-none">
          {/* Bento Item 1: Mission Status */}
          <BentoGridItem
            id="bento-mission-status"
            title="Mission Context"
            icon={<Rocket className="w-4 h-4" />}
            statusBadge={activeMission?.status || "ACTIVE"}
            statusColor="cyan"
            description="Mission registration & active context"
            onClick={() => setActivePage("missions")}
            header={
              <div className="space-y-1 py-1">
                <div className="text-sm font-mono font-semibold text-theme-primary">
                  {activeMission?.mission_name || "No Mission"}
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  Vehicle: <span className="text-[#00D1FF]">{activeMission?.spacecraft_name || "N/A"}</span>
                </div>
                <div className="text-[10px] text-theme-muted font-mono">
                  Mission ID #{activeMission?.id || 1}
                </div>
              </div>
            }
          />

          {/* Bento Item 2: Telemetry */}
          <BentoGridItem
            id="bento-telemetry"
            title="Subsystem Telemetry"
            icon={<Activity className="w-4 h-4" />}
            statusBadge={
               modalityState.lastTelemetryResponse == null
                 ? "NOT ANALYZED"
                 : modalityState.telemetryAnomaly
                 ? "ANOMALY"
                 : "NORMAL"
             }
             statusColor={
               modalityState.lastTelemetryResponse == null
                 ? "neutral"
                 : modalityState.telemetryAnomaly
                 ? "critical"
                 : "nominal"
             }
            description="Power, thermal, vibration & pressure sensors"
            onClick={() => setActivePage("telemetry")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  {modalityState.lastTelemetryResponse == null ? (
                    <Info className="w-4 h-4 text-theme-muted shrink-0" />
                  ) : modalityState.telemetryAnomaly ? (
                    <AlertOctagon className="w-4 h-4 text-rose-500 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  )}
                  <span className={`text-sm font-mono font-semibold ${
                    modalityState.lastTelemetryResponse == null
                      ? "text-theme-muted"
                      : modalityState.telemetryAnomaly
                      ? "text-rose-500"
                      : "text-emerald-500"
                  }`}>
                    {modalityState.lastTelemetryResponse == null
                      ? "Not Analyzed"
                      : modalityState.telemetryAnomaly
                      ? "Anomaly Detected"
                      : "Nominal Telemetry"}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  {modalityState.lastTelemetryResponse ? (
                    <span>Decision value: {modalityState.lastTelemetryResponse.decision_value ?? "Evaluated"}</span>
                  ) : (
                    <span>Isolation Forest / Subsystem ML Model Ready</span>
                  )}
                </div>
              </div>
            }
          />

          {/* Bento Item 3: Thermal / Imagery */}
          <BentoGridItem
            id="bento-thermal"
            title="Thermal / Infrared"
            icon={<Flame className="w-4 h-4" />}
            statusBadge={
               modalityState.lastImageryResponse == null
                 ? "NOT ANALYZED"
                 : modalityState.thermalAnomaly
                 ? "HOTSPOT"
                 : "NORMAL"
             }
             statusColor={
               modalityState.lastImageryResponse == null
                 ? "neutral"
                 : modalityState.thermalAnomaly
                 ? "critical"
                 : "nominal"
             }
            description="Radiometric infrared anomaly analysis"
            onClick={() => setActivePage("thermal")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  {modalityState.lastImageryResponse == null ? (
                    <Info className="w-4 h-4 text-theme-muted shrink-0" />
                  ) : modalityState.thermalAnomaly ? (
                    <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  )}
                  <span className={`text-sm font-mono font-semibold ${
                    modalityState.lastImageryResponse == null
                      ? "text-theme-muted"
                      : modalityState.thermalAnomaly
                      ? "text-rose-500"
                      : "text-emerald-500"
                  }`}>
                    {modalityState.lastImageryResponse == null
                      ? "Not Analyzed"
                      : modalityState.thermalAnomaly
                      ? "Thermal Anomaly"
                      : "Nominal Infrared"}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  {modalityState.lastImageryResponse ? (
                    <span>Max Hotspot: {modalityState.lastImageryResponse.hottest_intensity}</span>
                  ) : (
                    <span>Radiometric thresholding detector</span>
                  )}
                </div>
              </div>
            }
          />

          {/* Bento Item 4: Wavefront */}
          <BentoGridItem
            id="bento-wavefront"
            title="Optical Wavefront"
            icon={<Eye className="w-4 h-4" />}
            statusBadge={
               modalityState.lastWavefrontResponse == null
                 ? "NOT ANALYZED"
                 : modalityState.wavefrontAnomaly
                 ? "ABERRATION"
                 : "NORMAL"
             }
             statusColor={
               modalityState.lastWavefrontResponse == null
                 ? "neutral"
                 : modalityState.wavefrontAnomaly
                 ? "critical"
                 : "nominal"
             }
            description="Optical aberrations & wavelet analysis"
            onClick={() => setActivePage("wavefront")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  {modalityState.lastWavefrontResponse == null ? (
                    <Info className="w-4 h-4 text-theme-muted shrink-0" />
                  ) : modalityState.wavefrontAnomaly ? (
                    <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  )}
                  <span className={`text-sm font-mono font-semibold ${
                    modalityState.lastWavefrontResponse == null
                      ? "text-theme-muted"
                      : modalityState.wavefrontAnomaly
                      ? "text-rose-500"
                      : "text-emerald-500"
                  }`}>
                    {modalityState.lastWavefrontResponse == null
                      ? "Not Analyzed"
                      : modalityState.wavefrontAnomaly
                      ? "Aberration Alert"
                      : "Diffraction Nominal"}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  {modalityState.lastWavefrontResponse ? (
                    <span>Anomaly score: {modalityState.lastWavefrontResponse.anomaly_score?.toFixed(3)}</span>
                  ) : (
                    <span>Wavelet energy & Zernike decomposition</span>
                  )}
                </div>
              </div>
            }
          />

          {/* Bento Item 5: Orbital */}
          <BentoGridItem
            id="bento-orbital"
            title="Orbital Safety"
            icon={<Orbit className="w-4 h-4" />}
            statusBadge={orbitalRiskLevel}
            statusColor={orbitalRiskLevel === "CRITICAL" ? "critical" : orbitalRiskLevel === "WARNING" ? "warning" : "nominal"}
            description="Conjunction & close approach tracking"
            onClick={() => setActivePage("orbital")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  {orbitalRiskLevel === "CRITICAL" ? (
                    <AlertOctagon className="w-4 h-4 text-rose-500 shrink-0" />
                  ) : orbitalRiskLevel === "WARNING" ? (
                    <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                  ) : (
                    <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
                  )}
                  <span className={`text-sm font-mono font-semibold ${
                    orbitalRiskLevel === "CRITICAL"
                      ? "text-rose-500"
                      : orbitalRiskLevel === "WARNING"
                      ? "text-amber-500"
                      : "text-emerald-500"
                  }`}>
                    {orbitalRiskLevel === "CRITICAL" ? "Collision Risk" : orbitalRiskLevel === "WARNING" ? "Warning Conjunction" : "Safe Trajectory"}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  {modalityState.lastOrbitalResponse ? (
                    <span>Miss distance: {modalityState.lastOrbitalResponse.miss_distance?.toFixed(1)} km</span>
                  ) : (
                    <span>Conjunction evaluator</span>
                  )}
                </div>
              </div>
            }
          />

          {/* Bento Item 6: Space Weather */}
          <BentoGridItem
            id="bento-space-weather"
            title="Space Weather"
            icon={<SunMedium className="w-4 h-4" />}
            statusBadge={
               modalityState.lastWeatherResponse == null
                 ? "NOT ANALYZED"
                 : modalityState.spaceWeatherAnomaly
                 ? "ELEVATED"
                 : "NORMAL"
             }
             statusColor={
               modalityState.lastWeatherResponse == null
                 ? "neutral"
                 : modalityState.spaceWeatherAnomaly
                 ? "warning"
                 : "nominal"
             }
            description="Solar, radiation & geomagnetic flux"
            onClick={() => setActivePage("weather")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  {modalityState.lastWeatherResponse == null ? (
                    <Info className="w-4 h-4 text-theme-muted shrink-0" />
                  ) : modalityState.spaceWeatherAnomaly ? (
                    <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  )}
                  <span className={`text-sm font-mono font-semibold ${
                    modalityState.lastWeatherResponse == null
                      ? "text-theme-muted"
                      : modalityState.spaceWeatherAnomaly
                      ? "text-amber-500"
                      : "text-emerald-500"
                  }`}>
                    {modalityState.lastWeatherResponse == null
                      ? "Not Analyzed"
                      : modalityState.spaceWeatherAnomaly
                      ? "Elevated Flux"
                      : "Quiet Environment"}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono">
                  {modalityState.lastWeatherResponse ? (
                    <span>Solar: {modalityState.lastWeatherResponse.solar_activity} · Rad: {modalityState.lastWeatherResponse.radiation_level}</span>
                  ) : (
                    <span>Environmental disturbance model</span>
                  )}
                </div>
              </div>
            }
          />

          {/* Bento Item 7: Multimodal Fusion */}
          <BentoGridItem
            id="bento-fusion"
            className="md:col-span-2"
            title="Multimodal Fusion"
            icon={<Layers className="w-4 h-4" />}
            statusBadge={
               modalityState.lastFusionResponse
                 ? modalityState.lastFusionResponse.multi_modal_agreement
                   ? "AGREEMENT"
                   : `${modalityState.lastFusionResponse.anomaly_count ?? anomaliesCount}/${analyzedCount} Anomalous`
                 : analyzedCount === 0
                 ? "NOT ANALYZED"
                 : `${anomaliesCount}/${analyzedCount} Anomalous`
             }
            statusColor={anomaliesCount >= 3 ? "critical" : anomaliesCount > 0 ? "warning" : "nominal"}
            description="Unified cross-modal synthesis & consensus engine"
            onClick={() => setActivePage("fusion")}
            header={
              <div className="space-y-1.5 py-1">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#00D1FF] animate-ping shrink-0" />
                  <span className="text-sm font-mono font-semibold text-theme-primary">
                    {modalityState.lastFusionResponse
                      ? modalityState.lastFusionResponse.multi_modal_agreement
                        ? "Multimodal Agreement Detected"
                        : `${modalityState.lastFusionResponse.anomaly_count ?? anomaliesCount} Anomalies Detected`
                      : analyzedCount === 0
                      ? "No Modalities Analyzed Yet"
                      : `${anomaliesCount} of ${analyzedCount} Analyzed Modalities Anomalous`}
                  </span>
                </div>
                <div className="text-xs text-theme-muted font-mono flex items-center gap-4">
                  <span>Evaluates cross-modal consensus across all 5 telemetry pipelines</span>
                </div>
              </div>
            }
          />
        </BentoGrid>
      </div>
    </div>
  );
}
