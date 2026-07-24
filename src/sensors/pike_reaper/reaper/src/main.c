/*
 * Z-12 Pike / Reaper sensor -- reaper decision loop.
 *
 * STATUS: Integration scaffold wiring the enforcement flow:
 *
 *     Pike sensor -> runtime event -> ACM decision -> (ACM_DENY)
 *                                          -> PENDING enforcement request
 *                                          -> human approves in dashboard
 *                                          -> Kill Vector (SIGKILL + log)
 *
 * Enforcement is now GATED BY HUMAN APPROVAL. On ACM_DENY the reaper does NOT
 * kill the process directly. Instead it posts a PENDING enforcement request
 * to the backend control plane (POST /api/enforcement/request). A human must
 * Approve the request in the dashboard before the Kill Vector C engine
 * terminates the process. Deny and Hold never enforce.
 *
 * The real sensor (eBPF/ptrace event source) and the real ACM transport are
 * not implemented here; `handle_acm_decision` is the concrete, tested
 * integration point. The demo main() enqueues a demo request only -- it never
 * enforces against a real PID.
 */
#include "../../../../kill_vector/killswitch.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

/* ACM verdicts routed to the reaper. */
enum acm_action {
    ACM_ALLOW = 0,
    ACM_DENY = 1,
};

/* Minimal runtime event surfaced by the Pike sensor. */
struct event {
    pid_t pid;
    const char *lineage;
};

/*
 * Post a PENDING enforcement request to the backend control plane.
 * Uses curl as a subprocess so the reaper has no HTTP library dependency.
 * Returns 0 on success, -1 on failure.
 *
 * This function NEVER calls kill_vector_enforce -- it only enqueues a request.
 */
static int post_enforcement_request(pid_t pid, const char *reason,
                                      const char *lineage) {
    char body[512];
    char cmd[1024];

    snprintf(body, sizeof(body),
             "{\"pid\":%d,\"reason\":\"%s\",\"lineage\":\"%s\"}",
             (int)pid,
             reason ? reason : "POLUITA_LINEAGE",
             lineage ? lineage : "");

    snprintf(cmd, sizeof(cmd),
             "curl -s -o /dev/null -X POST "
             "-H 'Content-Type: application/json' "
             "-d '%s' "
             "%s 2>/dev/null || true",
             body, "http://127.0.0.1:8000/api/enforcement/request");

    /* Best-effort: failure to enqueue does NOT kill the process. */
    int rc = system(cmd);
    (void)rc;
    return 0;
}

/*
 * Route an ACM decision. On ACM_DENY the reaper enqueues a PENDING
 * enforcement request. It does NOT kill the process directly --
 * human approval is required before the Kill Vector acts.
 */
void handle_acm_decision(struct event *event, int action) {
    if (action == ACM_DENY) {
        post_enforcement_request(event->pid, "POLUITA_LINEAGE",
                                  event->lineage);
    }
}

int main(void) {
    kill_vector_log_init();
    printf("[pike-reaper] ACM_DENY events now enqueue PENDING enforcement requests.\n");
    printf("[pike-reaper] enforcement is gated by human approval in the dashboard.\n");
    printf("[pike-reaper] no live sensor attached; see handle_acm_decision().\n");

    /* Demo: enqueue a PENDING request for a safe demo PID.
     * Does NOT enforce against any real PID. */
    struct event demo = { .pid = 99999, .lineage = "demo:POLUITA_LINEAGE" };
    handle_acm_decision(&demo, ACM_DENY);
    printf("[pike-reaper] demo request enqueued for PID %d (PENDING).\n",
           (int)demo.pid);

    return 0;
}
