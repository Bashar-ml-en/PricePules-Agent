import type { SystemBlueprint } from "./types";

const configuredApiBaseUrl = import.meta.env.VITE_API_URL?.replace(/\/+$/, "");
const apiBaseUrl = configuredApiBaseUrl ?? (import.meta.env.DEV ? "http://localhost:8000" : undefined);

export const hasBlueprintApi = Boolean(apiBaseUrl);

export async function fetchSystemBlueprint(): Promise<SystemBlueprint> {
  if (!apiBaseUrl) {
    throw new Error("No system blueprint API is configured for this deployment");
  }

  const response = await fetch(`${apiBaseUrl}/system/blueprint`);
  if (!response.ok) {
    throw new Error(`Blueprint API returned ${response.status}`);
  }
  return response.json() as Promise<SystemBlueprint>;
}
