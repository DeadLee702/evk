/*
 * Z-12 Kill Vector test.
 *
 * 1. Fork a child process that sleeps.
 * 2. Parent calls kill_vector_enforce(child_pid, "TEST_POLICY_VIOLATION").
 * 3. Verify via waitpid() + WIFSIGNALED() that the child was terminated by the
 *    Kill Vector (SIGKILL).
 *
 * Also verifies the safety guard: enforcing an unsafe PID (1) is refused.
 */
#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE
#define _XOPEN_SOURCE 700

#include "../src/kill_vector/killswitch.h"

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    kill_vector_log_init();

    /* Safety guard: unsafe PID must be refused. */
    if (kill_vector_enforce(1, "SHOULD_BE_REFUSED") == 0) {
        fprintf(stderr, "Kill Vector Test: FAIL (acted on unsafe PID 1)\n");
        return 1;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return 1;
    }

    if (child == 0) {
        /* Child: sleep; should be killed before it returns. */
        sleep(30);
        _exit(0);
    }

    /* Parent: give the child a moment to enter sleep, then enforce. */
    usleep(100000); /* 100ms */

    if (kill_vector_enforce(child, "TEST_POLICY_VIOLATION") != 0) {
        fprintf(stderr, "Kill Vector Test: FAIL (enforce returned error)\n");
        return 1;
    }

    int status = 0;
    if (waitpid(child, &status, 0) != child) {
        fprintf(stderr, "Kill Vector Test: FAIL (waitpid)\n");
        return 1;
    }

    if (WIFSIGNALED(status) && WTERMSIG(status) == SIGKILL) {
        printf("Child terminated by Kill Vector\n");
        printf("Kill Vector Test: PASS\n");
        return 0;
    }

    fprintf(stderr, "Kill Vector Test: FAIL (child not SIGKILLed, status=%d)\n",
            status);
    return 1;
}
