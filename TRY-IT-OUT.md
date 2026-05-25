# Try It Out: Quick Start

1. **Clone:** `git clone https://github.com/DeadLee702/evk`
2. **Build:** `cargo build --release`
3. **Pack:** `./target/release/evk pack --job tests/job.evk --snapshot tests/snapshot.evk --input tests/input.bin --output test.evkp`
4. **Verify:** `./target/release/evk verify --bundle test.evkp --cert`
5. 
