import type {
  GauntletReport,
  ScanRecord,
  ComponentStatus,
  AuditEvent,
  VersionInfo,
  ScanResult,
} from "../types";

const BASE = "";

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${url}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!resp.ok) {
    const text = await resp.text().catch(() => resp.statusText);
    throw new Error(`${resp.status}: ${text}`);
  }
  return resp.json();
}

export const api = {
  health: () => fetchJson<GauntletReport>("/api/health"),
  swarm: () => fetchJson<{ swarm: unknown[] }>("/api/swarm"),
  version: () => fetchJson<VersionInfo>("/api/version"),
  reports: () => fetchJson<{ reports: unknown[] }>("/api/reports"),
  components: () => fetchJson<{ components: ComponentStatus[] }>("/api/components"),
  scans: () => fetchJson<{ scans: ScanRecord[] }>("/api/scans"),
  audit: () => fetchJson<{ events: AuditEvent[] }>("/api/audit"),
  gauntletHistory: () => fetchJson<{ runs: unknown[] }>("/api/gauntlet/history"),
  scan: (artifactPath: string) =>
    fetchJson<ScanResult>("/api/scan", {
      method: "POST",
      body: JSON.stringify({ artifact_path: artifactPath }),
    }),
  runPipeline: () =>
    fetchJson<GauntletReport>("/api/pipeline/run", { method: "POST" }),
};
