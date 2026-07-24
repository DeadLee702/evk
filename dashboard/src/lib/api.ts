import type {
  GauntletReport,
  ScanRecord,
  ComponentStatus,
  AuditEvent,
  VersionInfo,
  ScanResult,
  EnforcementAction,
  EnforcementPendingResponse,
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
  enforcementPending: () =>
    fetchJson<EnforcementPendingResponse>("/api/enforcement/pending"),
  enforcementApprove: (id: string) =>
    fetchJson<EnforcementAction>(`/api/enforcement/${id}/approve`, {
      method: "POST",
    }),
  enforcementDeny: (id: string) =>
    fetchJson<EnforcementAction>(`/api/enforcement/${id}/deny`, {
      method: "POST",
    }),
  enforcementHold: (id: string) =>
    fetchJson<EnforcementAction>(`/api/enforcement/${id}/hold`, {
      method: "POST",
    }),
  enforcementDecide: (id: string, decision: "approve" | "deny" | "hold") => {
    if (decision === "approve") return api.enforcementApprove(id);
    if (decision === "deny") return api.enforcementDeny(id);
    return api.enforcementHold(id);
  },
};
