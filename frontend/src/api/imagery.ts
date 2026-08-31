import { requestJson } from "./client";
import { ImageryResponse } from "../types";

/**
 * POST /thermal/ (multipart/form-data)
 * IMPORTANT: Do NOT set Content-Type manually — the browser must set it with
 * the multipart boundary. requestJson() already handles this correctly for FormData.
 */
export async function analyzeImagery(missionId: number, file: File): Promise<ImageryResponse> {
  const formData = new FormData();
  formData.append("mission_id", String(missionId));
  formData.append("file", file);
  return requestJson<ImageryResponse>("/thermal/", {
    method: "POST",
    body: formData,
  });
}

/** GET /thermal/latest/{missionId} — fetch most-recent persisted thermal result for this mission */
export async function getLatestImagery(missionId: number): Promise<ImageryResponse> {
  return requestJson<ImageryResponse>(`/thermal/latest/${missionId}`);
}
