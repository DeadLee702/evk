import { useState, useEffect, useCallback, useRef } from "react";
import { api } from "../lib/api";
import type {
  GauntletReport,
  ComponentStatus,
  ScanRecord,
  AuditEvent,
  VersionInfo,
  EnforcementAction,
} from "../types";

interface DashboardData {
  health: GauntletReport | null;
  components: ComponentStatus[];
  scans: ScanRecord[];
  audit: AuditEvent[];
  version: VersionInfo | null;
  enforcement: EnforcementAction[];
  loading: boolean;
  error: string | null;
  lastUpdate: Date | null;
}

export function useDashboardData(refreshMs: number = 30000) {
  const [data, setData] = useState<DashboardData>({
    health: null,
    components: [],
    scans: [],
    audit: [],
    version: null,
    enforcement: [],
    loading: true,
    error: null,
    lastUpdate: null,
  });
  const mountedRef = useRef(true);

  const fetchAll = useCallback(async () => {
    try {
      const [health, components, scans, audit, version, enforcement] = await Promise.all([
        api.health().catch(() => null),
        api.components().catch(() => ({ components: [] })),
        api.scans().catch(() => ({ scans: [] })),
        api.audit().catch(() => ({ events: [] })),
        api.version().catch(() => null),
        api.enforcementPending().catch(() => ({ requests: [] })),
      ]);

      if (!mountedRef.current) return;

      setData({
        health,
        components: (components as { components: ComponentStatus[] }).components || [],
        scans: (scans as { scans: ScanRecord[] }).scans || [],
        audit: (audit as { events: AuditEvent[] }).events || [],
        version,
        enforcement: (enforcement as { requests: EnforcementAction[] }).requests || [],
        loading: false,
        error: null,
        lastUpdate: new Date(),
      });
    } catch (err) {
      if (!mountedRef.current) return;
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch data",
        lastUpdate: new Date(),
      }));
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    fetchAll();
    const interval = setInterval(fetchAll, refreshMs);
    return () => {
      mountedRef.current = false;
      clearInterval(interval);
    };
  }, [fetchAll, refreshMs]);

  const runPipeline = useCallback(async () => {
    try {
      await api.runPipeline();
      await fetchAll();
    } catch (err) {
      setData((prev) => ({
        ...prev,
        error: err instanceof Error ? err.message : "Pipeline run failed",
      }));
    }
  }, [fetchAll]);

  const scanArtifact = useCallback(
    async (path: string) => {
      try {
        await api.scan(path);
        await fetchAll();
      } catch (err) {
        setData((prev) => ({
          ...prev,
          error: err instanceof Error ? err.message : "Scan failed",
        }));
      }
    },
    [fetchAll],
  );

  return { ...data, refresh: fetchAll, runPipeline, scanArtifact };
}
