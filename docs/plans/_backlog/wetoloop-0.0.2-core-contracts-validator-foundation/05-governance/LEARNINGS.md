# Learnings

## Planning observations

1. The WetoLoop template can drive a complete release-planning activity before a CLI or skill layer exists.
2. ImpactSet, VerificationRun, ProducerFingerprint and ProducerRecord are currently concepts carried by reasoning rather than enforced first-class contracts; 0.0.2 should make them explicit.
3. A strong written Test Strategy is insufficient when the aggregate validator does not validate it.
4. Compatibility code can silently become a second authority when legacy validation modes target a different document shape.
5. Dogfooding the activity that changes the contract is a useful conformance sensor but requires an explicit migration point to avoid circular planning authority.

## Test optimization candidates

Populate after implementation using measured duration, overlap, retry/flake data and producer invocation counts. Do not remove tests merely because they appear redundant during unrelated work.
