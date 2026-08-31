import React, { useState, useEffect, useCallback } from "react";
import {
  Orbit,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  ShieldCheck,
  Compass,
  Zap,
  Clock,
  Database,
  Send,
  Info,
} from "lucide-react";
import { analyzeOrbital, getLatestOrbital } from "../api/orbital";
import { useMission } from "../context/MissionContext";
import { OrbitalResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

export function Orbital() {
  const {
    activeMission,
    updateOrbitalResult,
    setInspectPayload,
  } = useMission();

  // Form State
  const [missionId, setMissionId] = useState<number>(activeMission?.id || 1);
  const [safetyDistance, setSafetyDistance] = useState<number>(5.0);

  // Object 1 State (Spacecraft)
  const [obj1Id, setObj1Id] = useState<string>("SC-PRIMARY-01");
  const [obj1Time, setObj1Time] = useState<string>(new Date().toISOString());
  const [obj1PosX, setObj1PosX] = useState<number>(6871.0);
  const [obj1PosY, setObj1PosY] = useState<number>(0.0);
  const [obj1PosZ, setObj1PosZ] = useState<number>(0.0);
  const [obj1VelX, setObj1VelX] = useState<number>(0.0);
  const [obj1VelY, setObj1VelY] = useState<number>(7.61);
  const [obj1VelZ, setObj1VelZ] = useState<number>(0.0);

  // Object 2 State (Debris / Target)
  const [obj2Id, setObj2Id] = useState<string>("DEBRIS-COSMOS-2251");
  const [obj2Time, setObj2Time] = useState<string>(new Date().toISOString());
  const [obj2PosX, setObj2PosX] = useState<number>(6873.5);
  const [obj2PosY, setObj2PosY] = useState<number>(1.2);
  const [obj2PosZ, setObj2PosZ] = useState<number>(0.8);
  const [obj2VelX, setObj2VelX] = useState<number>(0.1);
  const [obj2VelY, setObj2VelY] = useState<number>(7.58);
  const [obj2VelZ, setObj2VelZ] = useState<number>(0.2);

  // UX State
  const [loading, setLoading] = useState(false);
  const [fetchingLatest, setFetchingLatest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OrbitalResponse | null>(null);
  const [hasLatest, setHasLatest] = useState<boolean | null>(null);

  // ── Auto-fetch latest from DB on mission switch ───────────────────────
  const fetchLatest = useCallback(async (mid: number) => {
    setFetchingLatest(true);
    setResult(null);
    setError(null);
    setHasLatest(null);
    try {
      const data = await getLatestOrbital(mid);
      setResult(data);
      updateOrbitalResult(data);
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
  }, [updateOrbitalResult]);

  useEffect(() => {
    const mid = activeMission?.id ?? 1;
    setMissionId(mid);
    fetchLatest(mid);
  }, [activeMission?.id, fetchLatest]);

  // Presets
  const presets = [
    {
      label: "Safe Separation Orbit (Nominal)",
      safety: 5.0,
      o1: { id: "SC-PRIMARY-01", px: 6871.0, py: 0.0, pz: 0.0, vx: 0.0, vy: 7.61, vz: 0.0 },
      o2: { id: "DEBRIS-DELTA-44", px: 6950.0, py: 45.0, pz: 32.0, vx: -0.2, vy: 7.45, vz: 0.4 },
    },
    {
      label: "Critical Close Conjunction (Collision Risk)",
      safety: 10.0,
      o1: { id: "SC-PRIMARY-01", px: 6871.0, py: 0.0, pz: 0.0, vx: 0.0, vy: 7.61, vz: 0.0 },
      o2: { id: "DEBRIS-COSMOS-2251", px: 6871.3, py: 0.2, pz: 0.1, vx: 0.05, vy: 7.60, vz: 0.02 },
    },
    {
      label: "High-Speed Orthogonal Crossing (Warning)",
      safety: 15.0,
      o1: { id: "SC-PRIMARY-01", px: 7000.0, py: 0.0, pz: 0.0, vx: 0.0, vy: 7.55, vz: 0.0 },
      o2: { id: "SPACETRACK-9921", px: 7008.0, py: 12.0, pz: 5.0, vx: 5.2, vy: 0.5, vz: 4.1 },
    },
  ];

  const handleApplyPreset = (p: typeof presets[0]) => {
    setSafetyDistance(p.safety);
    setObj1Id(p.o1.id);
    setObj1PosX(p.o1.px);
    setObj1PosY(p.o1.py);
    setObj1PosZ(p.o1.pz);
    setObj1VelX(p.o1.vx);
    setObj1VelY(p.o1.vy);
    setObj1VelZ(p.o1.vz);

    setObj2Id(p.o2.id);
    setObj2PosX(p.o2.px);
    setObj2PosY(p.o2.py);
    setObj2PosZ(p.o2.pz);
    setObj2VelX(p.o2.vx);
    setObj2VelY(p.o2.vy);
    setObj2VelZ(p.o2.vz);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        mission_id: Number(missionId),
        object1: {
          object_id: obj1Id,
          timestamp: obj1Time,
          position: { x: Number(obj1PosX), y: Number(obj1PosY), z: Number(obj1PosZ) },
          velocity: { x: Number(obj1VelX), y: Number(obj1VelY), z: Number(obj1VelZ) },
        },
        object2: {
          object_id: obj2Id,
          timestamp: obj2Time,
          position: { x: Number(obj2PosX), y: Number(obj2PosY), z: Number(obj2PosZ) },
          velocity: { x: Number(obj2VelX), y: Number(obj2VelY), z: Number(obj2VelZ) },
        },
        safety_distance: Number(safetyDistance),
      };

      const response = await analyzeOrbital(payload);
      setResult(response);
      updateOrbitalResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to calculate orbital conjunction.");
    } finally {
      setLoading(false);
    }
  };

  const statusVariant =
    result?.collision_risk || result?.status === "CRITICAL"
      ? "critical"
      : result?.status === "WARNING"
        ? "warning"
        : "nominal";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Orbit className="w-5 h-5 text-[#00D1FF]" />
            Orbital Safety & Conjunction Analysis
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Are there dangerous orbital close approaches? Relative motion & conjunction risk evaluator.
          </p>
        </div>

        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Target Endpoint: <code className="text-[#00D1FF]">POST /orbital/</code>
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Two Orbital Objects Form */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Compass className="w-4 h-4 text-[#00D1FF]" />
                Orbital State Vectors
              </h3>
              <span className="text-[10px] font-mono text-[#00D1FF]/90">
                Mission #{missionId}
              </span>
            </div>

            {/* Presets */}
            <div className="mb-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Load Sample Conjunction Scenarios:
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
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    MISSION ID
                  </label>
                  <input
                    id="orbital-mission-id"
                    type="number"
                    value={missionId}
                    onChange={(e) => setMissionId(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-muted mb-1">
                    SAFETY DISTANCE (km)
                  </label>
                  <input
                    id="orbital-safety-distance"
                    type="number"
                    step="0.1"
                    value={safetyDistance}
                    onChange={(e) => setSafetyDistance(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                    required
                  />
                </div>
              </div>

              {/* Object 1 Card */}
              <div className="p-4 rounded-xl bg-theme-card-sub border border-theme-subtle space-y-3">
                <div className="flex items-center justify-between text-xs font-mono font-semibold text-[#00D1FF]">
                  <span>OBJECT 1 (Spacecraft)</span>
                  <input
                    id="obj1-id-input"
                    type="text"
                    value={obj1Id}
                    onChange={(e) => setObj1Id(e.target.value)}
                    className="px-2.5 py-1 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    placeholder="Object 1 ID"
                  />
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">POSITION (X, Y, Z km)</span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      step="0.1"
                      value={obj1PosX}
                      onChange={(e) => setObj1PosX(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.1"
                      value={obj1PosY}
                      onChange={(e) => setObj1PosY(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.1"
                      value={obj1PosZ}
                      onChange={(e) => setObj1PosZ(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">VELOCITY (Vx, Vy, Vz km/s)</span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      step="0.01"
                      value={obj1VelX}
                      onChange={(e) => setObj1VelX(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={obj1VelY}
                      onChange={(e) => setObj1VelY(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={obj1VelZ}
                      onChange={(e) => setObj1VelZ(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                  </div>
                </div>
              </div>

              {/* Object 2 Card */}
              <div className="p-4 rounded-xl bg-theme-card-sub border border-theme-subtle space-y-3">
                <div className="flex items-center justify-between text-xs font-mono font-semibold text-amber-500">
                  <span>OBJECT 2 (Secondary / Debris)</span>
                  <input
                    id="obj2-id-input"
                    type="text"
                    value={obj2Id}
                    onChange={(e) => setObj2Id(e.target.value)}
                    className="px-2.5 py-1 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    placeholder="Object 2 ID"
                  />
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">POSITION (X, Y, Z km)</span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      step="0.1"
                      value={obj2PosX}
                      onChange={(e) => setObj2PosX(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.1"
                      value={obj2PosY}
                      onChange={(e) => setObj2PosY(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.1"
                      value={obj2PosZ}
                      onChange={(e) => setObj2PosZ(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">VELOCITY (Vx, Vy, Vz km/s)</span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      step="0.01"
                      value={obj2VelX}
                      onChange={(e) => setObj2VelX(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={obj2VelY}
                      onChange={(e) => setObj2VelY(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={obj2VelZ}
                      onChange={(e) => setObj2VelZ(Number(e.target.value))}
                      className="px-2.5 py-1.5 rounded-lg bg-theme-input border border-theme-subtle text-xs font-mono text-theme-primary"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <button
                  id="submit-orbital-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Evaluating Conjunction...</span>
                  ) : (
                    <>
                      <Send className="w-4 h-4 text-[#00D1FF]" />
                      <span>Compute Conjunction (POST /orbital/)</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-4 p-3 rounded-xl bg-theme-card-sub border border-theme-subtle text-[11px] text-theme-muted flex items-start gap-2">
              <Info className="w-3.5 h-3.5 text-theme-muted shrink-0 mt-0.5" />
              <span>
                Note: Conjunction analysis calculates rectilinear closest approach distance and relative velocity over the state vectors provided.
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Orbital Results & Risk Assessment */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4">
              {/* Card Spotlight for Conjunction Risk */}
              <CardSpotlight
                id="orbital-verdict-spotlight"
                variant={statusVariant}
                className="bg-theme-card border-theme-subtle"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className={`p-2.5 rounded-xl border ${statusVariant === "critical"
                        ? "bg-rose-500/20 text-rose-500 border-rose-500/40"
                        : statusVariant === "warning"
                          ? "bg-amber-500/20 text-amber-500 border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-500 border-emerald-500/40"
                      }`}>
                      {statusVariant === "critical" ? (
                        <AlertOctagon className="w-6 h-6 animate-pulse" />
                      ) : statusVariant === "warning" ? (
                        <AlertTriangle className="w-6 h-6" />
                      ) : (
                        <ShieldCheck className="w-6 h-6" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border ${statusVariant === "critical"
                            ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                            : statusVariant === "warning"
                              ? "bg-amber-500/10 text-amber-500 border-amber-500/30"
                              : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                          }`}>
                          {result.status || (result.collision_risk ? "CRITICAL" : "NOMINAL")}
                        </span>
                        <span className="text-xs font-mono text-theme-muted">
                          {result.object1_id} ↔ {result.object2_id}
                        </span>
                      </div>

                      <h3 className={`text-xl font-mono font-bold mt-1.5 ${statusVariant === "critical"
                          ? "text-rose-500"
                          : statusVariant === "warning"
                            ? "text-amber-500"
                            : "text-emerald-500"
                        }`}>
                        {result.collision_risk
                          ? "COLLISION RISK / CLOSE CONJUNCTION"
                          : result.status === "WARNING"
                            ? "CLOSE APPROACH WARNING"
                            : "TRAJECTORY CLEAR / NOMINAL"}
                      </h3>

                      <p className="text-xs text-theme-secondary font-sans mt-1">
                        {result.collision_risk
                          ? `Calculated miss distance (${result.miss_distance?.toFixed(2)} km) breaches safety margin (${safetyDistance} km).`
                          : `Miss distance (${result.miss_distance?.toFixed(2)} km) maintains safe separation above designated threshold.`}
                      </p>
                    </div>
                  </div>

                  <button
                    id="inspect-orbital-json-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: "Orbital Conjunction Output",
                        data: result,
                      })
                    }
                    className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
                  >
                    Raw Output
                  </button>
                </div>
              </CardSpotlight>

              {/* Primary Conjunction Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block">MISS DISTANCE</span>
                  <div className={`text-2xl font-mono font-bold ${result.collision_risk ? "text-rose-500" : "text-emerald-500"}`}>
                    {typeof result.miss_distance === "number" ? result.miss_distance.toFixed(3) : result.miss_distance} km
                  </div>
                  <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                    Safety threshold: {safetyDistance} km
                  </span>
                </div>

                <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block">RELATIVE SPEED</span>
                  <div className="text-2xl font-mono font-bold text-[#00D1FF]">
                    {typeof result.relative_speed === "number" ? result.relative_speed.toFixed(3) : result.relative_speed} km/s
                  </div>
                  <span className="text-[10px] font-mono text-theme-muted mt-1 block">
                    Closing velocity
                  </span>
                </div>
              </div>

              {/* Detailed Conjunction Properties */}
              <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
                <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
                  <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                    Conjunction State Parameters
                  </h4>
                  <span className="text-[11px] font-mono text-theme-muted flex items-center gap-1">
                    <Database className="w-3 h-3 text-[#00D1FF]" />
                    <span>Database: {result.stored_in_database ? "Persisted" : "Evaluated"}</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">CURRENT DISTANCE</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.current_distance === "number" ? result.current_distance.toFixed(2) : result.current_distance} km
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">TIME TO CLOSEST (TCA)</span>
                    <span className="text-sm font-mono font-bold text-theme-primary">
                      {typeof result.time_to_closest_approach === "number" ? result.time_to_closest_approach.toFixed(1) + " s" : result.time_to_closest_approach}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">EVENT TYPE</span>
                    <span className="text-sm font-mono font-bold text-[#00D1FF]">
                      {result.event_type || "Conjunction"}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                    <span className="text-[10px] font-mono text-theme-muted block">RISK LEVEL</span>
                    <span className={`text-sm font-mono font-bold ${result.risk_level === "HIGH" || result.risk_level === "CRITICAL"
                        ? "text-rose-500"
                        : "text-emerald-500"
                      }`}>
                      {result.risk_level || (result.collision_risk ? "HIGH" : "LOW")}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : fetchingLatest ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
              <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
                <Orbit className="w-4 h-4 animate-pulse text-[#00D1FF]" />
                <span>Loading latest orbital for Mission #{missionId}…</span>
              </div>
            </div>
          ) : hasLatest === false ? (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Orbit className="w-8 h-8 text-theme-muted/40" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Not Analyzed — Mission #{missionId}
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                No orbital analysis found for this mission. Enter state vectors and click <strong>Compute Conjunction</strong>.
              </p>
            </div>
          ) : (
            <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
                <Orbit className="w-8 h-8 text-[#00D1FF]/50" />
              </div>
              <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
                Awaiting Conjunction Parameters
              </h4>
              <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
                Enter 3D orbital state vectors or select a preset close approach scenario and click &quot;Compute Conjunction&quot; to evaluate orbital safety.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
