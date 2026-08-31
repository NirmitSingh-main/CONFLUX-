import { requestJson } from "./client";
import { FusionResponse, RagResponse } from "../types";

export async function retrieveMissionGuidance(
  missionId: number,
  fusionResult: FusionResponse,
): Promise<RagResponse> {
  return requestJson<RagResponse>("/rag/", {
    method: "POST",
    body: JSON.stringify({ mission_id: missionId, fusion_result: fusionResult }),
  });
}
