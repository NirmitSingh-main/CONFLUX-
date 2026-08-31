import React, { useState, useEffect, useCallback } from "react";
import {
  SunMedium,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Flame,
  Zap,
  Radio,
  Database,
  Send,
  ShieldAlert,
  Sun,
  Activity,
} from "lucide-react";
import { analyzeSpaceWeather, getLatestSpaceWeather } from "../api/spaceWeather";
import { useMission } from "../context/MissionContext";
import { SpaceWeatherResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

export function SpaceWeather() {
  const {
    activeMission,
    updateWeatherResult,
    setInspectPayload,
  } = useMission();

  // Form State
  const [missionId, setMissionId] = useState<number>(activeMission?.id || 1);
  const [solarActivity, setSolarActivity] = useState<number>(25.0);
  const [radiationLevel, setRadiationLevel] = useState<number>(1.2);
  const [geomagneticActivity, setGeomagneticActivity] = useState<number>(2.0);

  // UX State
  const [loading, setLoading] = useState(false);
  const [fetchingLatest, setFetchingLatest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SpaceWeatherResponse | null>(null);
  const [hasLatest, setHasLatest] = useState<boolean | null>(null);

  // ── Auto-fetch latest from DB on mission switch ───────────────────────
  const fetchLatest = useCallback(async (mid: number) => {
    setFetchingLatest(true);
    setResult(null);
    setError(null);
    setHasLatest(null);
    try {
      const data = await getLatestSpaceWeather(mid);
      setResult(data);
      updateWeatherResult(data);
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
  }, [updateWeatherResult]);

  useEffect(() => {
    const mid = activeMission?.id ?? 1;
    setMissionId(mid);
    fetchLatest(mid);
  }, [activeMission?.id, fetchLatest]);

  // Presets
  const presets = [
    {
      label: "Quiet Sun & Magnetosphere (Nominal)",
      data: { solar: 18.0, rad: 0.8, geo: 1.5 },
    },
    {
      label: "X-Class Solar Flare & CME (Elevated Solar)",
      data: { solar: 185.0, rad: 4.2, geo: 3.8 },
    },
    {
      label: "Severe Solar Particle Event (Elevated Radiation)",
      data: { solar: 95.0, rad: 28.5, geo: 4.2 },
    },
    {
      label: "G5 Extreme Geomagnetic Storm (Elevated Geo)",
      data: { solar: 120.0, rad: 12.0, geo: 9.0 },
    },
  ];

  const handleApplyPreset = (p: typeof presets[0]) => {
    setSolarActivity(p.data.solar);
    setRadiationLevel(p.data.rad);
    setGeomagneticActivity(p.data.geo);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        mission_id: Number(missionId),
        solar_activity: Number(solarActivity),
        radiation_level: Number(radiationLevel),
        geomagnetic_activity: Number(geomagneticActivity),
      };

      const response = await analyzeSpaceWeather(payload);
      setResult(response);
      updateWeatherResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to analyze space weather conditions.");
    } finally {
      setLoading(false);
    }
  };

  // Helper to extract active event badges.
  // Uses ONLY active_events from the backend — the authoritative source.
  // Do NOT combine with solar_event / radiation_event booleans to avoid duplicates.
  const getActiveEventBadges = (): string[] => {
    if (!result) return [];
    if (Array.isArray(result.active_events)) {
      return result.active_events.map((ev: string) => ev.toUpperCase().replace(/_/g, " "));
    }
    return [];
  };

  const activeBadges = getActiveEventBadges();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <SunMedium className="w-5 h-5 text-[#00D1FF]" />
            Space Weather & Environmental Disturbances
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Are environmental conditions affecting the mission? Solar irradiance, ionizing flux & geomagnetic indices.
          </p>
        </div>

        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Target Endpoint: <code className="text-[#00D1FF]">POST /space-weather/</code>
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Sun className="w-4 h-4 text-[#00D1FF]" />
                Heliospheric Sensor Inputs
              </h3>
              <span className="text-[10px] font-mono text-[#00D1FF]/90">
                Mission #{missionId}
              </span>
            </div>

            {/* Presets */}
            <div className="mb-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Load Space Weather Scenarios:
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

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                  MISSION ID
                </label>
                <input
                  id="weather-mission-id"
                  type="number"
                  value={missionId}
                  onChange={(e) => setMissionId(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center justify-between">
                  <span className="flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5 text-amber-500" />
                    <span>SOLAR ACTIVITY (SFU / Flux Index)</span>
                  </span>
                  <span className="text-amber-500 font-bold">{solarActivity}</span>
                </label>
                <input
                  id="weather-solar"
                  type="number"
                  step="0.1"
                  value={solarActivity}
                  onChange={(e) => setSolarActivity(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center justify-between">
                  <span className="flex items-center gap-1">
                    <Radio className="w-3.5 h-3.5 text-rose-500" />
                    <span>RADIATION LEVEL (µGy/h / Flux)</span>
                  </span>
                  <span className="text-rose-500 font-bold">{radiationLevel}</span>
                </label>
                <input
                  id="weather-radiation"
                  type="number"
                  step="0.1"
                  value={radiationLevel}
                  onChange={(e) => setRadiationLevel(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center justify-between">
                  <span className="flex items-center gap-1">
                    <Zap className="w-3.5 h-3.5 text-[#00D1FF]" />
                    <span>GEOMAGNETIC ACTIVITY (Kp Index 0-9)</span>
                  </span>
                  <span className="text-[#00D1FF] font-bold">{geomagneticActivity}</span>
                </label>
                <input
                  id="weather-geomagnetic"
                  type="number"
                  step="0.1"
                  value={geomagneticActivity}
                  onChange={(e) => setGeomagneticActivity(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div className="pt-2">
                <button
                  id="submit-weather-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Evaluating Disturbances...</span>
                  ) : (
                    <>
                      <Send className="w-4 h-4 text-[#00D1FF]" />
                      <span>Evaluate Space Weather (POST /space-weather/)</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column: Space Weather Assessment & Event Badges */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Card Spotlight for Environmental Anomaly */}
              <CardSpotlight
                id="weather-verdict-spotlight"
                variant={result.environmental_anomaly ? "warning" : "nominal"}
                className="bg-theme-card border-theme-subtle"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2.5 rounded-xl border ${result.environmental_anomaly ? "bg-amber-500/20 text-amber-500 border-amber-500/40" : "bg-emerald-500/20 text-emerald-500 border-emerald-500/40"}`}>
                      {result.environmental_anomaly ? (
                        <AlertTriangle className="w-6 h-6 animate-pulse" />
                      ) : (
                        <CheckCircle2 className="w-6 h-6" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border ${result.environmental_anomaly
                            ? "bg-amber-500/10 text-amber-500 border-amber-500/30"
                            : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                          }`}>
                          {result.environmental_anomaly ? "ENVIRONMENTAL ANOMALY" : "QUIET SPACE ENVIRONMENT"}
                        </span>
                        <span className="text-xs font-mono text-theme-muted">
                          Modality: {result.modality || "space_weather"}
                        </span>
                      </div>

                      <h3 className={`text-xl font-mono font-bold mt-1.5 ${result.environmental_anomaly ? "text-amber-500" : "text-emerald-500"}`}>
                        {result.environmental_anomaly ? "ELEVATED SPACE WEATHER DISTURBANCE" : "QUIET BACKGROUND CONDITIONS"}
                      </h3>

                      <p className="text-xs text-theme-secondary font-sans mt-1">
                        {result.environmental_anomaly
                          ? "Heliospheric or magnetospheric flux triggers environmental anomaly thresholds."
                          : "Solar flux, cosmic radiation, and geomagnetic field indices within quiet baselines."}
                      </p>
                    </div>
                  </div>

                  <button
                    id="inspect-weather-json-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: "Space Weather Response",
                        data: result,
                      })
                    }
                    className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
                  >
                    Raw Output
                  </button>
                </div>
              </CardSpotlight>

              {/* Active Events Badges */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary mb-3 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-[#00D1FF]" />
                  Active Environmental Event Flags
                </h4>

                {activeBadges.length > 0 ? (
                  <div className="flex flex-wrap gap-2.5">
                    {activeBadges.map((badge, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-500 font-mono text-xs font-semibold flex items-center gap-2"
                      >
                        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                        <span>{badge}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 font-mono text-xs flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>No active solar flare, radiation storm, or geomagnetic events.</span>
                  </div>
                )}
              </div>

              {/* Measured Environmental Levels */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">SOLAR ACTIVITY</span>
                  <div className="text-xl font-mono font-bold text-theme-primary">
                    {result.solar_activity}
                  </div>
                  <span className={`text-[10px] font-mono mt-1 block font-semibold ${result.solar_event ? "text-rose-500" : "text-emerald-500"
                    }`}>
                    {result.solar_event ? "• Solar Event Active" : "• Nominal"}
                  </span>
                </div>

                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">RADIATION LEVEL</span>
                  <div className="text-xl font-mono font-bold text-theme-primary">
                    {result.radiation_level}
                  </div>
                  <span className={`text-[10px] font-mono mt-1 block font-semibold ${result.radiation_event ? "text-rose-500" : "text-emerald-500"
                    }`}>
                    {result.radiation_event ? "• Radiation Event Active" : "• Nominal"}
                  </span>
                </div>

                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">GEOMAGNETIC</span>
                  <div className="text-xl font-mono font-bold text-theme-primary">
                    {result.geomagnetic_activity}
                  </div>
                  <span className={`text-[10px] font-mono mt-1 block font-semibold ${result.geomagnetic_event ? "text-rose-500" : "text-emerald-500"
                    }`}>
                    {result.geomagnetic_event ? "• Geo Event Active" : "• Nominal"}
                  </span>
                </div>
              </div>
            </div>
          ) : fetchingLatest ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
              <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
                <SunMedium className="w-4 h-4 animate-pulse text-[#00D1FF]" />
                <span>Loading latest space weather for Mission #{missionId}…</span>
              </div>
            </div>
          ) : hasLatest === false ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <SunMedium className="w-8 h-8 text-theme-muted/40" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Not Analyzed — Mission #{missionId}
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                No space weather analysis found for this mission. Enter solar indices and click <strong>Evaluate Space Weather</strong>.
              </p>
            </div>
          ) : (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <SunMedium className="w-8 h-8 text-[#00D1FF]/50" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Awaiting Space Weather Telemetry
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                Enter solar irradiance, radiation levels, and geomagnetic field indices or load a preset and click &quot;Evaluate Space Weather&quot; to test with FastAPI.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
