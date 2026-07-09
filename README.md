### *Engineering Architecture*

*Version:* `0.3.2`
*Applies to:* `EVK v0.3.x`
*Status:* `Draft` – Interfaces marked `stable` vs `evolving`

### *1. System Purpose*
*A 3-layer system for guarded execution:* Rust handles compute + isolation, Python handles orchestration + state, Dashboard handles visibility + control.

### *2. Layer Responsibilities*
Layer	Language	Owns	Does Not Do
**Rust Engine `evk-lib`**	Rust 1.75+	CPU-bound work, panic isolation, C-ABI surface	Network, disk, UI, state persistence
**Python Orchestrator**	Python 3.11+	Zodiac FSM, scheduling, FFI lifecycle, HTTP/WS server	Heavy compute, direct memory alloc for Rust
**Dashboard**	HTML/JS	DOM rendering, operator input, client PDF export	Business logic, state mutation
### *3. Concurrency Model*

- *Rust* performs CPU-bound work. *Public contract:* work may execute concurrently. *Current implementation:* uses `rayon` threadpool.
- *Python* owns all orchestration and mutable application state. Single-threaded asyncio for HTTP/WS.
- *Dashboard* is read-only except for operator commands via `POST`.
- *Cross-language communication* occurs _only_ through the documented C-ABI.

*Thread-safety:* Unless otherwise documented, exported FFI functions are not reentrant. The Python orchestrator must serialize calls to `evk_run_leo()`. Concurrent calls result in undefined behavior. `evk_version()` and `evk_free()` are thread-safe.

### *4. Finite State Machine – Zodiac Rooms*

Each guard has 3 states: `INTACT`, `POLUITA`, `DORMANT`.

*Health Score* = $100 \times \frac{\text{count(INTACT)}}{\text{count(INTACT) + count(POLUITA)}}$
*Status: ZODIAKO GARDAS* = `all(room.state == INTACT for room in rooms if room.state!= DORMANT)`

### *5. FFI Contract – Current FFI v0.3*

*Status: `evolving`* – Signatures may change before `v1.0`. Do not rely on ABI stability.

*5.1 ABI Compatibility Policy*
- *Major:* Breaking ABI changes allowed. Clients must recompile.
- *Minor:* New APIs may be added. Existing `stable` APIs remain binary compatible.
- *Patch:* Bug fixes only. No ABI or behavior changes.

*5.2 Error Code Registry*
Code	Name	Meaning
`0`	`EVK_OK`	Success
`1`	`EVK_ERR_INVALID_INPUT`	Input pointer null or length invalid
`2`	`EVK_ERR_ABI_MISMATCH`	`evk_version()` major mismatch
`3`	`EVK_ERR_PANIC`	Caught panic at FFI boundary
`4`	`EVK_ERR_NOT_INITIALIZED`	`evk_init()` not called or failed
`5`	`EVK_ERR_INTERNAL`	Unspecified internal error
`<0`	System error	OS errno, propagated as negative
*5.3 API Surface*
// [stable] Initialize engine. Returns EVK_OK on success.
int32_t evk_init(const EvkConfig* cfg);

// [evolving] Run Leo profile. Blocking. Returns EVK_OK on success.
// out_data must be freed with evk_free. May add flags param in v0.4.
int32_t evk_run_leo(const uint8_t* input, size_t input_len,
                    uint8_t** out_data, size_t* out_len);

// [stable] Free buffers allocated by Rust. Idempotent on NULL.
void evk_free(uint8_t* ptr);

// [stable] Get semantic version "major.minor.patch".
// Clients MUST verify major version before calling evolving interfaces.
const char* evk_version(void);

// [evolving] Register Python callback. Called from Rust worker threads.
// Event struct may extend. Check version first.
int32_t evk_set_callback(void (*cb)(const EvkEvent*));
*5.4 Lifecycle Sequence*

*Required order for all clients:*
1. `evk_init(&cfg)` → Check `== EVK_OK`
2. `evk_version()` → Parse major. If mismatch, abort with `EVK_ERR_ABI_MISMATCH`
3. `evk_set_callback(cb)` → Optional. Must complete before `evk_run_leo`
4. `evk_run_leo(...)` → May be called multiple times, serialized by caller
5. `evk_free(ptr)` → For each buffer returned
6. *Process exit* → No explicit shutdown. OS reclaims resources.

*5.5 Architectural Assumptions*
Area	Rule	Rationale
**Thread ownership**	Rust worker threads call Python callbacks. GIL acquired via `PyGILState_Ensure`. Callbacks must be non-blocking. Queue long work in Python.	Prevents deadlock. Guideline: <100ms.
**Memory ownership**	Rust allocates all FFI return buffers. Python calls `evk_free` exactly once. Python inputs are copied.	No double-free. No use-after-free.
**Panic boundary**	All `extern "C"` fns use `catch_unwind`. No panic crosses FFI.	Prevents interpreter abort.
**Version negotiation**	Call `evk_version()` after `init`. If major!= expected, return `EVK_ERR_ABI_MISMATCH`.	Prevents silent ABI breakage.
### *6. Non-goals*

*The EVK engine does not:*
- Guarantee complete threat detection. Coverage = implemented guards only.
- Persist application state. Restart = clean slate.
- Expose network services directly. I/O via Python layer only.
- Replace host OS security controls. Runs as userspace process.

### *7. Claims vs Reality*
Claim	Accurate version
"Rust can't crash"	Panics at FFI boundary → `EVK_ERR_PANIC`. Aborts, OOM, or UB can still terminate process.
"No exit 101"	Build-time `exit 101` fixed. Runtime aborts still possible.
"12/12 = secure"	12/12 = all implemented guards INTACT. Coverage ≠ completeness.
### *8. Mental Model*
Dashboard (DOM)
    ↕ HTTP/WS JSON
Python (FSM + Server + FFI Loader)
    ↕ C-ABI, raw pointers, EVK_ERR_* codes
Rust (Compute + Allocator)
*EVK = Engine + FFI bindings.*
*Zodiako Gardas = 12-room security FSM built on EVK.*

