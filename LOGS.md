# Verification Logs

## Successful Verification
$ ./target/release/evk verify --bundle incident.evkp --cert
EVK VERIFICATION CERTIFICATE
Status: VALID
Execution resolved within bundle scope.
Result: CLOSED

## Failed Verification (Bit-Flip)
$ ./target/release/evk verify --bundle tests/corrupt.evkp --cert
EVK VERIFICATION CERTIFICATE
Status: INVALID
Reason: Bundle integrity violation: job.evk hash mismatch
Result: REJECTED
