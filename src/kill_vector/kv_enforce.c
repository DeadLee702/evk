/*
 * Z-12 Kill Vector — CLI bridge for subprocess invocation.
 *
 * Usage: kv_enforce <pid> [reason]
 *
 * Initializes the enforcement log, calls kill_vector_enforce(), and exits
 * with the function's return code (0 = enforced, -1 = refused/failed).
 * This lets the Python control plane invoke the audited C engine via
 * subprocess.run without duplicating SIGKILL logic.
 */
#define _POSIX_C_SOURCE 200809L

#include "killswitch.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <pid> [reason]\n", argv[0]);
        return 2;
    }

    long pid_val = strtol(argv[1], NULL, 10);
    if (pid_val <= 0) {
        fprintf(stderr, "[kv_enforce] invalid PID: %s\n", argv[1]);
        return 2;
    }

    const char *reason = (argc >= 3) ? argv[2] : "SUBPROCESS_ENFORCE";
    pid_t pid = (pid_t)pid_val;

    kill_vector_log_init();
    int rc = kill_vector_enforce(pid, reason);
    return (rc == 0) ? 0 : 1;
}
