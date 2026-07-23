import type { GauntletReport } from "../types";

export function HeaderBar({
  health,
  loading,
  onRefresh,
  onRunPipeline,
  pipelineRunning,
}: {
  health: GauntletReport | null;
  loading: boolean;
  onRefresh: () => void;
  onRunPipeline: () => Promise<void>;
  pipelineRunning: boolean;
}) {
  const isSecure = health?.gauntlet_status === "ZODIAKO_GARDAS";
  const verdict = isSecure ? "PURA" : health ? "MALPURA" : "---";
  const verdictColor = isSecure ? "text-emerald-400" : "text-red-400";
  const verdictBg = isSecure ? "bg-emerald-500/10" : "bg-red-500/10";
  const verdictBorder = isSecure ? "border-emerald-500/30" : "border-red-500/30";

  return (
    <div className="glass-card rounded-xl p-5 mb-6">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`px-4 py-2 rounded-lg ${verdictBg} ${verdictBorder} border`}>
            <div className="text-xs text-gray-500 uppercase tracking-wider">Final Status</div>
            <div className={`text-2xl font-bold font-mono ${verdictColor}`}>
              {verdict}
            </div>
          </div>
          <div className="space-y-1">
            <h1 className="text-lg font-semibold text-gray-100">
              Z-12 Sovereign Security Platform
            </h1>
            <div className="flex gap-4 text-xs text-gray-500">
              <span>
                EVK Core:{" "}
                <span className={health?.audit_results?.evk_core === "VERIFIED" ? "text-emerald-400" : "text-red-400"}>
                  {health?.audit_results?.evk_core || "---"}
                </span>
              </span>
              <span>
                Health:{" "}
                <span className="text-gray-300">
                  {health?.rooms_healthy ?? 0}/{health?.total_rooms ?? 0}
                </span>
              </span>
              <span>
                Risk:{" "}
                <span className={health && health.cop_score > 0 ? "text-amber-400" : "text-emerald-400"}>
                  {health ? `${health.cop_score.toFixed(1)}%` : "---"}
                </span>
              </span>
              <span>
                Score:{" "}
                <span className="text-gray-300">
                  {health ? `${health.health_score.toFixed(1)}%` : "---"}
                </span>
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {loading && (
            <span className="text-xs text-gray-500 animate-pulse">Loading...</span>
          )}
          <button
            onClick={onRefresh}
            className="px-3 py-1.5 bg-z12-surface border border-z12-border hover:border-gray-600 text-gray-300 text-sm rounded-lg transition-colors"
          >
            Refresh
          </button>
          <button
            onClick={onRunPipeline}
            disabled={pipelineRunning}
            className="px-4 py-1.5 bg-z12-primary hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {pipelineRunning ? "Running..." : "Run Pipeline"}
          </button>
        </div>
      </div>

      {health?.timestamp && (
        <div className="mt-3 text-xs text-gray-600 font-mono">
          Last gauntlet: {new Date(health.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
}
