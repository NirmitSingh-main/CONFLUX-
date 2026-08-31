import React, { useState } from "react";
import {
  Activity,
  Radio,
  Server,
  RefreshCw,
  Sun,
  Moon,
  ChevronDown,
  Plus,
  Settings,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react";
import { useMission } from "../../context/MissionContext";
import { PageId } from "../../types";

const PAGE_TITLES: Record<PageId, { title: string; subtitle: string; question: string }> = {
  overview: {
    title: "Mission Overview",
    subtitle: "High-level multimodal mission intelligence",
    question: "What is happening with the mission right now?",
  },
  missions: {
    title: "Mission Configuration",
    subtitle: "Mission registration & active context management",
    question: "Which mission/spacecraft am I analyzing?",
  },
  telemetry: {
    title: "Telemetry Intelligence",
    subtitle: "Real-time subsystem sensor & anomaly detection",
    question: "Is spacecraft telemetry behaving normally?",
  },
  thermal: {
    title: "Thermal / Infrared Imagery",
    subtitle: "Optical & radiometric hotspot anomaly analysis",
    question: "Is there a thermal/infrared anomaly?",
  },
  wavefront: {
    title: "Wavefront Optical System",
    subtitle: "Multi-modal optical aberration & wavelet decomposition",
    question: "Is the optical/wavefront system behaving normally?",
  },
  orbital: {
    title: "Orbital Safety & Conjunction",
    subtitle: "Close approach & collision risk evaluation",
    question: "Are there dangerous orbital close approaches?",
  },
  weather: {
    title: "Space Weather Conditions",
    subtitle: "Solar, radiation & geomagnetic disturbance tracking",
    question: "Are environmental conditions affecting the mission?",
  },
  fusion: {
    title: "Multimodal Fusion Engine",
    subtitle: "Cross-modality synthesis & agreement analysis",
    question: "What does CONFLUX conclude when multiple modalities are considered?",
  },
};

export function Header() {
  const {
    activePage,
    setActivePage,
    activeMission,
    setActiveMission,
    missions,
    systemOnline,
    healthStatus,
    systemName,
    isCheckingHealth,
    checkConnection,
    apiUrl,
    updateApiUrl,
    theme,
    toggleTheme,
  } = useMission();

  const [isMissionDropdownOpen, setIsMissionDropdownOpen] = useState(false);
  const [isApiSettingsOpen, setIsApiSettingsOpen] = useState(false);
  const [tempApiUrl, setTempApiUrl] = useState(apiUrl);

  const pageInfo = PAGE_TITLES[activePage] || PAGE_TITLES.overview;

  const handleSaveApiUrl = (e: React.FormEvent) => {
    e.preventDefault();
    updateApiUrl(tempApiUrl);
    setIsApiSettingsOpen(false);
  };

  return (
    <header className="sticky top-0 z-20 w-full border-b border-theme-subtle bg-theme-header backdrop-blur-md px-6 py-3 transition-colors">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: Page Title & Focus Question */}
        <div className="flex items-center gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-base font-mono font-semibold text-theme-primary uppercase tracking-widest">
                {pageInfo.title}
              </h1>
              <span className="hidden sm:inline-block text-[10px] font-mono px-2 py-0.5 rounded-md bg-theme-cyan-subtle border border-theme-cyan text-[#00D1FF] font-medium tracking-wide">
                {systemName} CORE
              </span>
            </div>
            <p className="text-xs text-theme-muted font-sans tracking-wide mt-0.5">
              {pageInfo.question}
            </p>
          </div>
        </div>

        {/* Right Controls: Mission Selector, Backend Status, Settings, Theme */}
        <div className="flex items-center flex-wrap gap-2.5">
          {/* Active Mission Selector */}
          <div className="relative">
            <button
              id="active-mission-selector-btn"
              onClick={() => setIsMissionDropdownOpen(!isMissionDropdownOpen)}
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-xs font-mono text-theme-primary hover:border-theme-hover hover:bg-theme-card-hover transition-all shadow-sm"
            >
              <Radio className="w-3.5 h-3.5 text-[#00D1FF]" />
              <div className="text-left">
                <span className="text-[9px] text-theme-muted block tracking-wider uppercase">Mission Context</span>
                <span className="font-semibold text-theme-primary">
                  {activeMission ? `ID #${activeMission.id} · ${activeMission.mission_name}` : "No Mission Selected"}
                </span>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-theme-muted ml-1" />
            </button>

            {/* Dropdown menu */}
            {isMissionDropdownOpen && (
              <div className="absolute right-0 mt-2 w-72 bg-theme-card border border-theme-subtle rounded-2xl shadow-2xl z-50 overflow-hidden py-1 backdrop-blur-xl">
                <div className="px-3.5 py-2.5 border-b border-theme-subtle text-[10px] font-mono text-theme-muted flex items-center justify-between uppercase tracking-wider">
                  <span>Select Active Mission</span>
                  <span className="text-[#00D1FF]">{missions.length} Registered</span>
                </div>
                <div className="max-h-60 overflow-y-auto">
                  {missions.map((m) => (
                    <button
                      key={m.id}
                      onClick={() => {
                        setActiveMission(m);
                        setIsMissionDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3.5 py-2.5 text-xs hover:bg-theme-card-hover flex items-center justify-between transition-colors ${
                        activeMission?.id === m.id ? "bg-theme-cyan-subtle text-[#00D1FF] font-semibold border-l-2 border-[#00D1FF]" : "text-theme-secondary"
                      }`}
                    >
                      <div>
                        <div className="font-mono font-medium text-theme-primary">{m.mission_name}</div>
                        <div className="text-[11px] text-theme-muted font-sans">
                          Spacecraft: {m.spacecraft_name}
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-theme-card-sub border border-theme-subtle text-theme-muted">
                        ID #{m.id}
                      </span>
                    </button>
                  ))}
                </div>
                <div className="p-2 border-t border-theme-subtle bg-theme-card-sub">
                  <button
                    id="create-new-mission-header-btn"
                    onClick={() => {
                      setIsMissionDropdownOpen(false);
                      setActivePage("missions");
                    }}
                    className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-theme-card hover:bg-theme-card-hover border border-theme-subtle text-theme-primary font-mono text-xs font-semibold transition-all"
                  >
                    <Plus className="w-3.5 h-3.5 text-[#00D1FF]" />
                    <span>Create New Mission</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Backend Status Badge & Refresh */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-theme-card-sub border border-theme-subtle text-xs font-mono">
            <span className="relative flex h-2 w-2">
              {healthStatus === "healthy" && (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </>
              )}
              {healthStatus === "checking" && (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-400 animate-pulse"></span>
              )}
              {healthStatus === "offline" && (
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              )}
            </span>

            <span className="text-[10px] uppercase font-mono tracking-widest text-theme-secondary">
              {healthStatus === "healthy" ? "127.0.0.1:8000" : healthStatus === "checking" ? "PINGING..." : "OFFLINE"}
            </span>

            <button
              id="refresh-backend-status-btn"
              title="Ping Backend Health (/health)"
              onClick={checkConnection}
              disabled={isCheckingHealth}
              className="p-1 rounded-md text-theme-muted hover:text-[#00D1FF] hover:bg-theme-card-hover transition-colors ml-0.5"
            >
              <RefreshCw className={`w-3 h-3 ${isCheckingHealth ? "animate-spin text-[#00D1FF]" : ""}`} />
            </button>
          </div>

          {/* API Base URL Config Button */}
          <button
            id="open-api-config-btn"
            title="Configure Backend URL (Default: http://127.0.0.1:8000)"
            onClick={() => {
              setTempApiUrl(apiUrl);
              setIsApiSettingsOpen(true);
            }}
            className="p-2 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted hover:text-theme-primary hover:border-theme-hover transition-colors"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* Theme Toggle */}
          <button
            id="theme-toggle-btn"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-theme-card-sub border border-theme-subtle text-theme-muted hover:text-theme-primary hover:border-theme-hover transition-colors"
          >
            {theme === "dark" ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-[#00D1FF]" />}
          </button>
        </div>
      </div>

      {/* API Endpoint Config Modal */}
      {isApiSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in">
          <div className="w-full max-w-md bg-theme-card border border-theme-subtle rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-theme-subtle">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-[#00D1FF]" />
                <h3 className="font-mono text-xs font-semibold text-theme-primary uppercase tracking-wider">
                  FastAPI Backend Endpoint
                </h3>
              </div>
              <button
                onClick={() => setIsApiSettingsOpen(false)}
                className="text-theme-muted hover:text-theme-primary"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveApiUrl} className="mt-4 space-y-4">
              <div>
                <label className="block text-[10px] font-mono uppercase tracking-wider text-theme-secondary mb-1.5">
                  Backend Base URL
                </label>
                <input
                  id="api-url-input"
                  type="text"
                  value={tempApiUrl}
                  onChange={(e) => setTempApiUrl(e.target.value)}
                  placeholder="http://127.0.0.1:8000"
                  className="w-full px-3 py-2 rounded-xl bg-theme-input border border-theme-subtle font-mono text-xs text-theme-primary focus:outline-none focus:border-[#00D1FF]"
                  required
                />
                <p className="mt-1.5 text-[11px] text-theme-muted">
                  Default: <code className="text-[#00D1FF]">http://127.0.0.1:8000</code>. Connects directly to CONFLUX FastAPI endpoints.
                </p>
              </div>

              <div className="rounded-xl bg-theme-card-sub p-3.5 border border-theme-subtle text-xs font-mono space-y-1">
                <div className="text-theme-muted text-[10px] uppercase tracking-wider mb-1">Target Endpoints:</div>
                <div className="text-theme-secondary text-[11px]">• GET / · GET /health</div>
                <div className="text-theme-secondary text-[11px]">• POST /missions/ · POST /telemetry/</div>
                <div className="text-theme-secondary text-[11px]">• POST /imagery/ · POST /wavefront/</div>
                <div className="text-theme-secondary text-[11px]">• POST /orbital/ · POST /space-weather/</div>
                <div className="text-theme-secondary text-[11px]">• POST /fusion/</div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setTempApiUrl("http://127.0.0.1:8000")}
                  className="px-3 py-1.5 text-xs font-mono rounded-xl bg-theme-card-sub text-theme-secondary hover:bg-theme-card-hover border border-theme-subtle transition-colors"
                >
                  Reset Default
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 text-xs font-mono font-semibold rounded-xl bg-theme-card hover:bg-theme-card-hover border border-theme-subtle text-theme-primary transition-all"
                >
                  Save & Re-Ping
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}
