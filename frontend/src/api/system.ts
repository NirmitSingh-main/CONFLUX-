import { requestJson } from "./client";
import { SystemStatusResponse, HealthResponse } from "../types";

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  return requestJson<SystemStatusResponse>("/");
}

export async function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}
