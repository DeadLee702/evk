#pragma once

#include <sys/types.h>

/*
 * Z-12 Kill Vector — runtime enforcement API.
 *
 * The Kill Vector is the platform's enforcement layer: when the Adversarial
 * Compliance Matrix (ACM) denies a runtime lineage (verdict POLUITA), the Kill
 * Vector terminates the offending process and records a forensic log entry.
 *
 * Safety contract:
 *   - Refuses to act on unsafe PIDs (pid <= 1) so init / kernel-adjacent
 *     processes can never be targeted.
 *   - Every enforcement decision (allowed or refused) is logged with a
 *     timestamp, the PID, the reason, and the action taken.
 *   - Enforcement is policy-driven: the caller supplies both the PID and the
 *     reason; the Kill Vector never discovers targets on its own.
 */

/* Initialize the enforcement log. Returns 0 on success, -1 on failure. */
int kill_vector_log_init(void);

/*
 * Enforce a containment action against `pid` for `reason`.
 *
 * Returns:
 *    0  enforcement succeeded (process signalled)
 *   -1  refused (unsafe PID) or the kill(2) syscall failed
 */
int kill_vector_enforce(pid_t pid, const char *reason);
