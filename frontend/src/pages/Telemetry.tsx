import React, { useState, useEffect, useCallback } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Gauge,
  Thermometer,
  Zap,
  BatteryCharging,
  Wind,
  Vibrate,
  Database,
  Terminal,
  Send,
} from "lucide-react";
import { analyzeTelemetry, getLatestTelemetry } from "../api/telemetry";
import { useMission } from "../context/MissionContext";
import { TelemetryResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

export function Telemetry() {
  const {
    activeMission,
    updateTelemetryResult,
    setInspectPayload,
  } = useMission();

  // Form State
  const [missionId, setMissionId] = useState<number>(activeMission?.id || 1);
  const [temperature, setTemperature] = useState<number>(24.5);
  const [voltage, setVoltage] = useState<number>(28.2);
  const [current, setCurrent] = useState<number>(4.1);
  const [battery, setBattery] = useState<number>(95.0);
  const [pressure, setPressure] = useState<number>(101.3);
  const [vibration, setVibration] = useState<number>(0.05);

  // UX State
  const [loading, setLoading] = useState(false);
  const [fetchingLatest, setFetchingLatest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TelemetryResponse | null>(null);
  // null = no result, false = checked DB and no analysis found
  const [hasLatest, setHasLatest] = useState<boolean | null>(null);

  // ── Auto-fetch latest from DB when mission changes ──────────────────────
  const fetchLatest = useCallback(async (mid: number) => {
    setFetchingLatest(true);
    setResult(null);
    setError(null);
    setHasLatest(null);
    try {
      const data = await getLatestTelemetry(mid);
      setResult(data);
      updateTelemetryResult(data);
      setHasLatest(true);
    } catch (err: any) {
      if (err?.status === 404 || (err?.message || "").includes("404")) {
        setHasLatest(false); // no analysis yet — NOT ANALYZED
      } else if (err?.status === 0 || (err?.message || "").toLowerCase().includes("network")) {
        setError(err.message); // backend offline
      } else {
        setHasLatest(false);
      }
    } finally {
      setFetchingLatest(false);
    }
  }, [updateTelemetryResult]);

  useEffect(() => {
    const mid = activeMission?.id ?? 1;
    setMissionId(mid);
    fetchLatest(mid);
  }, [activeMission?.id, fetchLatest]);

  // Presets
  const presets = [
    {
      label: "Nominal Subsystems",
      data: { temp: 23.4, volt: 28.0, curr: 4.2, batt: 96.5, press: 101.3, vib: 0.04 },
    },
    {
      label: "Thermal & Current Spike (Anomaly)",
      data: { temp: 78.9, volt: 34.5, curr: 14.8, batt: 62.0, press: 108.5, vib: 0.88 },
    },
    {
      label: "Depressurization & High Vibration (Anomaly)",
      data: { temp: -12.3, volt: 21.2, curr: 8.5, batt: 44.0, press: 12.4, vib: 1.45 },
    },
    {
      label: "Battery Depletion Surge",
      data: { temp: 42.1, volt: 19.8, curr: 11.2, batt: 18.5, press: 99.8, vib: 0.32 },
    },
  ];

  const handleApplyPreset = (p: typeof presets[0]) => {
    setTemperature(p.data.temp);
    setVoltage(p.data.volt);
    setCurrent(p.data.curr);
    setBattery(p.data.batt);
    setPressure(p.data.press);
    setVibration(p.data.vib);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        mission_id: Number(missionId),
        temperature: Number(temperature),
        voltage: Number(voltage),
        current: Number(current),
        battery: Number(battery),
        pressure: Number(pressure),
        vibration: Number(vibration),
      };

      const response = await analyzeTelemetry(payload);
      setResult(response);
      updateTelemetryResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to analyze telemetry data.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#00D1FF]" />
            Spacecraft Telemetry Intelligence
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Is spacecraft telemetry behaving normally? Evaluate multi-channel telemetry with isolation model.
          </p>
        </div>

        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Target Endpoint: <code className="text-[#00D1FF]">POST /telemetry/</code>
        </div>
      </div>

      {/* Main 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form & Presets */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Gauge className="w-4 h-4 text-[#00D1FF]" />
                Sensor Measurements Input
              </h3>
              <span className="text-[10px] font-mono text-[#00D1FF]/90">
                Mission ID: #{missionId}
              </span>
            </div>

            {/* Presets */}
            <div className="my-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Load Sample Telemetry Scenarios:
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
                  id="telemetry-mission-id"
                  type="number"
                  value={missionId}
                  onChange={(e) => setMissionId(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <Thermometer className="w-3 h-3 text-[#00D1FF]" />
                    <span>TEMP (°C)</span>
                  </label>
                  <input
                    id="telemetry-temperature"
                    type="number"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <Zap className="w-3 h-3 text-[#00D1FF]" />
                    <span>VOLTAGE (V)</span>
                  </label>
                  <input
                    id="telemetry-voltage"
                    type="number"
                    step="0.1"
                    value={voltage}
                    onChange={(e) => setVoltage(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <Zap className="w-3 h-3 text-[#00D1FF]" />
                    <span>CURRENT (A)</span>
                  </label>
                  <input
                    id="telemetry-current"
                    type="number"
                    step="0.1"
                    value={current}
                    onChange={(e) => setCurrent(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <BatteryCharging className="w-3 h-3 text-[#00D1FF]" />
                    <span>BATTERY (%)</span>
                  </label>
                  <input
                    id="telemetry-battery"
                    type="number"
                    step="0.1"
                    value={battery}
                    onChange={(e) => setBattery(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <Wind className="w-3 h-3 text-[#00D1FF]" />
                    <span>PRESSURE (kPa)</span>
                  </label>
                  <input
                    id="telemetry-pressure"
                    type="number"
                    step="0.1"
                    value={pressure}
                    onChange={(e) => setPressure(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1 flex items-center gap-1">
                    <Vibrate className="w-3 h-3 text-[#00D1FF]" />
                    <span>VIBRATION (g)</span>
                  </label>
                  <input
                    id="telemetry-vibration"
                    type="number"
                    step="0.01"
                    value={vibration}
                    onChange={(e) => setVibration(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  id="submit-telemetry-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Evaluating Model...</span>
                  ) : (
                    <>
                      <Send className="w-4 h-4 text-[#00D1FF]" />
                      <span>Submit Telemetry (POST /telemetry/)</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column: Results & AI Decision Display */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Card Spotlight for Anomaly Verdict */}
              <CardSpotlight
                id="telemetry-verdict-spotlight"
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
                          {result.anomaly_detected ? "CRITICAL ALERT" : "SYSTEM NOMINAL"}
                        </span>
                        <span className="text-xs font-mono text-theme-muted">
                          Modality: {result.modality || "telemetry"}
                        </span>
                      </div>

                      <h3 className={`text-xl font-mono font-bold mt-1.5 ${result.anomaly_detected ? "text-rose-500" : "text-emerald-500"}`}>
                        {result.anomaly_detected ? "ANOMALY DETECTED IN SUBSYSTEMS" : "NORMAL TELEMETRY SIGNALS"}
                      </h3>

                      <p className="text-xs text-theme-secondary font-sans mt-1">
                        {result.anomaly_detected
                          ? "Model output indicates atypical feature distribution or extreme sensor deviation from nominal flight envelope."
                          : "Subsystem metrics fall within normal operating envelope boundaries."}
                      </p>
                    </div>
                  </div>

                  <button
                    id="inspect-telemetry-json-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: "Telemetry Model Response",
                        data: result,
                      })
                    }
                    className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
                  >
                    Raw Output
                  </button>
                </div>
              </CardSpotlight>

              {/* Model Decision & Output Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">
                    DECISION VALUE
                  </span>
                  <div className="text-xl font-mono font-bold text-[#00D1FF]">
                    {result.decision_value !== undefined
                      ? typeof result.decision_value === "number"
                        ? result.decision_value.toFixed(4)
                        : String(result.decision_value)
                      : "N/A"}
                  </div>
                  <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                    Anomaly classifier boundary offset
                  </span>
                </div>

                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">
                    MODEL OUTPUT
                  </span>
                  <div className="text-xl font-mono font-bold text-theme-primary truncate">
                    {result.model_output !== undefined
                      ? typeof result.model_output === "object"
                        ? JSON.stringify(result.model_output)
                        : String(result.model_output)
                      : result.anomaly_detected ? "-1 (Anomaly)" : "1 (Nominal)"}
                  </div>
                  <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                    Telemetry Isolation Classifier
                  </span>
                </div>
              </div>

              {/* Clean Measurement Grid */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                    Processed Measurements Record
                  </h4>
                  <span className="text-[11px] font-mono text-theme-muted flex items-center gap-1">
                    <Database className="w-3 h-3 text-[#00D1FF]" />
                    <span>Database: {result.stored_in_database ? "Persisted" : "Evaluated"}</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">TEMPERATURE</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.temperature ?? temperature} °C
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">VOLTAGE</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.voltage ?? voltage} V
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">CURRENT</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.current ?? current} A
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">BATTERY STATE</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.battery ?? battery} %
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">INTERNAL PRESSURE</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.pressure ?? pressure} kPa
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">VIBRATION</span>
                    <span className="text-base font-mono font-bold text-theme-primary">
                      {result.measurements?.vibration ?? vibration} g
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : fetchingLatest ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
              <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
                <Activity className="w-4 h-4 animate-pulse text-[#00D1FF]" />
                <span>Loading latest telemetry for Mission #{missionId}…</span>
              </div>
            </div>
          ) : hasLatest === false ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Activity className="w-8 h-8 text-theme-muted/40" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Not Analyzed — Mission #{missionId}
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                No telemetry analysis found in the database for this mission.
                Enter sensor values and click <strong>Submit Telemetry</strong> to create one.
              </p>
            </div>
          ) : (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Activity className="w-8 h-8 text-[#00D1FF]/50" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Awaiting Telemetry Packet
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                Select a preset scenario or provide sensor parameters and click &quot;Submit Telemetry&quot; to execute the Isolation Forest model.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
