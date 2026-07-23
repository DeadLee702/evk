import type { ComponentStatus } from "../types";

const statusConfig: Record<string, { color: string; bg: string; dot: string }> = {
  OPERATIONAL: { color: "text-emerald-400", bg: "bg-emerald-500/10", dot: "bg-emerald-500" },
  DEGRADED: { color: "text-amber-400", bg: "bg-amber-500/10", dot: "bg-amber-500" },
  OFFLINE: { color: "text-red-400", bg: "bg-red-500/10", dot: "bg-red-500" },
};

export function ComponentPanel({ components }: { components: ComponentStatus[] }) {
  return (
    <div className="glass-card rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Platform Components
        </h2>
        <span className="text-xs text-gray-500">{components.length} registered</span>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {components.map((comp) => {
          const cfg = statusConfig[comp.status] || statusConfig.OFFLINE;
          return (
            <div
              key={comp.name}
              className={`${cfg.bg} rounded-lg p-3 border border-z12-border hover:border-gray-600 transition-colors`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className={`w-2 h-2 rounded-full ${cfg.dot} ${comp.status === "OFFLINE" ? "" : "animate-pulse"}`} />
                <span className="text-sm font-medium text-gray-200">{comp.name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${cfg.color}`}>{comp.status}</span>
                <span className="text-xs text-gray-500 font-mono">v{comp.version}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
