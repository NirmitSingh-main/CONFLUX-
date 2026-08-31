import { requestJson } from "./client";
import { SpaceWeatherRequest, SpaceWeatherResponse } from "../types";

/** POST /space-weather/ — run space weather analysis and persist to DB */
export async function analyzeSpaceWeather(data: SpaceWeatherRequest): Promise<SpaceWeatherResponse> {
  return requestJson<SpaceWeatherResponse>("/space-weather/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/** GET /space-weather/latest/{missionId} — fetch most-recent persisted space weather result for this mission */
export async function getLatestSpaceWeather(missionId: number): Promise<SpaceWeatherResponse> {
  return requestJson<SpaceWeatherResponse>(`/space-weather/latest/${missionId}`);
}
