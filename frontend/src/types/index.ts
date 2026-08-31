// ==========================================
// CONFLUX Types & Interfaces
// ==========================================

export interface SystemStatusResponse {
  system: string;
  status: string;
}

export interface HealthResponse {
  status: string;
}

// ------------------------------------------
// Missions
// ------------------------------------------
export interface CreateMissionRequest {
  mission_name: string;
  spacecraft_name: string;
  status: string;
}

export interface Mission {
  id: number;
  mission_name: string;
  spacecraft_name: string;
  status: string;
  created_at: string;
}

// ------------------------------------------
// Telemetry
// ------------------------------------------
export interface TelemetryRequest {
  mission_id: number;
  temperature: number;
  voltage: number;
  current: number;
  battery: number;
  pressure: number;
  vibration: number;
}

export interface TelemetryMeasurements {
  temperature?: number;
  voltage?: number;
  current?: number;
  battery?: number;
  pressure?: number;
  vibration?: number;
  [key: string]: number | undefined;
}

export interface TelemetryResponse {
  id?: number;
  mission_id: number;
  modality: string;
  measurements?: TelemetryMeasurements;
  anomaly_detected: boolean;
  model_output?: any;
  decision_value?: number;
  severity?: string;
  confidence?: number;
  status?: string;
  stored_in_database?: boolean;
  [key: string]: any;
}

// ------------------------------------------
// Imagery / Thermal
// ------------------------------------------
export type HottestLocation =
  | [number, number]
  | { x: number; y: number }
  | { row?: number; col?: number }
  | string
  | number[];

export interface ImageryResponse {
  id?: number;
  mission_id: number;
  modality: string;
  filename: string;
  anomaly_detected: boolean;
  mean_intensity: number;
  standard_deviation: number;
  threshold: number;
  hottest_intensity: number;
  hottest_location: HottestLocation;
  hotspot_pixels: number;
  hotspot_ratio: number;
  severity?: string;
  confidence?: number;
  status?: string;
  stored_in_database?: boolean;
  [key: string]: any;
}

// ------------------------------------------
// Wavefront
// ------------------------------------------
export interface WavefrontRequest {
  mission_id: number;
  wavefront_rms_um: number;
  tip_error_um: number;
  tilt_error_um: number;
  defocus_um: number;
  astigmatism_um: number;
  coma_um: number;
}

export interface WavefrontFeatureScores {
  wavefront_rms_um?: number;
  tip_error_um?: number;
  tilt_error_um?: number;
  defocus_um?: number;
  astigmatism_um?: number;
  coma_um?: number;
  [key: string]: number | undefined;
}

export interface WavefrontResponse {
  id?: number;
  mission_id: number;
  modality: string;
  anomaly_detected: boolean;
  anomaly_score: number;
  max_z_score: number;
  feature_scores?: WavefrontFeatureScores | Record<string, number>;
  wavelet_energy: number;
  baseline_energy: number;
  energy_ratio: number;
  wavelet_anomaly: boolean;
  wavelet: string;
  level: number;
  severity?: string;
  confidence?: number;
  status?: string;
  stored_in_database?: boolean;
  [key: string]: any;
}

// ------------------------------------------
// Orbital
// ------------------------------------------
export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

export interface OrbitalObject {
  object_id: string;
  timestamp: string;
  position: Vector3D;
  velocity: Vector3D;
}

export interface OrbitalRequest {
  mission_id: number;
  object1: OrbitalObject;
  object2: OrbitalObject;
  safety_distance: number;
}

export interface OrbitalResponse {
  id?: number;
  mission_id: number;
  object1_id: string;
  object2_id: string;
  current_distance: number;
  relative_speed: number;
  time_to_closest_approach: number;
  miss_distance: number;
  safety_threshold?: number;
  collision_risk: boolean;
  status: string; // e.g. "NOMINAL", "WARNING", "CRITICAL"
  event_type: string;
  risk_level: string;
  confidence?: number;
  stored_in_database?: boolean;
  [key: string]: any;
}

// ------------------------------------------
// Space Weather
// ------------------------------------------
export interface SpaceWeatherRequest {
  mission_id: number;
  solar_activity: number;
  radiation_level: number;
  geomagnetic_activity: number;
}

export interface SpaceWeatherResponse {
  id?: number;
  mission_id: number;
  modality: string;
  solar_activity: number;
  radiation_level: number;
  geomagnetic_activity: number;
  solar_event: boolean;
  radiation_event: boolean;
  geomagnetic_event: boolean;
  // active_events is the AUTHORITATIVE list — use this, not the boolean flags above, for display
  active_events: string[];
  environmental_anomaly: boolean;
  overall_status?: string;
  severity?: string;
  confidence?: number;
  stored_in_database?: boolean;
  [key: string]: any;
}

// ------------------------------------------
// Fusion
// ------------------------------------------

export interface ModalityDetail {
  analysis_id?: number;
  status: string;
  anomaly_detected?: boolean;
  severity?: string;
  confidence?: number;
  created_at?: string;
}

export interface ModalityState {
  status: string;
  anomaly_detected: boolean;
  severity?: string;
  confidence?: number;
}

export interface FusionRequest {
  mission_id: number;
  modalities?: string[]; // which modalities to include (backend loads from DB)
}

export interface FusionResponse {
  id?: number;
  mission_id: number;
  mission_name?: string;
  spacecraft_name?: string;

  // Modality classification
  available_modalities: string[];
  unavailable_modalities?: string[];
  anomalous_modalities: string[];
  normal_modalities: string[];
  anomaly_count: number;
  multi_modal_agreement: boolean;

  // Per-modality detail (from DB analyses)
  modality_details?: Record<string, ModalityDetail>;
  modality_states?: Record<string, ModalityState>;

  // Cross-modal analysis
  correlated_events?: string[];
  primary_problem?: string;

  // Overall assessment
  overall_severity?: string;
  risk_level?: string;
  confidence?: number;
  explanation?: string;
  recommended_action?: string;

  stored_in_database?: boolean;
  created_at?: string;
  [key: string]: any;
}

export interface RagEvidence {
  chunk_id: string;
  title: string;
  document_type: string;
  section?: string | null;
  page_number?: number | null;
  source: string;
  excerpt: string;
  relevance_score: number;
}

export interface RagResponse {
  mission_id: number;
  query: string;
  retrieval_status: string;
  evidence: RagEvidence[];
  sources: string[];
  source_entries?: Array<{ title: string; source: string; document_type: string }>;
  technical_interpretation: string;
  recommendations: string[];
}

// ------------------------------------------
// Application State & Navigation
// ------------------------------------------
export type PageId =
  | "overview"
  | "missions"
  | "telemetry"
  | "thermal"
  | "wavefront"
  | "orbital"
  | "weather"
  | "fusion";

export interface ModalityStateSnapshot {
  telemetryAnomaly?: boolean;
  thermalAnomaly?: boolean;
  wavefrontAnomaly?: boolean;
  orbitalStatus?: string;
  spaceWeatherAnomaly?: boolean;
  lastTelemetryResponse?: TelemetryResponse;
  lastImageryResponse?: ImageryResponse;
  lastWavefrontResponse?: WavefrontResponse;
  lastOrbitalResponse?: OrbitalResponse;
  lastWeatherResponse?: SpaceWeatherResponse;
  lastFusionResponse?: FusionResponse;
}
