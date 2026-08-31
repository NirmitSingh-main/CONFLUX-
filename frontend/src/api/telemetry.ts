import { requestJson } from "./client";
import { TelemetryRequest, TelemetryResponse } from "../types";

/** POST /telemetry/ — run Isolation Forest inference and persist to DB */
export async function analyzeTelemetry(data: TelemetryRequest): Promise<TelemetryResponse> {
  return requestJson<TelemetryResponse>("/telemetry/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** GET /telemetry/latest/{missionId} — fetch most-recent persisted result for this mission */
export async function getLatestTelemetry(missionId: number): Promise<TelemetryResponse> {
  return requestJson<TelemetryResponse>(`/telemetry/latest/${missionId}`);
}
