// ==========================================
// Centralized API Client for CONFLUX
// ==========================================

export const DEFAULT_API_BASE_URL =
  ((import.meta as any).env?.VITE_API_BASE_URL as string) || "http://127.0.0.1:8000";

let currentBaseUrl = DEFAULT_API_BASE_URL;

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("conflux_api_url");
    if (saved) return saved;
  }
  return currentBaseUrl;
}

export function setApiBaseUrl(url: string) {
  currentBaseUrl = url.replace(/\/+$/, "");
  if (typeof window !== "undefined") {
    localStorage.setItem("conflux_api_url", currentBaseUrl);
  }
}

export class ApiError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function requestJson<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = getApiBaseUrl().replace(/\/+$/, "");
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err: any) {
    throw new ApiError(
      `Network connection error reaching ${url}. Is FastAPI running at ${baseUrl}? Details: ${err.message || "Failed to fetch"}`,
      0,
      { url, originalError: err }
    );
  }

  let parsedData: any = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      parsedData = await response.json();
    } catch {
      parsedData = null;
    }
  } else {
    try {
      const text = await response.text();
      try {
        parsedData = JSON.parse(text);
      } catch {
        parsedData = text;
      }
    } catch {
      parsedData = null;
    }
  }

  if (!response.ok) {
    const errorMsg =
      (typeof parsedData === "object" && parsedData !== null
        ? parsedData.detail || parsedData.message || parsedData.error
        : null) || `Request failed with status ${response.status} (${response.statusText})`;

    throw new ApiError(errorMsg, response.status, parsedData);
  }

  return parsedData as T;
}
