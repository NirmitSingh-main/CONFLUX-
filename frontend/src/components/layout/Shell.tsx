import React, { useState } from "react";
import {
  LayoutDashboard,
  Rocket,
  Activity,
  Flame,
  Eye,
  Orbit,
  SunMedium,
  Layers,
  Server,
  ShieldCheck,
  Sun,
  Moon,
  Sparkles,
} from "lucide-react";
import { Sidebar, SidebarBody, SidebarLink } from "../ui/Sidebar";
import { Header } from "./Header";
import { InspectModal } from "../common/InspectModal";
import { useMission } from "../../context/MissionContext";
import { PageId } from "../../types";

export function Shell({ children }: { children: React.ReactNode }) {
  const {
    activePage,
    setActivePage,
    modalityState,
    systemOnline,
    healthStatus,
    theme,
    toggleTheme,
  } = useMission();

  const [open, setOpen] = useState(false);

  // Dynamic anomaly badges for sidebar navigation
  const navItems: Array<{
    id: PageId;
    label: string;
    icon: React.ReactNode;
    badge?: string;
  }> = [
    {
      id: "overview",
      label: "Overview",
      icon: <LayoutDashboard className="w-4 h-4" />,
    },
    {
      id: "missions",
      label: "Missions",
      icon: <Rocket className="w-4 h-4" />,
    },
    {
      id: "telemetry",
      label: "Telemetry",
      icon: <Activity className="w-4 h-4" />,
      badge: modalityState.telemetryAnomaly ? "ALERT" : undefined,
    },
    {
      id: "thermal",
      label: "Thermal / Imagery",
      icon: <Flame className="w-4 h-4" />,
      badge: modalityState.thermalAnomaly ? "ALERT" : undefined,
    },
    {
      id: "wavefront",
      label: "Wavefront",
      icon: <Eye className="w-4 h-4" />,
      badge: modalityState.wavefrontAnomaly ? "ALERT" : undefined,
    },
    {
      id: "orbital",
      label: "Orbital Safety",
      icon: <Orbit className="w-4 h-4" />,
      badge: modalityState.orbitalStatus === "CRITICAL" ? "CRIT" : modalityState.orbitalStatus === "WARNING" ? "WARN" : undefined,
    },
    {
      id: "weather",
      label: "Space Weather",
      icon: <SunMedium className="w-4 h-4" />,
      badge: modalityState.spaceWeatherAnomaly ? "ALERT" : undefined,
    },
    {
      id: "fusion",
      label: "Multimodal Fusion",
      icon: <Layers className="w-4 h-4" />,
    },
  ];

  return (
    <div className="flex h-screen w-full bg-theme-page text-theme-primary overflow-hidden select-none font-sans transition-colors duration-150">
      {/* Aceternity Collapsible Sidebar */}
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-6 border-r border-theme-subtle bg-theme-sidebar">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {/* Top Brand Logo */}
            <div className="flex items-center gap-3 py-2 px-1 mb-4 border-b border-theme-subtle">
              <div className="w-8 h-8 rounded-lg bg-[#111114] border border-[#2A2A2E] flex items-center justify-center shrink-0">
                <span className="text-[#00D1FF] font-mono font-bold text-xs">CX</span>
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="font-mono font-bold text-sm tracking-widest text-theme-primary truncate">
                  CONFLUX
                </span>
                <span className="text-[9px] font-mono text-[#00D1FF] truncate tracking-wider opacity-90 uppercase">
                  Mission Control
                </span>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="flex flex-col gap-1.5">
              {navItems.map((item) => (
                <SidebarLink
                  key={item.id}
                  link={{
                    id: item.id,
                    label: item.label,
                    icon: item.icon,
                    badge: item.badge,
                    active: activePage === item.id,
                    onClick: () => setActivePage(item.id),
                  }}
                />
              ))}
            </div>
          </div>

          {/* Bottom Sidebar Status Panel */}
          <div className="pt-3 border-t border-theme-subtle space-y-2">
            {/* System / API Status */}
            <div className="px-2.5 py-1.5 rounded-lg bg-theme-card-sub border border-theme-subtle text-[11px] font-mono flex items-center justify-between">
              <div className="flex items-center gap-2 truncate">
                <Server className="w-3.5 h-3.5 text-theme-muted shrink-0" />
                <span className="text-theme-muted truncate text-[10px] uppercase">API Status</span>
              </div>
              <span
                className={`px-1.5 py-0.5 rounded text-[9px] uppercase font-mono font-bold tracking-wider ${
                  healthStatus === "healthy"
                    ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                    : healthStatus === "checking"
                    ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                    : "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                }`}
              >
                {healthStatus === "healthy" ? "Online" : healthStatus === "checking" ? "Ping" : "Offline"}
              </span>
            </div>

            {/* Quick Theme Switch inside Sidebar */}
            <button
              id="sidebar-theme-toggle"
              onClick={toggleTheme}
              className="w-full px-2.5 py-1.5 rounded-lg bg-theme-card-sub hover:bg-theme-card-hover border border-theme-subtle text-[11px] font-mono text-theme-secondary hover:text-theme-primary flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-2">
                {theme === "dark" ? (
                  <Moon className="w-3.5 h-3.5 text-[#00D1FF]" />
                ) : (
                  <Sun className="w-3.5 h-3.5 text-amber-500" />
                )}
                <span className="text-[10px] uppercase font-mono">Theme</span>
              </div>
              <span className="text-[10px] uppercase text-theme-muted font-semibold font-mono">
                {theme}
              </span>
            </button>
          </div>
        </SidebarBody>
      </Sidebar>

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 h-screen overflow-hidden bg-theme-page">
        <Header />
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 md:p-8 bg-theme-page">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>

      {/* Inspect Raw Modal */}
      <InspectModal />
    </div>
  );
}
