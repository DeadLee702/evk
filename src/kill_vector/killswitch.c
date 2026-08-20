/*
 * Z-12 Kill Vector — enforcement engine.
 *
 * See killswitch.h for the API contract and safety guarantees.
 */
#define _POSIX_C_SOURCE 200809L

#include "killswitch.h"

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define KV_DEFAULT_LOG_DIR "/var/log/z12"
#define KV_DEFAULT_LOG_PATH KV_DEFAULT_LOG_DIR "/kill.log"

/* Lowest PID the Kill Vector is permitted to act on. PIDs <= 1 are refused. */
#define KV_MIN_SAFE_PID 2

/*
 * Resolve the log path. Honors the Z12_KILL_LOG override (used by tests and by
 * environments where /var/log is not writable); otherwise uses the default
 * /var/log/z12/kill.log.
 */
static const char *kv_log_path(void) {
    const char *override = getenv("Z12_KILL_LOG");
    if (override != NULL && override[0] != '\0') {
        return override;
    }
    return KV_DEFAULT_LOG_PATH;
}

int kill_vector_log_init(void) {
    /* Only attempt to create the default directory; an override path is assumed
     * to live in an already-existing directory. */
    const char *override = getenv("Z12_KILL_LOG");
    if (override == NULL || override[0] == '\0') {
        if (mkdir(KV_DEFAULT_LOG_DIR, 0750) != 0 && errno != EEXIST) {
            fprintf(stderr,
                    "[kill_vector] warning: cannot create %s: %s\n",
                    KV_DEFAULT_LOG_DIR, strerror(errno));
            return -1;
        }
    }

    FILE *f = fopen(kv_log_path(), "a");
    if (f == NULL) {
        fprintf(stderr, "[kill_vector] warning: cannot open log %s: %s\n",
                kv_log_path(), strerror(errno));
        return -1;
    }
    fclose(f);
    return 0;
}

/* Append one enforcement record. Never fails the enforcement path: if the log
 * file cannot be opened, the event is mirrored to stderr instead. */
static void kv_log_event(pid_t pid, const char *reason, const char *action) {
    long ts = (long)time(NULL);
    FILE *f = fopen(kv_log_path(), "a");
    if (f == NULL) {
        fprintf(stderr, "[%ld] PID=%d REASON=%s ACTION=%s\n", ts, (int)pid,
                reason ? reason : "UNSPECIFIED", action);
        return;
    }
    fprintf(f, "[%ld] PID=%d REASON=%s ACTION=%s\n", ts, (int)pid,
            reason ? reason : "UNSPECIFIED", action);
    fclose(f);
}

int kill_vector_enforce(pid_t pid, const char *reason) {
    if (pid < KV_MIN_SAFE_PID) {
        kv_log_event(pid, reason, "REFUSED_UNSAFE_PID");
        fprintf(stderr, "[kill_vector] refusing unsafe PID %d\n", (int)pid);
        return -1;
    }

    if (kill(pid, SIGKILL) != 0) {
        kv_log_event(pid, reason, "FAILED_SIGKILL");
        fprintf(stderr, "[kill_vector] kill(%d) failed: %s\n", (int)pid,
                strerror(errno));
        return -1;
    }

    kv_log_event(pid, reason, "SIGKILL");
    return 0;
}
