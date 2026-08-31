import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  Mission,
  PageId,
  ModalityStateSnapshot,
  TelemetryResponse,
  ImageryResponse,
  WavefrontResponse,
  OrbitalResponse,
  SpaceWeatherResponse,
  FusionResponse,
} from "../types";
import { getSystemStatus, getHealth } from "../api/system";
import { getMissions } from "../api/missions";
import { getApiBaseUrl, setApiBaseUrl } from "../api/client";

interface MissionContextType {
  // Navigation
  activePage: PageId;
  setActivePage: (page: PageId) => void;

  // Active Mission & Store
  activeMission: Mission | null;
  setActiveMission: (mission: Mission | null) => void;
  missions: Mission[];
  addMission: (mission: Mission) => void;
  refreshMissions: () => Promise<void>;

  // Modality States (Mission Intelligence state)
  modalityState: ModalityStateSnapshot;
  updateTelemetryResult: (res: TelemetryResponse) => void;
  updateImageryResult: (res: ImageryResponse) => void;
  updateWavefrontResult: (res: WavefrontResponse) => void;
  updateOrbitalResult: (res: OrbitalResponse) => void;
  updateWeatherResult: (res: SpaceWeatherResponse) => void;
  updateFusionResult: (res: FusionResponse) => void;

  // System & Health Connection
  systemOnline: boolean;
  healthStatus: "healthy" | "unhealthy" | "checking" | "offline";
  systemName: string;
  isCheckingHealth: boolean;
  checkConnection: () => Promise<void>;

  // API Config
  apiUrl: string;
  updateApiUrl: (url: string) => void;

  // Theme
  theme: "dark" | "light";
  toggleTheme: () => void;

  // Raw inspector modal helper
  inspectPayload: { title: string; data: any } | null;
  setInspectPayload: (payload: { title: string; data: any } | null) => void;
}

const MissionContext = createContext<MissionContextType | undefined>(undefined);

const DEFAULT_INITIAL_MISSION: Mission = {
  id: 1,
  mission_name: "ARES-V DEEP RECON",
  spacecraft_name: "ORION-X4",
  status: "ACTIVE",
  created_at: new Date().toISOString(),
};

export const MissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePage, setActivePage] = useState<PageId>("overview");
  
  // Theme state
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("conflux_theme");
      if (saved === "light" || saved === "dark") return saved;
    }
    return "dark";
  });

  // Missions state
  const [missions, setMissions] = useState<Mission[]>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("conflux_missions");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed) && parsed.length > 0) return parsed;
        } catch {
          // ignore
        }
      }
    }
    return [DEFAULT_INITIAL_MISSION];
  });

  const [activeMission, setActiveMission] = useState<Mission | null>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("conflux_active_mission");
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          // ignore
        }
      }
    }
    return missions[0] || DEFAULT_INITIAL_MISSION;
  });

  // Modality state
  const [modalityState, setModalityState] = useState<ModalityStateSnapshot>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("conflux_modality_state");
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch {
          // ignore
        }
      }
    }
    return {
      telemetryAnomaly: false,
      thermalAnomaly: false,
      wavefrontAnomaly: false,
      orbitalStatus: "NOMINAL",
      spaceWeatherAnomaly: false,
    };
  });

  // System status
  const [systemOnline, setSystemOnline] = useState<boolean>(false);
  const [healthStatus, setHealthStatus] = useState<"healthy" | "unhealthy" | "checking" | "offline">("checking");
  const [systemName, setSystemName] = useState<string>("CONFLUX");
  const [isCheckingHealth, setIsCheckingHealth] = useState<boolean>(false);
  const [apiUrl, setApiUrlState] = useState<string>(getApiBaseUrl());

  // Raw inspector modal
  const [inspectPayload, setInspectPayload] = useState<{ title: string; data: any } | null>(null);

  // Sync theme
  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    if (theme === "dark") {
      root.classList.add("dark");
      root.classList.remove("light");
      body.classList.add("dark");
      body.classList.remove("light");
      root.setAttribute("data-theme", "dark");
    } else {
      root.classList.add("light");
      root.classList.remove("dark");
      body.classList.add("light");
      body.classList.remove("dark");
      root.setAttribute("data-theme", "light");
    }
    localStorage.setItem("conflux_theme", theme);
  }, [theme]);

  // Sync missions to local storage
  useEffect(() => {
    localStorage.setItem("conflux_missions", JSON.stringify(missions));
  }, [missions]);

  // Sync active mission — and clear all modality state on mission switch
  useEffect(() => {
    if (activeMission) {
      localStorage.setItem("conflux_active_mission", JSON.stringify(activeMission));
    }
    // Reset all per-modality analysis results so stale data from the previous
    // mission never bleeds into the newly-selected mission's view.
    setModalityState({
      telemetryAnomaly: false,
      thermalAnomaly: false,
      wavefrontAnomaly: false,
      orbitalStatus: "NOMINAL",
      spaceWeatherAnomaly: false,
    });
  }, [activeMission?.id]); // only re-run when the mission ID itself changes

  // Sync modality state
  useEffect(() => {
    localStorage.setItem("conflux_modality_state", JSON.stringify(modalityState));
  }, [modalityState]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const updateApiUrl = (newUrl: string) => {
    setApiBaseUrl(newUrl);
    setApiUrlState(newUrl);
    checkConnection();
  };

  const addMission = (newMission: Mission) => {
    setMissions((prev) => {
      const exists = prev.some((m) => m.id === newMission.id);
      if (exists) {
        return prev.map((m) => (m.id === newMission.id ? newMission : m));
      }
      return [newMission, ...prev];
    });
    setActiveMission(newMission);
  };

  const refreshMissions = useCallback(async () => {
    try {
      const backendMissions = await getMissions();
      if (Array.isArray(backendMissions) && backendMissions.length > 0) {
        setMissions(backendMissions);
        setActiveMission((current) => {
          if (!current) return backendMissions[0];
          const found = backendMissions.find((m) => m.id === current.id);
          return found || backendMissions[0];
        });
      }
    } catch {
      // Backend may be offline
    }
  }, []);

  // Check connection against live backend
  const checkConnection = useCallback(async () => {
    setIsCheckingHealth(true);
    setHealthStatus("checking");
    try {
      const [sysRes, healthRes] = await Promise.all([
        getSystemStatus().catch(() => null),
        getHealth().catch(() => null),
      ]);

      if (sysRes) {
        setSystemOnline(sysRes.status?.toLowerCase() === "online" || true);
        if (sysRes.system) setSystemName(sysRes.system);
      } else {
        setSystemOnline(false);
      }

      if (healthRes && (healthRes.status?.toLowerCase() === "healthy" || healthRes.status === "ok")) {
        setHealthStatus("healthy");
      } else if (sysRes) {
        setHealthStatus("healthy");
      } else {
        setHealthStatus("offline");
      }

      // Fetch live missions from database
      await refreshMissions();
    } catch {
      setSystemOnline(false);
      setHealthStatus("offline");
    } finally {
      setIsCheckingHealth(false);
    }
  }, [refreshMissions]);

  // Check on mount and periodically
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 15000);
    return () => clearInterval(interval);
  }, [checkConnection]);


  // Handlers for modality result updates
  const updateTelemetryResult = useCallback((res: TelemetryResponse) => {
    setModalityState((prev) => ({
      ...prev,
      telemetryAnomaly: res.anomaly_detected,
      lastTelemetryResponse: res,
    }));
  }, []);

  const updateImageryResult = useCallback((res: ImageryResponse) => {
    setModalityState((prev) => ({
      ...prev,
      thermalAnomaly: res.anomaly_detected,
      lastImageryResponse: res,
    }));
  }, []);

  const updateWavefrontResult = useCallback((res: WavefrontResponse) => {
    setModalityState((prev) => ({
      ...prev,
      wavefrontAnomaly: res.anomaly_detected,
      lastWavefrontResponse: res,
    }));
  }, []);

  const updateOrbitalResult = useCallback((res: OrbitalResponse) => {
    setModalityState((prev) => ({
      ...prev,
      orbitalStatus: res.status || (res.collision_risk ? "CRITICAL" : "NOMINAL"),
      lastOrbitalResponse: res,
    }));
  }, []);

  const updateWeatherResult = useCallback((res: SpaceWeatherResponse) => {
    setModalityState((prev) => ({
      ...prev,
      spaceWeatherAnomaly: res.environmental_anomaly,
      lastWeatherResponse: res,
    }));
  }, []);

  const updateFusionResult = useCallback((res: FusionResponse) => {
    setModalityState((prev) => ({
      ...prev,
      lastFusionResponse: res,
    }));
  }, []);

  return (
    <MissionContext.Provider
      value={{
        activePage,
        setActivePage,
        activeMission,
        setActiveMission,
        missions,
        addMission,
        modalityState,
        updateTelemetryResult,
        updateImageryResult,
        updateWavefrontResult,
        updateOrbitalResult,
        updateWeatherResult,
        updateFusionResult,
        systemOnline,
        healthStatus,
        systemName,
        isCheckingHealth,
        checkConnection,
        apiUrl,
        updateApiUrl,
        theme,
        toggleTheme,
        inspectPayload,
        setInspectPayload,
      }}
    >
      {children}
    </MissionContext.Provider>
  );
};

export const useMission = () => {
  const context = useContext(MissionContext);
  if (!context) {
    throw new Error("useMission must be used within a MissionProvider");
  }
  return context;
};
