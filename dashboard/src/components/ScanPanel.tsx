import { useState } from "react";
import type { ScanRecord } from "../types";

const severityConfig: Record<string, string> = {
  LOW: "text-emerald-400 bg-emerald-500/10",
  MEDIUM: "text-amber-400 bg-amber-500/10",
  HIGH: "text-orange-400 bg-orange-500/10",
  CRITICAL: "text-red-400 bg-red-500/10",
};

const verdictConfig: Record<string, string> = {
  PURA: "text-emerald-400",
  VIGLA: "text-amber-400",
  POLUITA: "text-red-400",
};

export function ScanPanel({
  scans,
  onScan,
}: {
  scans: ScanRecord[];
  onScan: (path: string) => Promise<void>;
}) {
  const [artifactPath, setArtifactPath] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!artifactPath.trim()) return;
    setScanning(true);
    setError(null);
    try {
      await onScan(artifactPath.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="glass-card rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
        Artifact Scanner
      </h2>

      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={artifactPath}
          onChange={(e) => setArtifactPath(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleScan()}
          placeholder="test/incident_7f3a.evkp"
          className="flex-1 bg-z12-bg border border-z12-border rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-z12-primary focus:outline-none transition-colors"
        />
        <button
          onClick={handleScan}
          disabled={scanning || !artifactPath.trim()}
          className="px-4 py-2 bg-z12-primary hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {scanning ? "Scanning..." : "Scan"}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400 mb-3">{error}</p>
      )}

      <div className="text-xs text-gray-500 mb-3">
        {scans.length} scan{scans.length !== 1 ? "s" : ""} recorded
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {scans.length === 0 ? (
          <p className="text-xs text-gray-600 text-center py-4">No scans yet. Run one above.</p>
        ) : (
          scans.map((scan) => (
            <div
              key={scan.id}
              className="bg-z12-bg/50 border border-z12-border rounded-lg p-3 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-mono text-gray-300 truncate">{scan.artifact_name}</span>
                <span className={`text-xs font-bold ${verdictConfig[scan.verdict] || "text-gray-400"}`}>
                  {scan.verdict}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="font-mono text-gray-500">{scan.status_code}</span>
                <span className="text-gray-500">{scan.incident_type}</span>
                <span className={`px-1.5 py-0.5 rounded font-mono ${severityConfig[scan.severity] || "text-gray-400 bg-gray-500/10"}`}>
                  {scan.severity}
                </span>
                <span className="text-gray-600 ml-auto">
                  {new Date(scan.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
