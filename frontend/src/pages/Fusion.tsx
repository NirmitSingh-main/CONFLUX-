import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Layers,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Activity,
  Flame,
  Eye,
  Orbit,
  SunMedium,
  RefreshCw,
  Database,
  Send,
  ShieldCheck,
  Cpu,
  AlertCircle,
  Info,
  Loader2,
} from "lucide-react";
import { requestJson } from "../api/client";
import { getLatestFusion } from "../api/fusion";
import { retrieveMissionGuidance } from "../api/rag";
import { useMission } from "../context/MissionContext";
import { FusionResponse, RagResponse } from "../types";
import { CardSpotlight } from "../components/ui/CardSpotlight";

// --------------------------------------------------
// POST /fusion/ — send modality list; backend loads latest DB analysis per modality
// --------------------------------------------------
async function runFusion(mission_id: number, modalities: string[]): Promise<FusionResponse> {
  return requestJson<FusionResponse>("/fusion/", {
    method: "POST",
    body: JSON.stringify({ mission_id, modalities }),
  });
}

// --------------------------------------------------
// Modality config
// KEY must match exactly what the backend fusion service expects.
// "wavefront" NOT "wavelet" — backend reads from wavefront_analyses table.
// --------------------------------------------------
const MODALITY_CONFIG = [
  {
    key: "orbital",
    name: "Orbital Safety",
    icon: <Orbit className="w-4 h-4" />,
    desc: "Conjunction & Miss Distance",
    color: "cyan",
  },
  {
    key: "space_weather",
    name: "Space Weather",
    icon: <SunMedium className="w-4 h-4" />,
    desc: "Solar, Radiation & Geomagnetic Flux",
    color: "amber",
  },
  {
    key: "telemetry",
    name: "Telemetry",
    icon: <Activity className="w-4 h-4" />,
    desc: "Subsystem Power & Pressure",
    color: "cyan",
  },
  {
    key: "thermal",
    name: "Thermal / Infrared",
    icon: <Flame className="w-4 h-4" />,
    desc: "Radiometric Hotspot Detector",
    color: "amber",
  },
  {
    key: "wavefront",   // ← FIXED: was "wavelet" which backend doesn't recognise
    name: "Wavefront Optics",
    icon: <Eye className="w-4 h-4" />,
    desc: "Zernike & Wavelet Aberrations",
    color: "cyan",
  },
];

function getSeverityColor(severity: string | undefined): string {
  switch ((severity || "").toUpperCase()) {
    case "CRITICAL": return "text-rose-500";
    case "HIGH":     return "text-rose-400";
    case "MEDIUM":   return "text-amber-500";
    default:         return "text-emerald-500";
  }
}

function getOverallVariant(result: FusionResponse): "critical" | "warning" | "nominal" {
  const sev = (result.overall_severity || "").toUpperCase();
  if (sev === "CRITICAL" || sev === "HIGH") return "critical";
  if (sev === "MEDIUM") return "warning";
  return "nominal";
}

// --------------------------------------------------
// "NOT ANALYZED" empty state panel
// --------------------------------------------------
function NotAnalyzed({ missionId }: { missionId: number }) {
  return (
    <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub p-8 flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-2xl bg-theme-card border border-theme-subtle flex items-center justify-center text-theme-muted mb-4">
        <Layers className="w-8 h-8 text-[#00D1FF]/50" />
      </div>
      <h4 className="font-mono text-sm font-semibold text-theme-primary uppercase tracking-wider">
        No Fusion Analysis for Mission #{missionId}
      </h4>
      <p className="text-xs text-theme-muted max-w-sm mt-1.5 font-sans">
        First run individual modality analyses (Orbital, Space Weather, Telemetry, Thermal, Wavefront),
        then click <strong>Execute Multimodal Fusion</strong> to synthesize results.
      </p>
      <p className="text-[10px] text-theme-muted max-w-sm mt-2 font-mono">
        Or click "Load Latest" to retrieve a previously stored fusion result.
      </p>
      <div className="mt-5 pt-4 border-t border-theme-subtle text-[10px] font-mono uppercase tracking-wider text-theme-muted">
        <span className="text-[#00D1FF]">Mission Knowledge &amp; Guidance</span>
        <div className="mt-1">RUN MULTIMODAL FUSION FIRST</div>
      </div>
    </div>
  );
}

// --------------------------------------------------
// Main component
// --------------------------------------------------
export function Fusion() {
  const { activeMission, updateFusionResult, setInspectPayload } = useMission();

  const missionId = activeMission?.id ?? 1;

  // Which modalities to include — controls what backend loads from DB.
  // Checkboxes do NOT determine anomaly state; they only select which
  // modalities the backend should look up.
  const [selectedModalities, setSelectedModalities] = useState<Set<string>>(
    new Set(["orbital", "space_weather", "telemetry", "thermal", "wavefront"])
  );

  const [loading, setLoading]           = useState(false);
  const [loadingLatest, setLoadingLatest] = useState(false);
  const [error, setError]               = useState<string | null>(null);
  const [result, setResult]             = useState<FusionResponse | null>(null);
  // null = loading, false = no analysis found, FusionResponse = loaded
  const [autoLoaded, setAutoLoaded]     = useState<boolean | null>(null);
  const latestRequest = useRef(0);
  const ragRequest = useRef(0);
  const [ragResult, setRagResult] = useState<RagResponse | null>(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [ragError, setRagError] = useState<string | null>(null);
  const ragAssessmentKey = useRef<string | null>(null);

  const resetRag = () => {
    ++ragRequest.current;
    ragAssessmentKey.current = null;
    setRagResult(null);
    setRagError(null);
    setRagLoading(false);
  };

  // ── Auto-load latest fusion on mission switch ──────────────────────────────
  const loadLatestSilent = useCallback(async (mid: number) => {
    const requestId = ++latestRequest.current;
    setAutoLoaded(null);    // loading
    setResult(null);
    setError(null);
    try {
      const latest = await getLatestFusion(mid);
      if (requestId !== latestRequest.current) return;
      if (latest) {
        setResult(latest);
        updateFusionResult(latest);
        setAutoLoaded(true);
      } else {
        setAutoLoaded(false);
      }
    } catch (err: any) {
      if (requestId !== latestRequest.current) return;
      // 404 = no analysis yet — not an error to surface
      if (err?.status === 404 || (err?.message || "").includes("404")) {
        setAutoLoaded(false);
      } else {
        setAutoLoaded(false);
        // Only surface network errors (backend offline etc.)
        if (err?.status === 0 || (err?.message || "").toLowerCase().includes("network")) {
          setError(err.message);
        }
      }
    }
  }, [updateFusionResult]);

  useEffect(() => {
    loadLatestSilent(missionId);
  }, [missionId, loadLatestSilent]);

  useEffect(() => {
    if (!result || result.mission_id !== missionId) {
      ++ragRequest.current;
      ragAssessmentKey.current = null;
      setRagResult(null);
      setRagError(null);
      setRagLoading(false);
      return;
    }

    const assessmentKey = `${missionId}:${result.id ?? result.created_at ?? "current"}`;
    if (ragAssessmentKey.current === assessmentKey) return;
    ragAssessmentKey.current = assessmentKey;

    const requestId = ++ragRequest.current;
    setRagResult(null);
    setRagError(null);
    setRagLoading(true);
    retrieveMissionGuidance(missionId, result)
      .then((guidance) => {
        if (requestId === ragRequest.current) setRagResult(guidance);
      })
      .catch((err: any) => {
        if (requestId === ragRequest.current) {
          setRagError(err.message || "Failed to retrieve mission guidance.");
        }
      })
      .finally(() => {
        if (requestId === ragRequest.current) setRagLoading(false);
      });
  }, [missionId, result]);

  // ── Manual "Load Latest" button ────────────────────────────────────────────
  const handleLoadLatest = async () => {
    const requestId = ++latestRequest.current;
    setLoadingLatest(true);
    setError(null);
    resetRag();
    try {
      const latest = await getLatestFusion(missionId);
      if (requestId !== latestRequest.current) return;
      if (latest) {
        setResult(latest);
        updateFusionResult(latest);
      } else {
        setError(`No fusion analysis found for Mission #${missionId}. Run analyses first.`);
      }
    } catch (err: any) {
      if (requestId !== latestRequest.current) return;
      if (err?.status === 404 || (err?.message || "").includes("404")) {
        setError(`No fusion analysis found for Mission #${missionId}. Run analyses first.`);
      } else {
        setError(err.message || "Failed to load latest fusion result.");
      }
    } finally {
      setLoadingLatest(false);
    }
  };

  const handleToggleModality = (key: string) => {
    setSelectedModalities((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  // ── Execute Fusion ─────────────────────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedModalities.size === 0) {
      setError("Select at least one modality to include in fusion.");
      return;
    }
    setLoading(true);
    setError(null);
    resetRag();
    const requestId = ++latestRequest.current;
    try {
      const response = await runFusion(missionId, Array.from(selectedModalities));
      if (requestId !== latestRequest.current) return;
      setResult(response);
      updateFusionResult(response);
    } catch (err: any) {
      if (requestId !== latestRequest.current) return;
      setError(err.message || "Failed to execute multimodal fusion analysis.");
    } finally {
      setLoading(false);
    }
  };

  const overallVariant = result ? getOverallVariant(result) : "nominal";

  // ── Render right panel ─────────────────────────────────────────────────────
  const renderResults = () => {
    // Still auto-loading on mission switch
    if (autoLoaded === null) {
      return (
        <div className="h-full min-h-[380px] rounded-2xl border border-theme-subtle bg-theme-card-sub flex items-center justify-center">
          <div className="flex items-center gap-2 text-theme-muted font-mono text-xs">
            <Loader2 className="w-4 h-4 animate-spin text-[#00D1FF]" />
            <span>Loading latest fusion for Mission #{missionId}…</span>
          </div>
        </div>
      );
    }

    if (result) {
      return (
        <div className="space-y-4">
          {/* Primary Assessment Spotlight */}
          <CardSpotlight id="fusion-assessment-spotlight" variant={overallVariant} className="bg-theme-card border-theme-subtle">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className={`p-2.5 rounded-xl border ${
                  overallVariant === "critical" ? "bg-rose-500/20 text-rose-500 border-rose-500/40"
                  : overallVariant === "warning" ? "bg-amber-500/20 text-amber-500 border-amber-500/40"
                  : "bg-emerald-500/20 text-emerald-500 border-emerald-500/40"
                }`}>
                  {overallVariant === "critical" ? <AlertOctagon className="w-6 h-6 animate-pulse" />
                  : overallVariant === "warning"  ? <AlertTriangle className="w-6 h-6" />
                  : <ShieldCheck className="w-6 h-6" />}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-[10px] font-mono font-bold uppercase px-2.5 py-0.5 rounded-full border ${
                      overallVariant === "critical" ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                      : overallVariant === "warning" ? "bg-amber-500/10 text-amber-500 border-amber-500/30"
                      : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                    }`}>CONFLUX ASSESSMENT</span>
                    <span className="text-xs font-mono text-theme-muted">
                      Mission #{result.mission_id}{result.mission_name && ` — ${result.mission_name}`}
                    </span>
                  </div>
                  <h3 className="text-base font-mono font-bold mt-1.5 text-theme-primary">
                    {result.primary_problem || `${result.anomaly_count ?? 0} modalities indicate anomalous behaviour`}
                  </h3>
                </div>
              </div>
              <button
                id="inspect-fusion-json-btn"
                onClick={() => setInspectPayload({ title: "Multimodal Fusion Response", data: result })}
                className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub hover:bg-theme-card-hover text-theme-primary border border-theme-subtle transition-colors shrink-0"
              >Raw Output</button>
            </div>
          </CardSpotlight>

          {/* Per-Modality Status Matrix */}
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                Modality Status (from DB analyses)
              </h4>
              <span className="text-[11px] font-mono text-theme-muted flex items-center gap-1">
                <Database className="w-3 h-3 text-[#00D1FF]" />
                <span>{result.stored_in_database ? "Persisted" : "Evaluated"}</span>
              </span>
            </div>
            <div className="space-y-2.5">
              {MODALITY_CONFIG.map((mod) => {
                const state        = result.modality_states?.[mod.key];
                const isUnavailable = result.unavailable_modalities?.includes(mod.key) || (!state && !result.anomalous_modalities?.includes(mod.key) && !result.normal_modalities?.includes(mod.key));
                const isAnomaly    = result.anomalous_modalities?.includes(mod.key);
                const label        = isUnavailable ? "NOT ANALYZED" : isAnomaly ? "ANOMALOUS" : "NORMAL";

                return (
                  <div key={mod.key} className={`p-3.5 rounded-xl border flex items-center justify-between transition-colors ${
                    isUnavailable ? "bg-theme-card-sub border-theme-subtle opacity-60"
                    : isAnomaly   ? "bg-rose-500/10 border-rose-500/30"
                    : "bg-emerald-500/5 border-emerald-500/20"
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className={`p-2.5 rounded-xl ${
                        isUnavailable ? "bg-theme-card text-theme-muted border border-theme-subtle"
                        : isAnomaly   ? "bg-rose-500/20 text-rose-500 border border-rose-500/30"
                        : "bg-emerald-500/20 text-emerald-500 border border-emerald-500/30"
                      }`}>{mod.icon}</div>
                      <div>
                        <div className="font-mono text-xs font-bold text-theme-primary">{mod.name}</div>
                        <div className="text-[11px] font-sans text-theme-muted">
                          {isUnavailable ? "No analysis found in database for this mission"
                          : `${mod.desc}${state?.severity && state.severity !== "UNKNOWN" ? ` · Severity: ${state.severity}` : ""}`}
                        </div>
                        {state?.confidence != null && !isUnavailable && (
                          <div className="text-[10px] font-mono text-theme-muted mt-0.5">
                            Confidence: {(state.confidence * 100).toFixed(0)}%
                          </div>
                        )}
                      </div>
                    </div>
                    <span className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded-full border tracking-wider ${
                      isUnavailable ? "bg-theme-card-sub text-theme-muted border-theme-subtle"
                      : isAnomaly   ? "bg-rose-500/10 text-rose-500 border-rose-500/30"
                      : "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
                    }`}>{label}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Assessment Details */}
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5 space-y-4">
            <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary pb-3 border-b border-theme-subtle">
              Multimodal Assessment
            </h4>

            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">PRIMARY MISSION ISSUE</span>
              <div className={`font-mono text-sm font-bold ${getSeverityColor(result.overall_severity)}`}>
                {result.primary_problem || "—"}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <span className="text-[10px] font-mono text-theme-muted block">OVERALL RISK</span>
                <span className={`text-sm font-mono font-bold ${getSeverityColor(result.risk_level || result.overall_severity)}`}>
                  {result.risk_level || result.overall_severity || "—"}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                <span className="text-[10px] font-mono text-theme-muted block">SEVERITY</span>
                <span className={`text-sm font-mono font-bold ${getSeverityColor(result.overall_severity)}`}>
                  {result.overall_severity || "—"}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
              <span className="text-[10px] font-mono text-theme-muted block mb-1">FUSION CONFIDENCE</span>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-theme-card rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-2 rounded-full ${
                      (result.confidence || 0) > 0.75 ? "bg-emerald-500"
                      : (result.confidence || 0) > 0.5  ? "bg-amber-500"
                      : "bg-rose-500"
                    }`}
                    style={{ width: `${Math.round((result.confidence || 0) * 100)}%` }}
                  />
                </div>
                <span className="text-sm font-mono font-bold text-theme-primary">
                  {result.confidence != null ? `${(result.confidence * 100).toFixed(0)}%` : "—"}
                </span>
              </div>
            </div>

            {result.correlated_events && result.correlated_events.length > 0 && (
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-2">CORRELATED EVIDENCE</span>
                <div className="flex flex-wrap gap-1.5">
                  {result.correlated_events.map((ev: string, idx: number) => (
                    <span key={idx} className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-[#00D1FF]/10 text-[#00D1FF] border border-[#00D1FF]/30">
                      {ev.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.explanation && (
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">EXPLANATION</span>
                <p className="text-xs font-sans text-theme-secondary leading-relaxed">{result.explanation}</p>
              </div>
            )}

            {result.recommended_action && (
              <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20">
                <span className="text-[10px] font-mono uppercase tracking-wider text-amber-500 block mb-1 font-bold">RECOMMENDED ACTION</span>
                <p className="text-xs font-sans text-theme-secondary leading-relaxed">{result.recommended_action}</p>
              </div>
            )}
          </div>

          {/* Grounded knowledge retrieval after the observed Fusion assessment */}
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle">
              <h4 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary">
                Mission Knowledge &amp; Guidance
              </h4>
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#00D1FF]">RAG Intelligence</span>
            </div>

            {ragLoading && (
              <div className="space-y-1 text-xs font-mono text-[#00D1FF]">
                <div className="flex items-center gap-2 uppercase tracking-wider">
                <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Retrieving Mission Knowledge...</span>
                </div>
                <p className="text-[11px] text-theme-muted pl-6 normal-case tracking-normal">
                  Analyzing the current Fusion assessment and searching the technical knowledge base.
                </p>
              </div>
            )}

            {ragError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
                Knowledge retrieval failed: {ragError}
              </div>
            )}

            {ragResult && !ragLoading && (
              <>
                <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-500 flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Knowledge Analysis Complete
                  </span>
                  <span className="text-[10px] font-mono text-theme-muted">
                    {ragResult.evidence.length} relevant technical source{ragResult.evidence.length === 1 ? "" : "s"} retrieved
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[10px] font-mono uppercase tracking-wider">
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
                    <span className="block mb-1 text-[#00D1FF]">Observed</span>
                    Latest persisted modality results for Mission #{missionId}
                  </div>
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
                    <span className="block mb-1 text-amber-500">Inferred</span>
                    {result.primary_problem || result.overall_severity || "Mission assessment"}
                  </div>
                  <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
                    <span className="block mb-1 text-[#00D1FF]">Retrieved Knowledge</span>
                    Evidence from the local knowledge base
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">RETRIEVED EVIDENCE</span>
                  {ragResult.evidence.length ? (
                    <div className="space-y-2">
                      {ragResult.evidence.map((item) => (
                        <div key={item.chunk_id} className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle">
                          <div className="flex items-start justify-between gap-3">
                            <span className="text-xs font-mono font-semibold text-theme-primary">{item.title}</span>
                            <span className="text-[10px] font-mono text-[#00D1FF]">{(item.relevance_score * 100).toFixed(1)}%</span>
                          </div>
                          <span className="inline-block mt-1 text-[9px] font-mono uppercase tracking-wider text-amber-500">Development / Demo Knowledge</span>
                          <div className="text-[10px] font-mono text-theme-muted mt-1">
                            {item.section || item.source}{item.page_number ? ` · Page ${item.page_number}` : ""}
                          </div>
                          <p className="text-xs text-theme-secondary leading-relaxed mt-2">{item.excerpt}</p>
                        </div>
                      ))}
                    </div>
                  ) : <p className="text-xs font-mono text-theme-muted">{ragResult.retrieval_status.replace(/_/g, " ")}</p>}
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">TECHNICAL INTERPRETATION</span>
                  <p className="text-xs text-theme-secondary leading-relaxed">{ragResult.technical_interpretation}</p>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-amber-500 block mb-1">RECOMMENDED ACTION · OPERATIONAL GUIDANCE</span>
                  {ragResult.recommendations.length ? (
                    <ul className="space-y-1 text-xs text-theme-secondary">
                      {ragResult.recommendations.map((item, index) => <li key={index}>• {item}</li>)}
                    </ul>
                  ) : <p className="text-xs font-mono text-theme-muted">No guidance supported by retrieved evidence.</p>}
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-theme-muted block mb-1">SOURCES</span>
                  {ragResult.source_entries?.length ? (
                    <div className="space-y-2">
                      {ragResult.source_entries.map((source) => (
                        <div key={source.source} className="text-xs font-mono text-theme-muted">
                          <div className="text-theme-primary">• {source.title}</div>
                          <div className="pl-3 text-[10px]">{source.source}</div>
                          <div className="pl-3 text-[9px] uppercase tracking-wider text-amber-500">Development / Demo Knowledge</div>
                        </div>
                      ))}
                    </div>
                  ) : <p className="text-xs font-mono text-theme-muted">None</p>}
                </div>
              </>
            )}
          </div>

          {/* Anomalous / Normal breakdown */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
              <span className="text-[10px] font-mono text-rose-500 uppercase tracking-wider block mb-2 font-bold">
                ANOMALOUS ({result.anomalous_modalities?.length || 0})
              </span>
              {result.anomalous_modalities?.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {result.anomalous_modalities.map((m: string, i: number) => (
                    <span key={i} className="text-xs font-mono px-2.5 py-1 rounded-lg bg-rose-500/15 text-rose-500 border border-rose-500/30">{m}</span>
                  ))}
                </div>
              ) : <span className="text-xs font-mono text-theme-muted">None detected</span>}
            </div>
            <div className="rounded-2xl border border-theme-subtle bg-theme-card p-4">
              <span className="text-[10px] font-mono text-emerald-500 uppercase tracking-wider block mb-2 font-bold">
                NORMAL ({result.normal_modalities?.length || 0})
              </span>
              {result.normal_modalities?.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {result.normal_modalities.map((m: string, i: number) => (
                    <span key={i} className="text-xs font-mono px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-500 border border-emerald-500/30">{m}</span>
                  ))}
                </div>
              ) : <span className="text-xs font-mono text-theme-muted">None</span>}
            </div>
          </div>

          {result.unavailable_modalities && result.unavailable_modalities.length > 0 && (
            <div className="p-3 rounded-xl bg-theme-card-sub border border-theme-subtle flex items-start gap-2 text-xs font-mono text-theme-muted">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-theme-muted" />
              <span>
                No analysis data for: <strong>{result.unavailable_modalities.join(", ")}</strong>.
                These were marked as NOT ANALYZED — run those modality analyses first.
              </span>
            </div>
          )}
        </div>
      );
    }

    // No result (404 / not analyzed yet)
    return <NotAnalyzed missionId={missionId} />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-theme-subtle">
        <div>
          <h2 className="text-xl font-mono font-semibold text-theme-primary uppercase tracking-wide flex items-center gap-2">
            <Layers className="w-5 h-5 text-[#00D1FF]" />
            Multimodal Fusion & Consensus Engine
          </h2>
          <p className="text-xs text-theme-muted font-sans mt-1">
            Cross-modal intelligence synthesis. Fusion reads <strong>persisted</strong> analysis results from the database — not UI state.
          </p>
        </div>
        <div className="text-xs font-mono px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted">
          Mission <span className="text-[#00D1FF]">#{missionId}</span> · <code className="text-[#00D1FF]">POST /fusion/</code>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Config panel */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-2xl border border-theme-subtle bg-theme-card p-6 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-theme-subtle mb-4">
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-theme-primary flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#00D1FF]" />
                Fusion Configuration
              </h3>
              <button
                type="button"
                onClick={handleLoadLatest}
                disabled={loadingLatest}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#00D1FF]/10 hover:bg-[#00D1FF]/20 text-[#00D1FF] border border-[#00D1FF]/30 font-mono text-[11px] font-semibold transition-colors disabled:opacity-50"
                title="Load latest fusion result for current mission from database"
              >
                {loadingLatest ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Database className="w-3.5 h-3.5" />}
                <span>{loadingLatest ? "Loading…" : "Load Latest"}</span>
              </button>
            </div>

            {/* Info banner */}
            <div className="mb-4 p-3 rounded-xl bg-[#00D1FF]/5 border border-[#00D1FF]/20 text-[#00D1FF] text-[11px] font-mono flex items-start gap-2">
              <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>
                Fusion reads the <strong>latest persisted analyses</strong> from the database for Mission #{missionId}.
                Checkboxes control <em>which</em> modalities are included — they do <strong>NOT</strong> determine anomaly status.
              </span>
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                <div><span className="font-bold">Error: </span>{error}</div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Modality toggles */}
              <div className="space-y-2.5">
                <span className="text-[10px] font-mono text-theme-muted block uppercase tracking-wider">
                  Include in Fusion (loads latest DB analysis per modality):
                </span>
                {MODALITY_CONFIG.map((mod) => (
                  <label
                    key={mod.key}
                    className="flex items-center justify-between p-3.5 rounded-xl bg-theme-card-sub border border-theme-subtle hover:border-theme-muted cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className={mod.color === "amber" ? "text-amber-500" : "text-[#00D1FF]"}>
                        {mod.icon}
                      </span>
                      <div>
                        <span className="text-xs font-mono text-theme-primary block font-medium">{mod.name}</span>
                        <span className="text-[10px] text-theme-muted font-mono">{mod.desc}</span>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={selectedModalities.has(mod.key)}
                      onChange={() => handleToggleModality(mod.key)}
                      className="w-4 h-4 accent-[#00D1FF] rounded cursor-pointer"
                    />
                  </label>
                ))}
              </div>

              <div className="pt-2">
                <button
                  id="submit-fusion-btn"
                  type="submit"
                  disabled={loading || selectedModalities.size === 0}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-theme-primary text-theme-page hover:opacity-90 disabled:opacity-50 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /><span>Synthesizing Modalities…</span></>
                  ) : (
                    <><Send className="w-4 h-4 text-[#00D1FF]" /><span>Execute Multimodal Fusion (POST /fusion/)</span></>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-7 space-y-4">
          {renderResults()}
        </div>
      </div>
    </div>
  );
}
