# Complete policy and retained validation

The three Python source files are byte-identical copies of the frozen research implementation and exact checkers. The policy imports only the standard library. Its inputs are an explicit original ANF encoded as monomial bit masks, ambient dimension, integer accuracy exponent, a getrandbits(k) provider and an original-input parity oracle. Fourier data and generic ranks are reference-only. Scripted test tapes do not implement the ideal independent fair-bit assumption of the probability theorem.

The exact reference computes residual ANFs, truth tables and determinant certificates solely to check bounded fixtures. It is not part of the general polynomial runtime claim. See the manuscript for cached bit-mask storage and all-tape resource accounting.

[Provenance](../verification/policy-provenance.json) binds the unchanged source files and raw receipts/logs. The historical S236 campaign remains STOP despite 19 certified good-event successes, because its final rank-collapse coverage gate failed. A separate S237 campaign passed both required rank-loss cases. The initial S236 import failure is also retained in its original receipt; no test was rerun for publication. Machine-specific controllers and stderr paths are omitted; their original hashes remain provenance, not claims that those files are included here.

To reproduce the deterministic cases with Python 3.10+:

    python tools/replay_policy_checks.py --suite s237 --execute
    python tools/replay_policy_checks.py --suite s236 --execute

The public wrapper invokes unchanged fixture/checking functions and their original aggregate acceptance conditions. S236 is expected to exit nonzero at its preserved coverage gate; this is not a new failure or an all-gates pass. S237 is expected to pass. Use an external process/resource limit; the original bounded controllers used 300 seconds/256 MiB for S236 and 120 seconds/128 MiB for S237. The wrapper is a new portable launcher, statically inspected but not executed for publication. It does not reproduce the original process-memory measurements or isolated-Python startup error.

Do not invoke the preserved checker files directly: their original entry points also hash machine-specific controller files omitted from this public export. Use the wrapper above. Document/package tools never run these experiments.
