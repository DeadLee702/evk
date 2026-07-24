import { useState } from "react";
import type { EnforcementAction } from "../types";
import { api } from "../lib/api";

interface Props {
  actions: EnforcementAction[];
  onDecided: () => void;
}

export function PendingEnforcement({ actions, onDecided }: Props) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const handleDecide = async (
    actionId: string,
    decision: "approve" | "deny" | "hold",
  ) => {
    setBusy(`${actionId}:${decision}`);
    setError(null);
    setConfirmId(null);
    try {
      await api.enforcementDecide(actionId, decision);
      onDecided();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${decision} action`);
    } finally {
      setBusy(null);
    }
  };

  const pending = actions.filter((a) => a.status === "PENDING");

  if (pending.length === 0) {
    return (
      <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-4">
        <h3 className="text-sm font-semibold text-gray-300 mb-1">
          Enforcement Queue
        </h3>
        <p className="text-xs text-gray-500">No pending enforcement actions.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-amber-400">
          Pending Enforcement — Human Approval Required
        </h3>
        <span className="text-xs text-amber-500/70 bg-amber-500/10 px-2 py-0.5 rounded-full">
          {pending.length} pending
        </span>
      </div>

      {error && (
        <div className="mb-2 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
          {error}
        </div>
      )}

      <div className="space-y-2">
        {pending.map((action) => (
          <div
            key={action.id}
            className="flex items-center justify-between gap-3 p-3 bg-gray-900/60 rounded-lg border border-gray-800"
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-mono text-red-400 font-semibold">
                  PID {action.pid}
                </span>
                <span className="text-gray-500">·</span>
                <span className="text-gray-300 truncate">{action.reason}</span>
              </div>
              {action.lineage && (
                <div className="text-xs text-gray-600 mt-0.5 font-mono truncate">
                  {action.lineage}
                </div>
              )}
              <div className="text-xs text-gray-600 mt-0.5">
                {new Date(action.created_at).toLocaleString()}
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {confirmId === action.id ? (
                <>
                  <span className="text-xs text-red-400 font-medium">Confirm kill?</span>
                  <button
                    disabled={busy !== null}
                    onClick={() => handleDecide(action.id, "approve")}
                    className="px-3 py-1.5 text-xs font-medium rounded-md bg-red-600 hover:bg-red-500 text-white transition-colors disabled:opacity-50"
                  >
                    {busy === `${action.id}:approve` ? "..." : "Yes, Kill"}
                  </button>
                  <button
                    disabled={busy !== null}
                    onClick={() => setConfirmId(null)}
                    className="px-3 py-1.5 text-xs font-medium rounded-md bg-gray-700 hover:bg-gray-600 text-gray-200 transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <button
                    disabled={busy !== null}
                    onClick={() => setConfirmId(action.id)}
                    className="px-3 py-1.5 text-xs font-medium rounded-md bg-red-600 hover:bg-red-500 text-white transition-colors disabled:opacity-50"
                  >
                    {busy === `${action.id}:approve` ? "..." : "Approve Kill"}
                  </button>
                  <button
                    disabled={busy !== null}
                    onClick={() => handleDecide(action.id, "deny")}
                    className="px-3 py-1.5 text-xs font-medium rounded-md bg-gray-700 hover:bg-gray-600 text-gray-200 transition-colors disabled:opacity-50"
                  >
                    {busy === `${action.id}:deny` ? "..." : "Deny"}
                  </button>
                  <button
                    disabled={busy !== null}
                    onClick={() => handleDecide(action.id, "hold")}
                    className="px-3 py-1.5 text-xs font-medium rounded-md bg-amber-600/80 hover:bg-amber-500 text-white transition-colors disabled:opacity-50"
                  >
                    {busy === `${action.id}:hold` ? "..." : "Hold"}
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-3 text-xs text-gray-600">
        No action is taken until a human explicitly approves. Held actions stay
        in the queue indefinitely (Adaptive Hold).
      </p>
    </div>
  );
}
