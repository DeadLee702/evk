import type { RoomReport } from "../types";
import { ZODIAC_ICONS } from "../types";

const statusConfig: Record<string, { color: string; border: string; bg: string; label: string }> = {
  PURA: { color: "text-emerald-400", border: "border-emerald-500/30", bg: "bg-emerald-500/5", label: "HEALTHY" },
  VIGLA: { color: "text-amber-400", border: "border-amber-500/30", bg: "bg-amber-500/5", label: "WARNING" },
  POLUITA: { color: "text-red-400", border: "border-red-500/30", bg: "bg-red-500/5", label: "COMPROMISED" },
};

export function RoomGrid({ reports }: { reports: RoomReport[] }) {
  return (
    <div className="glass-card rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Gauntlet Swarm — 12 Rooms
        </h2>
        <div className="flex gap-3 text-xs">
          <span className="text-emerald-400">
            {reports.filter((r) => r.status === "PURA").length} Healthy
          </span>
          <span className="text-amber-400">
            {reports.filter((r) => r.status === "VIGLA").length} Warning
          </span>
          <span className="text-red-400">
            {reports.filter((r) => r.status === "POLUITA").length} Compromised
          </span>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {reports.map((room) => {
          const cfg = statusConfig[room.status] || statusConfig.PURA;
          return (
            <div
              key={room.id}
              className={`${cfg.bg} ${cfg.border} rounded-lg p-4 border transition-all hover:scale-[1.02] cursor-default ${
                room.status === "POLUITA" ? "danger-pulse" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{ZODIAC_ICONS[room.zodiac] || "\u2753"}</span>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-200">{room.room}</h3>
                    <span className="text-xs text-gray-500">{room.zodiac}</span>
                  </div>
                </div>
                <span className={`text-xs font-mono font-bold ${cfg.color}`}>{cfg.label}</span>
              </div>
              <p className="text-xs text-gray-400 mb-3 line-clamp-2">{room.attack_vector}</p>
              <div className="flex gap-2 text-xs">
                <span className={`px-2 py-0.5 rounded ${room.benign_pass ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                  {room.benign_pass ? "\u2713 Benign" : "\u2717 Benign"}
                </span>
                <span className={`px-2 py-0.5 rounded ${room.malicious_blocked ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                  {room.malicious_blocked ? "\u2713 Blocked" : "\u2717 Blocked"}
                </span>
              </div>
              <p className="text-[10px] text-gray-600 mt-2 font-mono truncate" title={room.signature}>
                {room.signature}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
