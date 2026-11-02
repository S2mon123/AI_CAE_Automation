# Future physical execution requirements

These are development requirements, not capabilities currently available.

Before adding any physical write backend, centralize actual side-effect
classification and enforce it again on the Win7 execution boundary. Start TRUE
and FALSE, recovery, path parameters and PP changes may all move equipment.
Done and safety signals must remain unwritable. No toggle or arbitrary address API.

The operator approval mechanism must bind action, desired value and expected
pre-state to task, controller, AMS/Runtime, context/source hashes, valid simulation
evidence and a commissioned independent Stop channel. Codex must not create or
approve its own physical-motion authorization. Files writable by the same account
are procedural records, not strong security isolation.

Use a persistent local Supervisor, durable command ledger, one active owner and
explicit request IDs. Persist before effects; a timeout/crash after transmission
means OUTCOME_UNKNOWN, never automatic resend, Start clearing or recovery.
One BOOL cannot guarantee exactly-once execution across crashes. Reliable unattended
operation requires a commissioned sequence/ack/session and local watchdog contract.

Process Stop requires authentication but no new motion approval. Implement an
independent low-latency path that cannot queue behind wait_done, simulation or COM.
Report STOP_REQUESTED, REQUEST_DELIVERED, RAPID_STOPPED and STANDSTILL_OBSERVED
separately. Ordinary software Stop does not replace hardware safety functions.
Clearing Stop must not Resume or move home. A failed/unavailable Stop requires the
verified site procedure, not a success response.

Deployment is a separate transaction: current inventory, backup, ownership and
dependencies, simulation/review, exact diff, approval, additive load, readback and
hash verification. A prefix does not establish ownership. Preserve production
main/system modules. Failure must not automatically unload an executing module,
reset PP or restore a mechanical pose.
