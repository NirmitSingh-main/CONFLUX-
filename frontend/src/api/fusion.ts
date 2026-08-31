import { requestJson } from "./client";
import { FusionRequest, FusionResponse } from "../types";

/** POST /fusion/ — run multimodal fusion against persisted DB analyses and persist result */
export async function analyzeFusion(data: FusionRequest): Promise<FusionResponse> {
  return requestJson<FusionResponse>("/fusion/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** GET /fusion/latest/{missionId} — fetch most-recent persisted fusion result for this mission */
export async function getLatestFusion(missionId: number): Promise<FusionResponse> {
  return requestJson<FusionResponse>(`/fusion/latest/${missionId}`);
}
