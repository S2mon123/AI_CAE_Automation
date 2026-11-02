# Scoped rollback

Before this change, the existing `mcp/robotstudio` and
`codex-skills/robotstudio-core` sources were copied to an external baseline with
SHA-256 inventory and the pre-existing Git status. Its exact local location is in
the private delivery report, not public source.

This work does not overwrite controller/PLC projects or install an auto-start
service. To undo it, stop only the newly configured read-only processes, remove
only the optional `abb-physical-ai` Codex registration if you added it, and restore
the scoped source files from the recorded backup. Preserve unrelated user edits.
Do not use `git reset --hard`, `git clean` or repository-wide checkout: the baseline
already contained substantial uncommitted work.

Existing RobotStudio edits are Python tool registration/instructions, the new cube
context tool/tests, and Skill/documentation. Remove the new registration/import and
restore modified files from the scoped backup if later edits have not superseded
them. Restore repository indexes from their individual backups or reverse only
the Physical AI additions. The additive `physical_ai_bridge` and `abb-physical-ai`
skill directories can be archived independently after checking for newer work.

Keep generated task artifacts and evidence for traceability; deleting local drafts
is not a controller rollback. No physical state was changed by this development
run, and no robot pose restoration is required or performed.
