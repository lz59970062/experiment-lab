---
name: experiment-lab
description: Manage computer science experiments — design protocols, pre-run reflection/checks, run records, analysis, and reports. Activate whenever the user discusses experiments, benchmarks, ablation studies, training runs, performance tests, data collection, research protocols, experimental design, or any structured research workflow. Before any formal experiment or training run, require a user-visible reflection that understands the scenario, checks parameter reasonableness, configuration completeness, and experiment-chain risks. Do not wait for the user to explicitly ask for lab commands — proactively suggest `/lab` commands when the conversation involves planning, running, or analyzing experiments.
---

# Experiment Lab

> **When to activate:** This skill activates for any conversation about planning, running, or analyzing experiments. Do not wait for the user to say `/lab` — proactively offer it when the topic fits.

## Python Package Requirement

This skill uses the installable `experiment-lab` Python package for helper commands such as `lab-queue`.

If `lab-queue` or `experiment-lab-paths` is not available in the active Python environment, ask the user before installing it. Use the package manager for the actual active environment:

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

If the project uses `uv`, use the active project interpreter explicitly:

```bash
uv pip install --python "$(command -v python)" git+https://github.com/lz59970062/experiment-lab.git
```

When this skill is installed with `experiment-lab-install-skill`, the copied `SKILL.md` includes a generated install command for the Python interpreter that ran the installer.

CS experiment management system for designing, running, and analyzing experiments.

## Overview

Helps researchers and engineers conduct structured experiments with proper scientific methodology. Manages the full lifecycle: design → run → record → analyze → report.

## Mandatory Pre-Run Reflection

Before starting any formal experiment, benchmark, ablation, or training run, pause and produce a short user-visible reflection/check. Do this even when the user sounds ready to run. The goal is not ceremony; it is to catch flawed comparisons, incomplete configs, and broken experiment chains before compute is spent.

The pre-run reflection must cover:

- **Scenario understanding**: what the experiment is trying to test, the core claim/hypothesis, and the comparison or control group.
- **Variable hygiene**: what changes, what stays fixed, and whether more than one meaningful variable is being changed at once.
- **Parameter reasonableness**: key hyperparameters or run settings, why they fit the goal, and any values that look risky or under-specified.
- **Configuration completeness**: dataset paths, checkpoints/weights, output directories, seeds, hardware/GPU choice, eval cadence, logging fields, and whether old artifacts could be reused by accident.
- **Execution-chain risks**: whether the intended code path actually enables/disables the right model branches, losses, metrics, preprocessing, inference, and reporting steps.
- **Decision**: either `Proceed`, `Proceed with cautions`, or `Do not start yet`, with the concrete reasons and fixes.

If information is missing, inspect the repository/configs when possible. If a critical setting still cannot be verified, do not silently start the formal run; surface the uncertainty and ask for the minimum missing input. For low-risk exploratory smoke tests, state that it is a smoke test and record what it does not validate.

## Long Task Wakeup Integration

When a formal experiment, training run, benchmark, ablation, or long backtest is likely to finish
after Codex may be inactive, use `long-task-callback` by default when available. This means:

- Prefer `codex-long-task-wakeup run --via-daemon --session "$CODEX_THREAD_ID" --cwd "$PWD" ...`
  around the long command when Codex launches it directly.
- Prefer `codex-long-task-wakeup done --via-daemon ...` in shell traps, Python `finally` blocks,
  Slurm epilogues, or other externally managed exit paths.
- Use the systemd daemon path as the standard durable setup:
  `codex-long-task-wakeup install-systemd --enable --now`.
- Record the exact wakeup-wrapped command and queue/service assumptions in the experiment
  `report.md`, together with the usual logs, screen names, run IDs, and metrics.

Before relying on wakeup, check the minimum viable conditions when possible:

```bash
command -v codex-long-task-wakeup
systemctl --user is-active codex-long-task-wakeup.service
```

If `codex-long-task-wakeup` is unavailable, the daemon is not active, or the user does not want
automatic wakeup, continue with the normal experiment-lab recording flow and explicitly note that
the run has no callback. Do not install or start services without the user's approval.

For multi-round experiment chains, follow the `long-task-callback` controlled autonomy rule: after
each wakeup, write a short decision record (`continue`, `stop_success`, `stop_blocked`, or
`ask_user`) before launching another long task. Continue automatically only for clear, low-risk,
same-goal follow-ups within budget. Stop and ask the user when the next step requires new GPU time,
data, credentials, disk, a changed hypothesis/main variable, larger search space, or a strategic
tradeoff.

## When to Activate

**Actively invoke this skill** whenever the conversation involves:

- Planning or designing an experiment, benchmark, or ablation study
- Running experiments and recording results
- Collecting or analyzing performance data
- Writing up experimental reports or papers
- Managing a research project with multiple experiments
- Debugging unexpected experimental results
- Comparing multiple experimental conditions

**Proactive prompts** — do not wait for the user to say `/lab`:

- User describes an experiment idea → offer `/lab init` to scaffold it
- User mentions running a test → offer `/lab run` to record it properly
- User shows experimental data → offer `/lab analyze` or `/lab validate`
- User has multiple related experiments → offer `/lab collection` or `/lab search`
- User plans a series of experiments → offer `/lab tasks` to build a queue
- User wants a second opinion on methodology → offer `/lab review design`
- User wants to publish or share results → offer `/lab report`

Do not activate for casual mentions of experiments without intent to plan, run, or analyze.

## Directory Structure

Each experiment is stored in:
```
[project-root]/.experiments/
├── roadmap.md                     # Project-level experiment roadmap, always maintained
├── _tasks/
│   │   ├── _queue.json          # Pending task queue
│   │   └── _index.json         # Task index (id→path mapping)
│   ├── YYYY-MM-DD-experiment-name/
│   │   ├── _meta.json           # Experiment metadata
│   │   ├── design.md           # Experiment design document
│   │   ├── runs/               # Individual run data
│   │   ├── results.md          # Aggregated results and analysis
│   │   ├── report.md           # Final experiment report
│   │   └── _collection.md       # Optional: belongs to a result collection
│   └── _collections/            # Cross-experiment result groupings
│       ├── _index.json         # Collection index
│       ├── my-paper-figures.json
│       ├── ablation-summary.json
│       └── ...
```

## Commands

### /lab init <experiment-name>
Create a new experiment with interactive design.

Steps:
1. Ask for research question / hypothesis
2. Define independent variables (what you're changing)
3. Define dependent variables (what you're measuring)
4. Define controlled variables (what stays constant)
5. Determine sample size / number of runs
6. Create experiment directory and design.md

Example design.md:
```markdown
# Experiment: [Name]

**Date**: YYYY-MM-DD
**Status**: designed | running | completed

## Research Question
[What are we trying to learn?]

## Hypothesis
[Expected outcome]

## Variables

### Independent ( manipulated )
| Variable | Levels | Description |
|----------|--------|-------------|
| [var1]   | [v1, v2, v3] | [what it is] |

### Dependent ( measured )
| Variable | Unit | Measurement Method |
|----------|------|-------------------|
| [metric1] | ms | [how measured] |

### Controlled ( held constant )
- [var]: [value]

## Methodology
[Experimental procedure]

## Sample Size
[N runs per condition]
```

### /lab run
Record a new experimental run.

Before recording or launching a formal run, perform the **Mandatory Pre-Run Reflection** above and show it to the user. If the run is a training job, explicitly check that the config, hyperparameters, loss branches, checkpoint behavior, output directory, evaluation schedule, and logs match the experiment goal before starting.

Interactive prompt for:
- Run parameters (independent variable values)
- Measured outcomes (dependent variable values)
- Notes / observations
- Timestamp (auto)

Stores as JSON:
```json
{
  "run_id": "run-003",
  "timestamp": "2024-01-15T14:30:00Z",
  "environment": {
    "hostname": "server-01",
    "cpu": "Intel Xeon Gold 6248",
    "memory_gb": 128,
    "gpu": "NVIDIA A100 40GB",
    "cuda_version": "12.1",
    "os": "Ubuntu 22.04",
    "git_commit": "a1b2c3d4",
    "git_dirty": false,
    "python_version": "3.10.12",
    "random_seed": 42
  },
  "parameters": {
    "batch_size": 32,
    "learning_rate": 0.001
  },
  "results": {
    "accuracy": 0.945,
    "training_time_ms": 12500
  },
  "notes": "GPU utilization was 95%"
}
```

### /lab queue
Use a lightweight sequential queue when multiple long-running experiment tasks must not run concurrently. Prefer this over ad hoc watcher scripts for single-machine training queues.

Bundled helper: `scripts/lab_queue.py`

Installable command: `lab-queue` from the `experiment-lab` Python package. Prefer `lab-queue` when the package is installed, because it avoids hard-coding the local Codex skill directory path. Use `python scripts/lab_queue.py ...` only when running directly from an unpacked skill checkout.

Queue state lives in:
```text
.experiments/_tasks/_queue.json
.experiments/_tasks/_queue.lock
.experiments/_tasks/_exits/
```

Minimal task fields:
```json
{
  "task_id": "2026-04-26-example-train",
  "status": "queued",
  "command": "python train.py --gpu 2",
  "screen": "train_example_20260426",
  "log": "logs/train.log",
  "depends_on_screen": "optional_existing_screen"
}
```

Status lifecycle:
```text
queued -> launching -> running -> completed
queued -> launching -> running -> failed
queued -> cancelled
```

Rules:
- Use `queued` for work that must wait; do not start its training screen manually.
- Run exactly one worker per project queue, normally inside its own `screen`.
- The worker starts the first runnable queued task, then waits until that task's screen disappears before starting the next task.
- A task with `depends_on_screen` is not runnable until that external screen disappears.
- Every state transition must update `_queue.json`; terminal states must include `finished_at`.
- Use `flock`/the helper's lock file for writes; do not hand-edit `_queue.json` while a worker is active unless stopping the worker first.

Typical commands:
```bash
# enqueue
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-example-train \
  --screen train_example_20260426 \
  --log logs/train_example_20260426.log \
  --depends-on-screen train_current_20260426 \
  --command 'python train.py --gpu 2'

# start one queue worker
screen -dmS lab_queue_20260426 bash -lc \
  'lab-queue worker --root /path/to/project --poll-seconds 60'

# inspect status
lab-queue status --root /path/to/project
```

For training runs, still follow the Mandatory Pre-Run Reflection before enqueueing. Save the exact `enqueue` command, worker screen name, target screen name, and training command in the experiment `report.md`.

When the queued task is long-running and wakeup conditions are met, bake the wakeup wrapper into
the queued command at enqueue time so the target `CODEX_THREAD_ID` and `cwd` are explicit:

```bash
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-example-train \
  --screen train_example_20260426 \
  --log logs/train_example_20260426.log \
  --command 'codex-long-task-wakeup run --via-daemon --session "'"$CODEX_THREAD_ID"'" --cwd /path/to/project --task "2026-04-26-example-train" -- python train.py --gpu 2'
```

If the command is already managed by a script or scheduler, put `codex-long-task-wakeup done
--via-daemon` in that script's exit path instead of wrapping the worker command twice.

### /lab status
Show experiment overview:
- Total runs completed
- Summary statistics per condition
- Missing data flags

### /lab analyze
Generate results.md with:
- Descriptive statistics (mean, std, min, max per condition)
- Comparison tables
- Effect size calculations (Cohen's d for two groups, eta-squared for multiple)
- Statistical significance tests (t-test, ANOVA as appropriate)
- Confidence intervals (95%)
- Observations and patterns

Statistical tests to perform:
- Two conditions: Welch's t-test (handles unequal variance)
- Three+ conditions: One-way ANOVA with post-hoc Tukey HSD
- Paired data: Paired t-test
- Non-normal: Mann-Whitney U or Kruskal-Wallis

Report format:
```markdown
## Statistical Analysis

### Condition Comparisons
| Comparison | Mean Diff | 95% CI | p-value | Significant |
|------------|-----------|--------|---------|-------------|
| A vs B     | 12.5 ms   | [8.2, 16.8] | 0.003 | **Yes** |

### Effect Sizes
| Comparison | Cohen's d | Interpretation |
|------------|-----------|----------------|
| A vs B     | 1.24      | Large |

### Sample Size Check
- Minimum required: n=3 per condition
- Actual: n=5 per condition ✅
- Power (estimated): 0.85 for detecting d=0.8
```

### /lab plot
Create visualizations (ASCII or suggests code):
- Bar charts for comparisons
- Line plots for trends
- Box plots for distributions

### /lab report
Generate final report.md:
```markdown
# Experiment Report: [Name]

## Executive Summary
[Key findings in 2-3 sentences]

## Results
[Tables and figures]

## Statistical Analysis
[Significance tests if applicable]

## Conclusions
[Does data support hypothesis?]

## Limitations
[Known issues, confounding factors]

## Next Steps
[Follow-up experiments]
```

### /lab review [design|data|report]
Convene expert subagents to review experiment quality.

**When to use:**
- Before running: `/lab review design` — validate experimental design
- After analysis: `/lab review data` — check statistical validity
- Before publication: `/lab review report` — comprehensive review

#### Review Panel Configuration

#### Execution Mode: Foreground (实时前台执行)

All review subagents run in **foreground blocking mode** — the agent waits for all experts to complete before returning results. This ensures the full review panel is visible and results are collected synchronously.

```
User: /lab review design
  │
  ├─→ Agent spawns 4 subagents simultaneously (foreground):
  │     Methodologist   ──→ [reads design.md] ──→ Review
  │     Statistician    ──→ [reads design.md] ──→ Review
  │     Domain Expert   ──→ [reads design.md] ──→ Review
  │     Reproducibility ──→ [reads design.md] ──→ Review
  │
  │  All subagents run in parallel, each blocked until done
  │
  └─→ Agent waits for all results, then:
        1. Shares all reviews with all experts (Phase 2)
        2. Spawns discussion round (foreground)
        3. Synthesizes into final report
        4. Presents to user as single cohesive output
```

**Key behaviors:**
- All subagent work is **synchronous and blocking** — the agent does not return to the user until the complete review (all phases) is done
- Subagents see each other's work — the discussion phase depends on reading all Phase 1 outputs
- The agent synthesizes expert opinions into a **unified, prioritized action plan** — not just raw opinions concatenated
- If a subagent reports a P0 issue, the agent **pauses and surfaces it immediately** before proceeding

#### Subagent Review Output Format

Each subagent outputs a structured Phase 1 review:

```
## [Expert Role] — Supportive Review

### Verification & Validation
1. [What was checked]
   - Status: verified / needs attention / question
   - Evidence: [what supports this assessment]
   - If attention needed: [specific, actionable suggestion]

### Assistance Offered
- [Ways to improve the experiment or analysis]
- [Alternative approaches to consider]
- [Resources or references that might help]

### Questions for Clarity
- [Non-judgmental questions to understand intent]

### Confidence Assessment
- Implementation correctness: high/medium/uncertain
- Key strengths: [what's done well]
- Areas where help may be useful: [constructive suggestions]
```

#### Synthesis: Parent Agent Role

After collecting all expert Phase 1 outputs, the parent agent:

1. **Detects P0 issues** — if any expert marks a verification item as critical, surface it prominently before the discussion
2. **Cross-references** — identifies where experts agree or disagree on the same point
3. **Prioritizes** — P0 items first, then P1, then P2
4. **Produces Phase 3 report** — a single actionable document, not raw subagent opinions
5. **Offers encouragement** — explicitly call out what's done well

#### Review Philosophy

**Purpose**: Help the researcher produce valid, reliable results—not to criticize.

**Tone**: Constructive, curious, helpful. Assume good faith and competence.

**Focus Areas** (in priority order):
1. **Implementation correctness** — Does the code do what the design says?
2. **Assumption validity** — Are the statistical/technical assumptions reasonable?
3. **Interpretation support** — Are conclusions well-supported by the data?
4. **Improvement suggestions** — How could this be even better?

#### Phase 2 — Collaborative Discussion

After collecting all Phase 1 reviews, spawn the discussion round:

- Share perspectives ("I noticed X, did you consider Y?")
- Offer alternative interpretations
- Converge on helpful recommendations
- Celebrate good practices

#### Phase 3 — Supportive Report

Generate review report focused on helping:

```markdown
# Experiment Review: [Experiment Name]
**Review Date**: YYYY-MM-DD
**Type**: design | data | report
**Tone**: Supportive & Constructive

## Summary
- ✅ Verification passed: N items
- 🔧 Assistance offered: N suggestions
- ❓ Questions for clarity: N items
- Overall: ready / needs small fixes / let's discuss

## Implementation Correctness (Priority 1)

### 1. [Verification Item]
- **Aspect checked**: [what was verified]
- **Status**: ✅ Verified / 🔧 Needs attention / ❓ Question
- **Evidence**: [basis for assessment]
- **If attention needed**: [specific, actionable fix with example code if applicable]
- **Impact if not addressed**: [consequence, framed helpfully]

## Design/Analysis Validity (Priority 2)

[Similar format—focused on whether approach can answer the question]

## Suggestions for Improvement (Optional)

### [Suggestion Title]
- **Current approach**: [what's being done]
- **Consider**: [alternative or enhancement]
- **Why**: [benefit, not criticism of current]
- **Reference**: [paper, tutorial, example]

## Collaborative Discussion

### Shared Observations
- [What all experts agree is working well]

### Different Perspectives
- **[Topic]**: [Expert A noticed X, Expert B suggests Y as an alternative worth considering]

## Expert Contributions

### Methodologist
- Verified: [what's sound in the design]
- Helpful suggestion: [how to strengthen it]
- Open question: [something to consider, not a flaw]

### Statistician
- Verified: [statistical approach is appropriate]
- Helpful suggestion: [enhancement or alternative analysis]
- Open question: [consideration for interpretation]

### Domain Expert
- Verified: [implementation matches intent]
- Helpful suggestion: [technical improvement]
- Open question: [implementation detail to confirm]

### Reproducibility Auditor
- Verified: [what's well-documented]
- Helpful suggestion: [how to improve reproducibility]
- Open question: [documentation clarification]

## Action Items (Collaborative)

| Priority | Action | Help Available From | Notes |
|----------|--------|---------------------|-------|
| P0 | [If critical fix truly needed] | [Expert] | [Specific guidance] |
| P1 | [Suggested improvement] | [Expert] | [How to implement] |
| P2 | [Nice-to-have enhancement] | [Expert] | [Optional reference] |

## Encouragement

[Specific strengths of the experiment to acknowledge]
```

Save review to: `experiments/[name]/review-[type]-YYYY-MM-DD.md`

#### Design Review Checklist (/lab review design)

**Methodologist — Helping ensure the design answers the question:**
- [ ] Research question is clear and the design can answer it
- [ ] Hypothesis is testable with this approach
- [ ] Variables are defined in a way that supports the hypothesis
- [ ] Controlled variables help isolate the effect of interest
- [ ] Sample size is reasonable for the expected effect
- [ ] Consider: Are there confounds I can help you think through?

**Statistician — Helping ensure the analysis plan is sound:**
- [ ] Planned tests are appropriate for the data structure
- [ ] Sample size supports the planned analysis
- [ ] Consider: Would you like suggestions on effect size reporting?
- [ ] Offer: Alternative analysis approaches if interested

**Domain Expert — Helping verify technical correctness:**
- [ ] Implementation approach matches the stated methodology
- [ ] Measurements capture what they intend to measure
- [ ] Consider: Edge cases or technical pitfalls to be aware of?
- [ ] Offer: Code review if helpful

**Reproducibility Auditor — Helping make work reproducible:**
- [ ] Key details for replication are documented
- [ ] Random seeds and environment are captured
- [ ] Consider: Additional documentation that might help future you or others?
- [ ] Offer: Template or example if useful

#### Data Review Checklist (/lab review data)

**Methodologist — Helping ensure data quality:**
- [ ] Data collection followed the planned protocol
- [ ] Consider: Any data patterns that might need explanation?
- [ ] Offer: Suggestions for handling edge cases if needed

**Statistician — Helping ensure analysis correctness:**
- [ ] Analysis matches the pre-registered plan (or deviations are documented)
- [ ] Statistical assumptions are reasonable for this data
- [ ] Consider: Would additional diagnostics be helpful?
- [ ] Offer: Alternative visualization or summary approaches

**Domain Expert — Helping verify results make sense:**
- [ ] Results are technically plausible given the implementation
- [ ] No obvious bugs or artifacts in the data
- [ ] Consider: Sanity checks that might increase confidence?
- [ ] Offer: Validation techniques used in the field

**Reproducibility Auditor — Helping ensure transparency:**
- [ ] All runs are documented with complete metadata
- [ ] Analysis code is available and matches description
- [ ] Consider: Additional provenance information that would be helpful?

#### Report Review Checklist (/lab review report)

**All experts — Helping ensure clear communication:**
- [ ] Claims are supported by the data shown
- [ ] Limitations are acknowledged transparently
- [ ] Visualizations accurately represent the data
- [ ] Consider: Would additional context help readers?
- [ ] Offer: Writing or presentation suggestions if helpful

**Statistician — Helping with statistical communication:**
- [ ] Statistical claims are precise and appropriately qualified
- [ ] Uncertainty is communicated clearly
- [ ] Offer: Wording suggestions for statistical claims

**Domain Expert — Helping with technical accuracy:**
- [ ] Technical details are correct and complete
- [ ] Implementation description matches what was done
- [ ] Offer: Clarifications that might help readers

### /lab tasks [subcommand]
Manage the experiment task queue — plan what to run, track pending work, and organize by priority.

#### Task States

```
planned → queued → running → completed
                    ↓
                 blocked (by dependency)
                    ↓
                 skipped (no longer needed)
                    ↓
                 failed (error during execution)
```

#### Subcommands

**`/lab tasks add`** — Add a new pending task

Interactive prompt for:
- Task description (what to run)
- Target experiment (existing or new)
- Priority (P0 critical, P1 high, P2 medium, P3 low)
- Dependencies (blockers — task IDs that must complete first)
- Estimated duration
- Notes / context

Stores task in `_tasks/_queue.json`:

```json
{
  "task_id": "task-042",
  "description": "Ablation: remove attention mechanism",
  "target_experiment": "YYYY-MM-DD-model-ablation",
  "priority": "P1",
  "status": "planned",
  "dependencies": ["task-041"],
  "created_at": "2024-03-15T10:00:00Z",
  "estimated_duration_minutes": 45,
  "notes": "Based on finding from task-038 — attention contributes 15ms latency overhead",
  "tags": ["ablation", "attention", "latency"],
  "created_by": "alice"
}
```

**`/lab tasks list [--filter STATUS] [--sort PRIORITY|DATE]`** — Show task queue

Default shows all non-completed tasks, sorted by priority:

```
Task Queue (.experiments/_tasks/)
══════════════════════════════════════════════════════════════
ID       │ Status    │ Priority │ Description                │ Experiment
─────────┼───────────┼──────────┼────────────────────────────┼────────────────────────────
task-042 │ planned   │ P1       │ Ablation: remove attention │ 2024-03-10-model-ablation
task-041 │ running   │ P1       │ Ablation: remove FFN layer │ 2024-03-10-model-ablation
task-040 │ queued    │ P2       │ Compare batch sizes 16/32   │ 2024-03-12-batch-size
task-039 │ blocked   │ P1       │ Reproduce baseline from pa… │ 2024-03-08-reproduce-test
task-037 │ completed │ P1       │ Baseline measurement        │ 2024-03-08-baseline
...
══════════════════════════════════════════════════════════════
8 pending | 1 running | 5 completed | 2 blocked
```

**`/lab tasks next`** — Show the highest-priority queued task

```
Next task to run:
══════════════════════════════════════
ID:      task-042
Desc:    Ablation: remove attention mechanism
Exp:     2024-03-10-model-ablation
Depends: task-041 (running)
Status:  → ready (dependency satisfied)
──────────────────────────────────────
Run with: /lab run --experiment 2024-03-10-model-ablation
Mark done: /lab tasks done task-042
```

**`/lab tasks done <task-id>`** — Mark task as completed

Also prompts for a brief summary of what was learned/observed.

**`/lab tasks fail <task-id> [--note "..."]`** — Mark task as failed

**`/lab tasks skip <task-id> [--reason "..."]`** — Mark task as skipped

**`/lab tasks edit <task-id>`** — Edit task fields interactively

**`/lab tasks depend <task-id> [--add <dep-id>] [--remove <dep-id>]`** — Manage dependencies

**`/lab tasks log`** — Show activity timeline

Chronological log of all task state changes:
```
2024-03-15 14:23 | task-037 → completed | Baseline measurement done
2024-03-15 14:24 | task-038 → queued    | Auto-queued after task-037
2024-03-15 14:25 | task-039 → blocked    | Waiting on task-038
2024-03-15 14:30 | task-038 → running    | Started by alice
```

### /lab meta [experiment-name]
View or edit metadata for an experiment.

#### Metadata Fields

Stored in `_meta.json` alongside each experiment:

```json
{
  "experiment_id": "YYYY-MM-DD-experiment-name",
  "title": "Human-readable title",
  "project": "project-name-or-id",
  "author": "alice",
  "created_at": "2024-03-10T09:00:00Z",
  "updated_at": "2024-03-15T16:00:00Z",
  "status": "running",
  "priority": "P1",
  "tags": ["ablation", "attention", "latency"],
  "linked_tasks": ["task-037", "task-038", "task-042"],
  "parent": "YYYY-MM-DD-parent-experiment",
  "children": [],
  "collections": ["my-paper-figures"],
  "paper_refs": ["arxiv:2401.12345"],
  "external_ids": ["wandb:alice/run-xyz", "mlflow:run-abc"],
  "notes": "Follow-up to the 2024-03-08 baseline study"
}
```

#### Subcommands

**`/lab meta get [experiment-name]`** — Display current metadata

**`/lab meta set <field> <value> [--experiment experiment-name]`** — Set a field

Example: `/lab meta set priority P0 --experiment my-exp`

**`/lab meta tag <tags...> [--experiment experiment-name]`** — Add tags

Tags are comma-separated or space-separated: `/lab meta tag ablation,latency`

**`/lab meta untag <tag> [--experiment experiment-name]`** — Remove a tag

**`/lab meta link <task-id> [--experiment experiment-name]`** — Link a task to this experiment

**`/lab meta add-external <service> <id> [--experiment experiment-name]`** — Link external IDs

Example: `/lab meta add-external wandb alice/run-xyz`

**`/lab meta set-parent <parent-id> [--experiment experiment-name]`** — Set parent experiment

**`/lab meta set-project <project-id> [--experiment experiment-name]`** — Set project grouping

**`/lab meta search [--tag TAG] [--project PROJECT] [--author AUTHOR] [--status STATUS]`** — Find experiments by metadata

### /lab collection [subcommand]
Organize experiments into named result collections for papers, reports, or thematic summaries.

A **collection** is a named group of experiments with shared context and a summary document.

#### Collection Index (_collections/_index.json)

```json
{
  "collections": {
    "my-paper-figures": {
      "name": "my-paper-figures",
      "description": "Experiments for Figure 3 in the NeurIPS submission",
      "created_at": "2024-03-10T09:00:00Z",
      "experiments": [
        "YYYY-MM-DD-baseline",
        "YYYY-MM-DD-ablation-attention",
        "YYYY-MM-DD-ablation-ffn"
      ],
      "tags": ["neurips", "figure-3"],
      "status": "in_progress"
    }
  }
}
```

#### Subcommands

**`/lab collection create <name>`** — Create a new collection

Interactive: name, description, initial experiments (optional), tags.

**`/lab collection add <collection-name> <experiment-name>`** — Add experiment to collection

**`/lab collection remove <collection-name> <experiment-name>`** — Remove experiment from collection

**`/lab collection list`** — Show all collections

```
Collections (.experiments/_collections/)
══════════════════════════════════════════════════════════════════
Name                  │ Experiments │ Status       │ Description
──────────────────────┼─────────────┼──────────────┼──────────────────────
my-paper-figures       │ 3           │ in_progress   │ Figure 3, NeurIPS
latency-benchmark      │ 7           │ completed     │ All latency benchmarks
ablation-series        │ 12          │ in_progress   │ Full ablation study
══════════════════════════════════════════════════════════════════
```

**`/lab collection view <collection-name>`** — Show collection details with experiment summaries

```
Collection: my-paper-figures
══════════════════════════════════════════════════════════════════
Description: Experiments for Figure 3 in the NeurIPS submission
Status: in_progress | Tags: neurips, figure-3
──────────────────────────────────────────────────────────────────
Experiments:
1. YYYY-MM-DD-baseline (completed)
   → Baseline accuracy: 94.5% ± 0.3%
2. YYYY-MM-DD-ablation-attention (completed)
   → Ablation without attention: 91.2% ± 0.4% (↓3.3%)
3. YYYY-MM-DD-ablation-ffn (running)
   → Currently at run 4/10
──────────────────────────────────────────────────────────────────
Completion: 2/3 experiments done
```

**`/lab collection summarize <collection-name>`** — Generate a cross-experiment summary

Reads results from all experiments in the collection and produces a unified summary:

```markdown
# Collection Summary: my-paper-figures

## Overview
- Experiments: 3
- Status: 2 completed, 1 in progress
- Coverage: baseline, -attention, -ffn

## Cross-Experiment Results

### Primary Metric (Accuracy %)
| Experiment            | Mean  | Std   | N   |
|-----------------------|-------|-------|-----|
| baseline              | 94.5% | 0.3%  | 10  |
| ablation-attention    | 91.2% | 0.4%  | 10  |
| ablation-ffn          | [pending]        | 4/10 |
| **Delta: attention**  | **-3.3%** | [p<0.001] |
| **Delta: ffn**        | [pending]        |       |

### Key Findings
1. Attention mechanism contributes 3.3% accuracy (p<0.001, Cohen's d=1.8)
2. FFN ablation in progress — preliminary trend suggests larger impact

## Open Items
- [ ] FFN ablation: 6 runs remaining
- [ ] Statistical power calculation pending full completion
```

**`/lab collection export <collection-name> [--format md|json|csv]`** — Export collection data

### /lab search <query>
Full-text and metadata search across all experiments.

Searches:
- Experiment names and descriptions
- design.md content
- run notes
- experiment metadata (tags, project, author)
- results.md summaries

```
$ /lab search "attention mechanism"

Found 3 experiments:
══════════════════════════════════════════════════════════════════
1. 2024-03-10-model-ablation (tagged: ablation, attention)
   → Baseline accuracy: 94.5%
   → Ablation without attention: 91.2% (-3.3%)
   → Status: completed | Project: latency-study
2. 2024-03-08-baseline (tagged: baseline)
   → Matches in: notes ("attention layer adds overhead")
   → Status: completed | Project: latency-study
3. 2024-02-20-attention-compare (tagged: attention)
   → Matches in: design.md ("compare scaled vs. linear attention")
   → Status: completed | Project: nlp-exploration
══════════════════════════════════════════════════════════════════
3 results | Searched: metadata, design, notes
```

Search options:
- `--tag TAG` — filter by tag
- `--project PROJECT` — filter by project
- `--author AUTHOR` — filter by author
- `--status STATUS` — filter by experiment status
- `--after DATE` / `--before DATE` — date range filter
- `--limit N` — max results (default 20)

## Workflows

### Standard Experiment Flow (with Auto-Review)
```
/lab init
   ↓
Update .experiments/roadmap.md ←── 记录计划中的实验分支/路线
   ↓
[🤖 AUTO: design review] ←── 自动省察触发
   ├── ⚠️ Critical issues → 暂停，要求修复
   └── ✅ Passed → 继续
   ↓
Pre-run reflection/check ←── 正式实验前用户可见检查
   ├── ❌ Do not start yet → 补齐配置/修复链路
   ├── ⚠️ Proceed with cautions → 记录风险后继续
   └── ✅ Proceed → 允许开跑
   ↓
Run experiments
   ↓
/lab run (记录每次运行)
   ↓
Update .experiments/roadmap.md ←── 同步当前实验进展
   ↓
达到里程碑 (25% / 50% / 75%)
   ↓
[🤖 AUTO: progress review] ←── 自动进度检查
   ├── ⚠️ 异常检测 → 警告提示
   └── ✅ On track → 继续
   ↓
完成所有运行
   ↓
[🤖 AUTO: data quality review] ←── 自动数据审查
   ↓
/lab analyze
   ↓
[🤖 AUTO: pre-report review] ←── 自动报告前检查
   ├── ⚠️ Critical → 阻止报告生成
   └── ✅ Passed → 允许生成
   ↓
/lab report
   ↓
Update .experiments/roadmap.md ←── 总结结果、结论和后续分支
   ↓
[🤖 AUTO: final review] ←── 自动最终审查
```

### Manual Override

即使启用自动省察，仍可手动触发深度审查：

```bash
/lab review design --deep       # 深度设计审查
/lab review data --expert       # 专家级数据分析
/lab review report --committee  # 委员会式全面审查
```

### Review Trigger Matrix

| 阶段 | 自动触发 | 手动触发 | 适用场景 |
|------|----------|----------|----------|
| 设计 | 创建后自动 | `/lab review design` | 所有实验 |
| 开跑前 | 每次正式运行前 | `/lab review pre-run` | 训练、benchmark、消融、长任务 |
| 进度 | 25/50/75/100% | `/lab review progress` | 长周期实验 |
| 数据 | 完成运行后 | `/lab review data` | 复杂分析 |
| 报告 | 生成前自动 | `/lab review report` | 发表前必审 |

### Ablation Study
```
/lab init model-ablation
  ↓
Design: List all components to ablate
  ↓
/lab run for each ablation variant
  ↓
/lab analyze --compare-baseline
```

### Benchmark Comparison
```
/lab init framework-benchmark
  ↓
Design: Define workloads and metrics
  ↓
/lab run for each (framework, workload) pair
  ↓
/lab analyze --rank
```

## Auto-Review Configuration (自动省察)

自动在关键节点触发审查，确保实验质量。

### Configuration File

创建 `.labrc.json` 在实验根目录：

```json
{
  "auto_review": {
    "enabled": true,
    "stages": {
      "design": {
        "enabled": true,
        "trigger": "after_init",
        "min_runs_required": 0
      },
      "pre_run": {
        "enabled": true,
        "trigger": "before_formal_run",
        "show_to_user": true,
        "block_on_unverified_critical_settings": true
      },
      "progress": {
        "enabled": true,
        "trigger": "on_milestone",
        "milestones": [0.25, 0.50, 0.75, 1.0],
        "min_runs_between_reviews": 3
      },
      "data": {
        "enabled": true,
        "trigger": "before_analyze",
        "conditions": ["complete_data", "anomalous_result"]
      },
      "report": {
        "enabled": true,
        "trigger": "before_report",
        "strict_mode": true
      }
    },
    "experts": {
      "methodologist": true,
      "statistician": true,
      "domain_expert": true,
      "reproducibility_auditor": true
    },
    "severity_threshold": "warning",
    "block_on_critical": true
  }
}
```

### Trigger Conditions

| 触发器 | 条件 | 动作 |
|--------|------|------|
| `after_init` | 设计文档创建后 | 自动审查设计 |
| `before_formal_run` | 启动正式实验、训练、benchmark 或消融前 | 用户可见的场景理解、参数、配置和链路检查 |
| `on_milestone` | 完成 25%/50%/75%/100% 计划运行 | 进度审查 |
| `before_analyze` | 执行分析前 | 数据质量审查 |
| `before_report` | 生成报告前 | 全面审查 |
| `anomalous_result` | 检测到异常值或与假设矛盾 | 紧急审查 |

### 自动审查工作流

```
/lab init
   ↓
[自动触发: design review]
   ↓
正式运行前
   ↓
[自动触发: pre-run reflection/check]
   ├── 关键配置无法验证 → 暂停并补齐
   └── 通过/带风险通过 → 记录判断
   ↓
运行实验
   ↓
达到里程碑 (25% → 50% → 75%)
   ↓
[自动触发: progress review]
   ├── 正常 → 继续
   └── 异常 → 警告/暂停
   ↓
完成所有运行
   ↓
[自动触发: data review]
   ↓
/lab analyze
   ↓
[自动触发: pre-report review]
   ↓
/lab report
```

### 审查结果存储

自动审查报告保存到：
```
experiments/[name]/reviews/
├── auto-design-2024-04-05.md      # 设计审查
├── auto-progress-2024-04-05-25.md  # 25% 进度审查
├── auto-progress-2024-04-05-50.md  # 50% 进度审查
├── auto-data-2024-04-05.md         # 数据审查
└── auto-report-2024-04-05.md       # 报告前审查
```

### 自动响应机制 (建设性协助)

| 验证项目 | 结果 | 自动动作 |
|----------|------|----------|
| 实现与设计一致 | ✅ 通过 | 记录确认，实验继续 |
| 实现与设计一致 | ❓ 有疑问 | 提供澄清问题，协助验证 |
| 假设可测试性 | ✅ 通过 | 记录确认，实验继续 |
| 假设表述 | ❓ 可优化 | 提供改进建议，继续 |
| 样本量 | ✅ 充足 | 记录确认，实验继续 |
| 样本量 | ℹ️ 较小 | 说明增加样本的收益，可选 |
| 检测到异常值 | ℹ️ 发现 | 提供可能解释，协助诊断 |
| 数据与假设不符 | ❓ 矛盾 | 协助分析原因（实现/数据/假设），提供排查清单 |
| 环境一致性 | ✅ 一致 | 记录确认，实验继续 |
| Git 未提交 | ℹ️ 提醒 | 建议记录状态，提供提交命令 |

### 自动省察决策流程

```
开始
  │
  ├─→ 验证实现正确性
  │     │
  │     ├─✅ 确认 ──→ 继续
  │     │
  │     └─❓ 不确定 ──→ 提供验证方法建议
  │                    │
  │                    └─→ 协助设计验证实验
  │
  ├─→ 验证假设合理性
  │     │
  │     ├─✅ 合理 ──→ 继续
  │     │
  │     └─❓ 可优化 ──→ 提供替代表述
  │
  └─→ 提供协助建议
        │
        └─→ 实验继续
```

### 静默模式

对于已知安全的实验，可禁用自动审查：

```bash
# 命令行禁用
/lab init --no-auto-review

# 或在 .labrc.json
{ "auto_review": { "enabled": false } }
```

## Best Practices

1. **Design before running**: Always create design.md first
2. **One variable at a time**: Isolate effects when possible
3. **Replication**: Minimum 3 runs per condition for reliability
4. **Documentation**: Record everything that might matter later
5. **Roadmap upkeep**: Keep `.experiments/roadmap.md` current after design, launch, analysis, report, or major decision changes
6. **Version control**: Experiments directory should be committed

## Data Integrity

- Never modify run-*.json after creation
- If a run is invalid, mark it in notes rather than deleting
- Include environment info (hardware, software versions) in design.md
- Hash or git commit reference for code being tested

## Automatic Data Validation

### /lab validate
Check data quality and flag issues:

```
Validation Checks:
├── Schema Validation
│   ├── Required fields present ✅
│   ├── Data types correct ✅
│   └── Timestamp format valid ✅
├── Completeness
│   ├── All conditions have runs ✅
│   ├── Minimum sample size met ⚠️ (2/3 runs for condition C)
│   └── Missing values flagged
├── Consistency
│   ├── Units consistent across runs ✅
│   ├── Parameter values in design range ✅
│   └── Timestamps monotonic ⚠️ (run-003 before run-002)
├── Outlier Detection
│   ├── Z-score > 3 flagged: run-004.latency
│   └── IQR outliers flagged: none
└── Reproducibility
    ├── Git commit recorded ✅
    ├── Environment hash consistent ✅
    └── Random seeds documented ⚠️ (seed missing for run-002)
```

### Validation Rules

| Check | Rule | Severity |
|-------|------|----------|
| Missing required field | JSON must contain run_id, timestamp, parameters, results | Error |
| Parameter out of range | Value must match design.md levels | Warning |
| Duplicate run_id | Must be unique | Error |
| Timestamp in future | Must be ≤ now | Error |
| Sample size < 3 | Minimum for statistical power | Warning |
| Outlier detected | Z > 3 or outside 1.5×IQR | Info |
| Git dirty | Uncommitted changes | Warning |

### Auto-validation on /lab run
Before accepting a new run:
1. Validate JSON schema
2. Check parameter values against design.md
3. Warn if same conditions already have 3+ runs
4. Flag potential outliers in real-time
5. Verify git status and record commit hash

## Reproducibility Check

### /lab reproduce <run-id>
Verify that an experiment can be reproduced:

```
Reproducibility Check for run-003:

Environment Comparison:
├── Hardware
│   ├── Original: Intel Xeon Gold 6248, NVIDIA A100
│   ├── Current:  Intel Xeon Silver 4214, NVIDIA A100
│   └── Status:   ⚠️ CPU different (may affect CPU-bound ops)
├── Software
│   ├── Original: CUDA 12.1, Python 3.10.12
│   ├── Current:  CUDA 12.2, Python 3.10.12
│   └── Status:   ⚠️ CUDA version mismatch
├── Code
│   ├── Original commit: a1b2c3d4
│   ├── Current commit:  a1b2c3d4
│   └── Status:   ✅ Exact match
└── Configuration
    ├── Random seed: 42 (recorded) ✅
    ├── Hyperparameters: match ✅
    └── Data version: v1.2.3 ✅

Reproducibility Score: 8/10
⚠️ Minor environment differences detected
→ Recommend: Document environment tolerance in report
```

### Reproducibility Requirements

| Component | Storage | Check Method |
|-----------|---------|--------------|
| Code | Git commit hash | `git rev-parse HEAD` |
| Dependencies | requirements.txt hash | `md5sum requirements.txt` |
| Random seed | Explicit value | Must be user-provided |
| Data | Version/path + hash | File checksum |
| Hardware | Auto-detected | Compare key specs |
| Environment | Key env vars | `env` subset |

### /lab reproduce-all
Check reproducibility of entire experiment:
- Environment drift across runs
- Git history divergence
- Seed consistency
- Hardware changes

Generates reproducibility report with confidence score.

## Project Maintenance (项目维护)

### .experiments/roadmap.md

Every project using experiment-lab should maintain `.experiments/roadmap.md` as the living project-level map. Create it if missing, and update it whenever an experiment is designed, launched, paused, completed, analyzed, reported, or when future priorities change.

The roadmap should stay concise and decision-oriented. It must include:

- **Past results and conclusions**: short summaries of completed experiments, key metrics, conclusions, and links to `results.md` / `report.md`.
- **Current experiments**: active or paused experiments, status, goal, current checkpoint/run state, blockers, and next action.
- **Future plan**: ordered next experiments, expected comparison/control, why each matters, and prerequisites.
- **Branches and decision tree**: alternative routes depending on outcomes, including stop/continue criteria where possible.
- **Open questions and risks**: unresolved assumptions, config risks, data/evaluation concerns, and items that need user or evidence confirmation.

Suggested skeleton:

```markdown
# Experiment Roadmap

## Past Results
| Experiment | Status | Key Result | Conclusion | Links |
|------------|--------|------------|------------|-------|

## Current Experiments
| Experiment | Goal | Status | Next Action | Risk/Blocker |
|------------|------|--------|-------------|--------------|

## Future Plan
| Priority | Experiment | Comparison | Rationale | Prerequisites |
|----------|------------|------------|-----------|---------------|

## Branches
- If [result/metric condition], then [next route].
- If [negative/ambiguous result], then [fallback or diagnostic].

## Open Questions
- [Question] — owner/status/evidence needed.
```

When reporting experiment progress to the user, mention whether the roadmap was updated. If it was not updated, state why.

### /lab sync-claude-md

自动更新项目根目录的 `CLAUDE.md`，同步实验项目信息。

**Updates to CLAUDE.md:**

```markdown
## Project Overview

### Active Experiments
| Experiment | Status | Progress | Last Updated |
|------------|--------|----------|--------------|
| layerscale-cifar10 | running | 10/18 runs | 2024-04-05 |
| attention-ablation | completed | 30/30 runs | 2024-03-28 |

### Experiment Details
- **Primary Location**: `.experiments/`
- **Design Docs**: `.experiments/*/design.md`
- **Raw Data**: `.experiments/*/runs/`
- **Results**: `.experiments/*/results.md`
- **Reports**: `.experiments/*/report.md`

### Quick Access
| Experiment | Design | Latest Run | Report |
|------------|--------|------------|--------|
| layerscale-cifar10 | [design](.experiments/2024-04-05-layerscale-cifar10-ablation/design.md) | [run-010](.experiments/.../runs/run-010.json) | [report](.experiments/.../report.md) |
```

**Usage:**
```bash
/lab sync-claude-md                    # Update CLAUDE.md with current experiment status
/lab sync-claude-md --add-links        # Add experiment detail links
/lab sync-claude-md --section "Name"   # Update specific section
```

### /lab tasks

维护实验任务队列和进度跟踪。

```bash
/lab tasks list                        # Show all pending/completed tasks
/lab tasks add "Run baseline-12L seed 45" --priority high --exp layerscale-cifar10
/lab tasks complete <task-id>
/lab tasks progress                    # Show overall progress across all experiments
```

**Task Queue Format** (`.experiments/_tasks/_queue.json`):
```json
{
  "tasks": [
    {
      "id": "task-001",
      "experiment": "layerscale-cifar10",
      "description": "Run baseline-12L with seed 45",
      "status": "pending",
      "priority": "high",
      "created": "2024-04-05T10:00:00Z",
      "due": "2024-04-06T18:00:00Z"
    }
  ],
  "summary": {
    "total": 18,
    "completed": 10,
    "pending": 8
  }
}
```

### /lab framework

维护项目的基本框架和结构。

```bash
/lab framework init                    # Initialize experiment framework in current project
/lab framework validate                # Validate framework structure
/lab framework upgrade                 # Upgrade to latest experiment-lab version
```

**Framework Structure:**
```
project-root/
├── CLAUDE.md                          # Updated by /lab sync-claude-md
├── .experiments/                      # Experiment data (auto-created)
│   ├── _tasks/                        # Task queue
│   ├── _collections/                  # Cross-experiment collections
│   └── YYYY-MM-DD-*/                  # Individual experiments
├── .labrc.json                        # Experiment-lab configuration
└── requirements-experiments.txt       # Experiment dependencies
```

### /lab toolchain

管理实验工具链。

```bash
/lab toolchain list                    # List available tools
/lab toolchain add python@3.10         # Add tool requirement
/lab toolchain add pytorch@2.1
/lab toolchain check                   # Verify all tools available
/lab toolchain env                     # Generate environment setup script
```

**Toolchain Record** (stored in experiment metadata):
```json
{
  "toolchain": {
    "python": "3.10.12",
    "pytorch": "2.1.0",
    "cuda": "12.1",
    "numpy": "1.24.0",
    "custom_tools": [
      {
        "name": "custom-benchmark",
        "version": "1.2.0",
        "source": "git@github.com:example/benchmark-tool.git"
      }
    ]
  }
}
```

### /lab info <experiment-name>

显示实验详细信息的查看地址。

```bash
/lab info layerscale-cifar10           # Show detailed experiment info
```

**Output:**
```
╔══════════════════════════════════════════════════════════════════╗
║  Experiment: layerscale-cifar10-ablation                         ║
╠══════════════════════════════════════════════════════════════════╣
║  📁 Location                                                       ║
║     .experiments/2024-04-05-layerscale-cifar10-ablation/          ║
╠══════════════════════════════════════════════════════════════════╣
║  📄 Documents                                                      ║
║     Design:   [design.md](.experiments/.../design.md)             ║
║     Results:  [results.md](.experiments/.../results.md)           ║
║     Report:   [report.md](.experiments/.../report.md)             ║
╠══════════════════════════════════════════════════════════════════╣
║  📊 Data                                                           ║
║     Raw runs:  [runs/](.experiments/.../runs/) (10 files)         ║
║     Reviews:   [reviews/](.experiments/.../reviews/) (2 files)    ║
║     Config:    [.labrc.json](.experiments/.../.labrc.json)        ║
╠══════════════════════════════════════════════════════════════════╣
║  🔗 Quick Access                                                   ║
║     Latest run:   run-010.json                                     ║
║     Best result:  run-006.json (93.28% acc)                       ║
║     Logs:         [logs/](.experiments/.../logs/)                 ║
╠══════════════════════════════════════════════════════════════════╣
║  📈 Status: 10/18 runs (56%) | Last updated: 2024-04-05T17:05:55Z  ║
╚══════════════════════════════════════════════════════════════════╝
```

### /lab dashboard

生成项目仪表盘概览。

```bash
/lab dashboard                         # Show project-wide experiment dashboard
/lab dashboard --html                  # Generate HTML dashboard
/lab dashboard --refresh               # Force refresh all data
```

**Dashboard Output:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Experiment Dashboard - Project: vision-research                 │
├─────────────────────────────────────────────────────────────────┤
│  Overall Progress                                                │
│  ████████████████████░░░░░░  67% (24/36 experiments complete)   │
│                                                                  │
│  Active Experiments (3)                                          │
│  ┌────────────────────────┬────────┬────────┬─────────────────┐ │
│  │ Name                   │ Status │ Runs   │ Last Activity   │ │
│  ├────────────────────────┼────────┼────────┼─────────────────┤ │
│  │ layerscale-cifar10     │ 🔥 Run │ 10/18  │ 2 hours ago     │ │
│  │ attention-v2           │ ⏸️  Pause│ 5/20   │ 1 day ago       │ │
│  │ optimizer-sweep        │ 🆕 Init│ 0/50   │ Just now        │ │
│  └────────────────────────┴────────┴────────┴─────────────────┘ │
│                                                                  │
│  Recently Completed (2)                                          │
│  • baseline-cifar10 - 2024-04-04 - [report](...)                 │
│  • data-aug-study   - 2024-04-03 - [report](...)                 │
│                                                                  │
│  📋 Task Queue: 8 pending | 3 due today                          │
└─────────────────────────────────────────────────────────────────┘
```

### Automated Maintenance

Enable automatic maintenance in `.labrc.json`:

```json
{
  "maintenance": {
    "auto_sync_claude_md": true,
    "sync_on": ["run_complete", "analysis_complete", "report_generated"],
    "task_reminders": true,
    "dashboard_refresh": "daily"
  }
}
```

**Auto-sync behavior:**
- After each `/lab run` → Update CLAUDE.md progress
- After `/lab analyze` → Update results section
- After `/lab report` → Mark experiment complete
- Daily → Refresh dashboard and task reminders
