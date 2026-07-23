import type { AuditEvent } from "../types";

const severityColors: Record<string, string> = {
  LOW: "text-emerald-400",
  MEDIUM: "text-amber-400",
  HIGH: "text-orange-400",
  CRITICAL: "text-red-400",
};

const componentColors: Record<string, string> = {
  EVK: "text-blue-400",
  "GEMINI-BOX": "text-cyan-400",
  ACM: "text-purple-400",
  "KILL-VECTOR": "text-red-400",
  DASHBOARD: "text-gray-400",
};

export function AuditLog({ events }: { events: AuditEvent[] }) {
  return (
    <div className="glass-card rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
        Audit Trail
      </h2>
      <div className="space-y-1.5 max-h-64 overflow-y-auto">
        {events.length === 0 ? (
          <p className="text-xs text-gray-600 text-center py-4">No audit events recorded.</p>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-3 py-2 px-3 rounded-lg hover:bg-z12-bg/50 transition-colors border border-transparent hover:border-z12-border"
            >
              <span className={`text-xs font-mono ${severityColors[event.severity] || "text-gray-400"} mt-0.5`}>
                {event.severity}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono font-medium ${componentColors[event.component] || "text-gray-400"}`}>
                    {event.component}
                  </span>
                  <span className="text-xs text-gray-500">{event.action}</span>
                </div>
                <p className="text-xs text-gray-400 truncate">{event.message}</p>
              </div>
              <span className="text-xs text-gray-600 font-mono whitespace-nowrap">
                {new Date(event.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
