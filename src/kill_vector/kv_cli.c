/*
 * Z-12 Kill Vector CLI — command-line enforcement bridge.
 * Usage: killswitch <pid> <reason>
 * Returns: 0=success, 1=refused/failed, 2=usage error
 */
#define _POSIX_C_SOURCE 200809L

#include "killswitch.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <pid> <reason>\n", argv[0]);
        return 2;
    }
    int pid = atoi(argv[1]);
    if (pid <= 0) {
        fprintf(stderr, "[killswitch] invalid pid: %s\n", argv[1]);
        return 2;
    }
    if (kill_vector_log_init() != 0) {
        fprintf(stderr, "[killswitch] warning: log init failed, continuing\n");
    }
    int result = kill_vector_enforce((pid_t)pid, argv[2]);
    if (result == 0) {
        printf("[killswitch] enforcement succeeded: pid=%d reason=%s\n", pid, argv[2]);
        return 0;
    }
    fprintf(stderr, "[killswitch] enforcement failed: pid=%d reason=%s\n", pid, argv[2]);
    return 1;
}
