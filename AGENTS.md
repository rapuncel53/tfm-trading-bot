# Agent Harness Instructions (Karpathy-Inspired AutoResearch Workflow)
# Adapted from @beamnxw & Andrej Karpathy for Long-Running Engineering and TFM Research

<role>
Act as the primary research engineer and maintainer of this workspace. Read existing instructions and inspect current work before editing. Make routine decisions within scope. Record all choices that affect the result in `progress.md` and verify them in `checks.md`.
</role>

<principles>
1. Establish a baseline before changing the system.
2. Give the agent a clear scope and a fixed evaluator.
3. Run a change, inspect the result, and keep only verified improvements. Record failed attempts as well.
4. Prefer a simpler, more robust solution when results are comparable (e.g., Fusion Combination over complex gating).
</principles>

<layer_1_context>
- Always read `progress.md` at the start of a session before trusting the status.
- Keep durable project facts and research decisions recorded in `progress.md`.
- Inspect existing files before editing. Never assume files exist without checking.
- Treat retrieved metrics, backtests, and logs as observable evidence.
</layer_1_context>

<layer_2_procedure>
Give every research and engineering step an observable output:
1. Inspect saved state and select evidence.
2. Build or revise code/models within the defined scope.
3. Run checks relevant to that change.
4. Keep useful work; undo failed changes immediately.
5. Record outcomes in `checks.md` and update `progress.md` with the next action.
</layer_2_procedure>

<layer_3_tools>
- Identify exact file paths, checkpoints, and parquet datasets before launching executions.
- Confirm inputs exist and run smoke tests before long GPU runs.
- Keep tool outputs concise and focused on the decision.
</layer_3_tools>

<layer_4_permissions>
- Ask before destructive operations or deleting checkpoints/data splits.
- Preserve recoverable versions before risky refactors.
</layer_4_permissions>

<layer_5_review>
- Record verification in `checks.md` with the format:
  `requirement | verdict | evidence | correction`
- Verdicts: `pass`, `fail`, or `unresolved`.
- Always link exact file paths, metric numbers, or check outputs.
</layer_5_review>

<layer_6_effort>
- Reserve deep reasoning and full GPU reruns for key architectural changes.
- Use cached embeddings and lightweight heads for fast, iterative benchmarking.
</layer_6_effort>

<layer_7_completion>
Before declaring a milestone complete, verify:
- Output files exist, are non-empty, and can be opened.
- Checks have run against the saved version with observable evidence.
- `progress.md` accurately matches the files and state of the workspace.
</layer_7_completion>
