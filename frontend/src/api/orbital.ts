import { requestJson } from "./client";
import { OrbitalRequest, OrbitalResponse } from "../types";

/** POST /orbital/ — run conjunction analysis and persist to DB */
export async function analyzeOrbital(data: OrbitalRequest): Promise<OrbitalResponse> {
  return requestJson<OrbitalResponse>("/orbital/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** GET /orbital/latest/{missionId} — fetch most-recent persisted orbital result for this mission */
export async function getLatestOrbital(missionId: number): Promise<OrbitalResponse> {
  return requestJson<OrbitalResponse>(`/orbital/latest/${missionId}`);
}
