import { requestJson } from "./client";
import { WavefrontRequest, WavefrontResponse } from "../types";

/** POST /wavefront/ — run wavefront aberration analysis and persist to DB */
export async function analyzeWavefront(data: WavefrontRequest): Promise<WavefrontResponse> {
  return requestJson<WavefrontResponse>("/wavefront/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** GET /wavefront/latest/{missionId} — fetch most-recent persisted wavefront result for this mission */
export async function getLatestWavefront(missionId: number): Promise<WavefrontResponse> {
  return requestJson<WavefrontResponse>(`/wavefront/latest/${missionId}`);
}
