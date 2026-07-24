import { useState } from "react";
import { useDashboardData } from "./hooks/useDashboardData";
import { HeaderBar } from "./components/HeaderBar";
import { ComponentPanel } from "./components/ComponentPanel";
import { RoomGrid } from "./components/RoomGrid";
import { ScanPanel } from "./components/ScanPanel";
import { AuditLog } from "./components/AuditLog";
import { PendingEnforcement } from "./components/PendingEnforcement";
import { Footer } from "./components/Footer";

export function App() {
  const {
    health,
    components,
    scans,
    audit,
    version,
    enforcement,
    loading,
    error,
    lastUpdate,
    refresh,
    runPipeline,
    scanArtifact,
  } = useDashboardData(30000);

  const [pipelineRunning, setPipelineRunning] = useState(false);

  const handleRunPipeline = async () => {
    setPipelineRunning(true);
    try {
      await runPipeline();
    } finally {
      setPipelineRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-z12-bg text-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <HeaderBar
          health={health}
          loading={loading}
          onRefresh={refresh}
          onRunPipeline={handleRunPipeline}
          pipelineRunning={pipelineRunning}
        />

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
            {error}
          </div>
        )}

        <div className="mb-6">
          <ComponentPanel components={components} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <RoomGrid reports={health?.reports || []} />
          </div>
          <div className="space-y-6">
            <ScanPanel scans={scans} onScan={scanArtifact} />
          </div>
        </div>

        <div className="mb-6">
          <PendingEnforcement
            actions={enforcement}
            onDecided={refresh}
          />
        </div>

        <div className="mb-6">
          <AuditLog events={audit} />
        </div>

        <Footer version={version} />

        {lastUpdate && (
          <div className="mt-4 text-center text-xs text-gray-600">
            Last updated: {lastUpdate.toLocaleTimeString()} | Auto-refresh: 30s
          </div>
        )}
      </div>
    </div>
  );
}
