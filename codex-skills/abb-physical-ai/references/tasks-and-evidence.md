# Tasks and evidence

A = reference an existing verified routine; B = constrained generated routine;
C = additive generated module. The category is not a physical risk level.
This release packages B/C cube drafts in a uniquely named module with `RunCube`;
neither includes an automatic approach, PLC handshake or asynchronous Stop code.

The 200 mm path uses workobject axes, constant TCP orientation and the sequence:

`000 100 110 010 000 001 101 111 011 001 101 100 110 111 011 010 000`

There are 16 segments, 12 different edges, 3200 mm total. At v50 and 30% override,
the nominal constant-speed duration is 213.33 s before acceleration and fine-point
stops. 600 s is an uncommissioned completion-time example, never a Stop timeout.
The generated code does not set speed override. Do not approach a frozen anchor
automatically; current pose/configuration requires separate validation.

Task input schema is in `mcp/physical_ai_bridge/schemas/task-spec.schema.json`.
The context binds controller, RobotWare/options, profile, Station, configuration,
dependencies, Tool/Load/WObj, anchor translation, orientation, robot configuration
and external axes. Files are immutable by normal tools; rendering uses a unique
directory and cannot overwrite existing modules, including those prefixed AI_.

A supplied report must bind `task_id`, `spec_hash`, `source_hash`, `context_hash`
and contain report ID, source and finite `issued_at`/`expires_at` Unix seconds.
Each of these must be exactly PASS:

- RAPID compilation (`rapid_check`), path reachability and joint limits;
- collision check, singularity/configuration review and speed review;
- model coverage and whole-path check, not just eight endpoints.

Allowed report-source labels are ROBOTSTUDIO_VC and OPERATOR_ROBOTSTUDIO_REVIEW.
Labels and hashes alone do not authenticate authorship. The current evaluator
returns `evidence_authenticity=UNVERIFIED`, `auto_deployable=false` and
`real_motion_authorized=false` even for a structurally complete report. No signed
execution credential exists in this release. UNKNOWN, absent, expired or changed
context returns INCOMPLETE. Never patch a preflight predicate to make a demo pass.
