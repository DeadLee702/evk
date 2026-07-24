# Z-12 Kill Vector — C enforcement subsystem build.
#
# The main EVK engine is built with Cargo (`cargo build --release`). This
# Makefile builds the Kill Vector runtime-enforcement subsystem (C) and its test.
#
#   make killswitch.o      # compile the enforcement engine object
#   make test_killswitch   # build + run the Kill Vector test  -> "Kill Vector Test: PASS"
#   make reaper            # build the Pike/Reaper integration scaffold
#   make clean

CC      ?= cc
CFLAGS  ?= -Wall -Wextra -O2 -std=c11

KV_SRC   := src/kill_vector/killswitch.c
KV_HDR   := src/kill_vector/killswitch.h
KV_OBJ   := killswitch.o

TEST_SRC := tests/test_killswitch.c
TEST_BIN := test_killswitch_runner

REAPER_SRC := src/sensors/pike_reaper/reaper/src/main.c
REAPER_BIN := pike_reaper

KV_ENFORCE_SRC := src/kill_vector/kv_enforce.c
KV_ENFORCE_BIN := kv_enforce

.PHONY: all test_killswitch reaper kv_enforce clean

all: $(KV_OBJ) $(REAPER_BIN) $(KV_ENFORCE_BIN)

$(KV_OBJ): $(KV_SRC) $(KV_HDR)
	$(CC) $(CFLAGS) -c $(KV_SRC) -o $(KV_OBJ)

# Build and run the Kill Vector test. Logs to a temp file so it needs no root.
test_killswitch: $(KV_OBJ) $(TEST_SRC)
	$(CC) $(CFLAGS) $(TEST_SRC) $(KV_OBJ) -o $(TEST_BIN)
	Z12_KILL_LOG=$${TMPDIR:-/tmp}/z12_kill_test.log ./$(TEST_BIN)

$(REAPER_BIN): $(REAPER_SRC) $(KV_OBJ)
	$(CC) $(CFLAGS) $(REAPER_SRC) $(KV_OBJ) -o $(REAPER_BIN)

reaper: $(REAPER_BIN)

$(KV_ENFORCE_BIN): $(KV_ENFORCE_SRC) $(KV_OBJ) $(KV_HDR)
	$(CC) $(CFLAGS) $(KV_ENFORCE_SRC) $(KV_OBJ) -o $(KV_ENFORCE_BIN)

kv_enforce: $(KV_ENFORCE_BIN)

clean:
	rm -f $(KV_OBJ) $(TEST_BIN) $(REAPER_BIN) $(KV_ENFORCE_BIN)
