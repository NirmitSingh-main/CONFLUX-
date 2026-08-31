import { requestJson } from "./client";
import { CreateMissionRequest, Mission } from "../types";

export async function createMission(data: CreateMissionRequest): Promise<Mission> {
  return requestJson<Mission>("/missions/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getMissions(): Promise<Mission[]> {
  return requestJson<Mission[]>("/missions/");
}

export async function getMissionById(missionId: number): Promise<Mission> {
  return requestJson<Mission>(`/missions/${missionId}`);
}

export async function getMissionObservations(missionId: number): Promise<any[]> {
  return requestJson<any[]>(`/missions/${missionId}/observations`);
}

export async function getMissionAnomalies(missionId: number): Promise<any[]> {
  return requestJson<any[]>(`/missions/${missionId}/anomalies`);
}

