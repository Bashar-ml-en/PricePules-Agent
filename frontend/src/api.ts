import type { AnalysisPayload, CatalogueItem } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed with status ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export async function getItems(): Promise<CatalogueItem[]> {
  const response = await request<{ items: CatalogueItem[] }>("/catalogue/items");
  return response.items;
}

export async function getLocations(
  geographyType: "state" | "district",
): Promise<string[]> {
  const response = await request<{ values: string[] }>(
    `/catalogue/locations?geography_type=${geographyType}`,
  );
  return response.values;
}

export function runAnalysis(payload: AnalysisPayload["scope"]): Promise<AnalysisPayload> {
  return request<AnalysisPayload>("/analysis/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
