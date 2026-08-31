import React, { useState } from "react";
import {
  Rocket,
  Plus,
  CheckCircle2,
  AlertCircle,
  Radio,
  Clock,
  Check,
  Sparkles,
  Database,
  ExternalLink,
} from "lucide-react";
import { createMission } from "../api/missions";
import { useMission } from "../context/MissionContext";
import { Mission } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

export function Missions() {
  const {
    activeMission,
    setActiveMission,
    missions,
    addMission,
    setInspectPayload,
  } = useMission();

  // Form State
  const [missionName, setMissionName] = useState("");
  const [spacecraftName, setSpacecraftName] = useState("");
  const [status, setStatus] = useState("ACTIVE");

  // UX State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMission, setSuccessMission] = useState<Mission | null>(null);

  // Preset templates for testing
  const presets = [
    { name: "ARES-V Deep Recon", craft: "ORION-X4", status: "ACTIVE" },
    { name: "Europa Orbital Oceanographer", craft: "CLIPPER-02", status: "CRITICAL_MANEUVER" },
    { name: "Deep Space Gateway", craft: "GATEWAY-HALO", status: "NOMINAL" },
    { name: "Helios Solar Orbiter", craft: "SOLAR-PROBE-9", status: "OBSERVATION" },
  ];

  const handleApplyPreset = (preset: { name: string; craft: string; status: string }) => {
    setMissionName(preset.name);
    setSpacecraftName(preset.craft);
    setStatus(preset.status);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!missionName.trim() || !spacecraftName.trim()) {
      setError("Please provide both a mission name and spacecraft name.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMission(null);

    try {
      const response = await createMission({
        mission_name: missionName.trim(),
        spacecraft_name: spacecraftName.trim(),
        status: status.trim(),
      });

      setSuccessMission(response);
      addMission(response);
      // Reset form
      setMissionName("");
      setSpacecraftName("");
    } catch (err: any) {
      setError(err.message || "Failed to create mission on backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Rocket className="w-5 h-5 text-[#00D1FF]" />
            Spacecraft Mission Registration
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Register and manage active space missions. Submissions post directly to <code className="text-[#00D1FF] font-mono">POST /missions/</code>.
          </p>
        </div>

        {activeMission && (
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-theme-card-sub border border-theme-cyan text-xs font-mono">
            <Radio className="w-4 h-4 text-[#00D1FF] animate-pulse" />
            <div>
              <span className="text-[10px] text-theme-muted block uppercase">Current Context</span>
              <span className="font-semibold text-theme-primary">
                ID #{activeMission.id} · {activeMission.mission_name}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Create Form on Left, Active/Registered Missions on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Mission Creation Form */}
        <div className="lg:col-span-6 space-y-6">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-4 border-b border-theme-subtle">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Plus className="w-4 h-4 text-[#00D1FF]" />
                Register New Mission
              </h3>
              <span className="text-[11px] font-mono text-[#00D1FF]/80">
                POST /missions/
              </span>
            </div>

            {/* Quick Preset Buttons */}
            <div className="my-4">
              <span className="text-[10px] font-mono text-theme-muted block mb-2 uppercase tracking-wider">
                Quick Load Mission Templates:
              </span>
              <div className="flex flex-wrap gap-2">
                {presets.map((p) => (
                  <button
                    key={p.name}
                    type="button"
                    onClick={() => handleApplyPreset(p)}
                    className="px-2.5 py-1 text-[11px] font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-secondary border border-theme-subtle hover:border-[#00D1FF]/40 transition-colors"
                  >
                    {p.name}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Error:</span> {error}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-theme-secondary mb-1.5 uppercase">
                  Mission Name <span className="text-[#00D1FF]">*</span>
                </label>
                <input
                  id="input-mission-name"
                  type="text"
                  value={missionName}
                  onChange={(e) => setMissionName(e.target.value)}
                  placeholder="e.g. ARES-V DEEP RECON"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary placeholder-slate-500 focus:outline-none focus:border-[#00D1FF] transition-colors"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-theme-secondary mb-1.5 uppercase">
                  Spacecraft / Vehicle Name <span className="text-[#00D1FF]">*</span>
                </label>
                <input
                  id="input-spacecraft-name"
                  type="text"
                  value={spacecraftName}
                  onChange={(e) => setSpacecraftName(e.target.value)}
                  placeholder="e.g. ORION-X4"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary placeholder-slate-500 focus:outline-none focus:border-[#00D1FF] transition-colors"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-theme-secondary mb-1.5 uppercase">
                  Mission Status
                </label>
                <select
                  id="select-mission-status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF] transition-colors"
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="NOMINAL">NOMINAL</option>
                  <option value="ORBIT_INSERTION">ORBIT_INSERTION</option>
                  <option value="CRITICAL_MANEUVER">CRITICAL_MANEUVER</option>
                  <option value="OBSERVATION">OBSERVATION</option>
                  <option value="STANDBY">STANDBY</option>
                </select>
              </div>

              <div className="pt-2">
                <button
                  id="submit-create-mission-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <span>Registering with FastAPI...</span>
                  ) : (
                    <>
                      <Rocket className="w-4 h-4 text-[#00D1FF]" />
                      <span>Create Mission (POST /missions/)</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Success Card Spotlight if freshly created */}
          {successMission && (
            <CardSpotlight
              id="mission-success-spotlight"
              variant="nominal"
              className="bg-theme-card border-emerald-500/40"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-500 border border-emerald-500/30">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase text-emerald-500 font-bold">
                        MISSION CREATED SUCCESSFULLY
                      </span>
                      <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-theme-card-sub text-[#00D1FF] font-bold">
                        ID #{successMission.id}
                      </span>
                    </div>
                    <h4 className="text-base font-mono font-bold text-theme-primary mt-1">
                      {successMission.mission_name}
                    </h4>
                    <p className="text-xs text-theme-secondary font-sans mt-0.5">
                      Spacecraft: <span className="font-mono text-theme-primary">{successMission.spacecraft_name}</span> · Status: <span className="font-mono text-emerald-500">{successMission.status}</span>
                    </p>
                    <p className="text-[11px] text-theme-muted font-mono mt-1">
                      Created at: {new Date(successMission.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    id="set-active-success-mission-btn"
                    onClick={() => setActiveMission(successMission)}
                    className="px-3 py-1.5 rounded-xl text-xs font-mono font-semibold bg-emerald-500 text-white hover:bg-emerald-600 transition-colors"
                  >
                    Set as Active
                  </button>
                  <button
                    id="inspect-mission-payload-btn"
                    onClick={() =>
                      setInspectPayload({
                        title: `Mission #${successMission.id} Output`,
                        data: successMission,
                      })
                    }
                    className="px-3 py-1 text-[11px] font-mono rounded-xl bg-theme-card-sub text-theme-secondary hover:bg-theme-card-hover transition-colors"
                  >
                    Raw JSON
                  </button>
                </div>
              </div>
            </CardSpotlight>
          )}
        </div>

        {/* Right: Registered Missions Context List */}
        <div className="lg:col-span-6 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-4 border-b border-theme-subtle">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Database className="w-4 h-4 text-[#00D1FF]" />
                Registered Missions ({missions.length})
              </h3>
              <span className="text-[11px] font-mono text-theme-muted">
                Select to switch active telemetry target
              </span>
            </div>

            <div className="mt-4 space-y-3">
              {missions.map((mission) => {
                const isActive = activeMission?.id === mission.id;
                return (
                  <div
                    key={mission.id}
                    className={`p-4 rounded-xl border transition-all ${
                      isActive
                        ? "bg-theme-cyan-subtle border-theme-cyan shadow-sm"
                        : "bg-theme-card-sub border-theme-subtle hover:border-theme-muted"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-theme-card text-[#00D1FF]">
                            ID #{mission.id}
                          </span>
                          <h4 className="font-mono font-bold text-sm text-theme-primary">
                            {mission.mission_name}
                          </h4>
                          {isActive && (
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-theme-cyan-subtle text-[#00D1FF] border border-theme-cyan">
                              ACTIVE TARGET
                            </span>
                          )}
                        </div>

                        <div className="mt-2 text-xs font-mono text-theme-muted space-y-0.5">
                          <div>
                            Spacecraft: <span className="text-theme-secondary">{mission.spacecraft_name}</span>
                          </div>
                          <div>
                            Status: <span className="text-emerald-500">{mission.status}</span>
                          </div>
                          <div className="text-[11px] text-theme-muted flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span>{new Date(mission.created_at).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 shrink-0">
                        {!isActive ? (
                          <button
                            id={`activate-mission-btn-${mission.id}`}
                            onClick={() => setActiveMission(mission)}
                            className="px-3 py-1.5 rounded-xl text-xs font-mono bg-theme-card hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors"
                          >
                            Set Active
                          </button>
                        ) : (
                          <span className="px-3 py-1.5 rounded-xl text-xs font-mono text-[#00D1FF] bg-theme-cyan-subtle border border-theme-cyan flex items-center gap-1">
                            <Check className="w-3.5 h-3.5" />
                            <span>Active</span>
                          </span>
                        )}

                        <button
                          onClick={() =>
                            setInspectPayload({
                              title: `Mission #${mission.id} Details`,
                              data: mission,
                            })
                          }
                          className="px-2 py-1 text-[10px] font-mono text-theme-muted hover:text-theme-primary text-center"
                        >
                          View JSON
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
