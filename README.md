# Experiment Lab

[中文文档](README.zh-CN.md)

Experiment Lab is an installable Python package for the `experiment-lab` Codex skill and its helper scripts.

It is designed for research and engineering workflows where experiments need to be planned, queued, recorded, and reviewed consistently. The first bundled helper is a lightweight single-machine queue for long-running experiment jobs, especially training or benchmark tasks that should run sequentially instead of competing for the same GPU or workstation resources.

The package exists mainly to remove hard-coded local paths such as:

```text
/home/user/.codex/skills/experiment-lab/scripts/lab_queue.py
```

After installation, callers can use stable command-line entry points and package resource helpers instead.

## Why This Exists

When a Codex skill contains scripts or templates, direct usage often depends on the local skill checkout path. That works on one machine, but it becomes fragile when the skill is copied, installed into a virtual environment, used by another user, or published as a GitHub repository.

Experiment Lab separates these concerns:

- `SKILL.md` remains usable as a Codex skill entry file.
- Python helpers are packaged under `experiment_lab`.
- Command-line tools are exposed as stable console scripts.
- Bundled files such as `SKILL.md` can be located through package resources.
- Experiment queue state stays in each target project under `.experiments/`.

## Main Features

- Install directly from GitHub with `pip`.
- Use `lab-queue` without hard-coding `~/.codex/skills/...` paths.
- Locate bundled package resources with `experiment-lab-paths`.
- Run one queue worker per project to launch tasks sequentially.
- Track queue state, logs, screen sessions, dependencies, and exit codes.
- Keep direct checkout usage working through `scripts/lab_queue.py`.

## Typical Use Cases

- Queue multiple model training jobs on a shared machine.
- Avoid starting two GPU-heavy experiment runs at the same time.
- Record exactly which command, log file, screen session, and project root belong to each run.
- Package a Codex skill so it can be installed and reused outside one local `~/.codex/skills` directory.
- Keep experiment helpers versioned in GitHub and installable across machines.

Repository:

```text
https://github.com/lz59970062/experiment-lab.git
```

## Quick Start

Install directly from GitHub:

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

Verify the installation:

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-paths --skill-md
```

Use the queue helper in any experiment project:

```bash
lab-queue status --root /path/to/project
```

This creates queue state under the target project when needed:

```text
/path/to/project/.experiments/_tasks/
```

## What Is Included

```text
experiment-lab/
├── SKILL.md                         # Codex skill source, kept for direct skill use
├── scripts/
│   └── lab_queue.py                 # Compatibility wrapper for direct checkout usage
├── src/
│   └── experiment_lab/
│       ├── SKILL.md                 # Bundled package resource
│       ├── lab_queue.py             # Queue implementation
│       ├── resources.py             # Resource path helper
│       ├── __init__.py
│       └── __main__.py
├── pyproject.toml
├── README.md
└── README.zh-CN.md
```

Installed console commands:

```text
lab-queue              # Experiment task queue helper
experiment-lab-paths   # Print installed package resource paths
experiment-lab-install-skill # Copy SKILL.md into local Codex/Claude skill directories
```

## Install

### Option 1: Install From GitHub

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

Upgrade to the latest commit:

```bash
python -m pip install --upgrade --force-reinstall git+https://github.com/lz59970062/experiment-lab.git
```

### Option 2: Clone Then Install

```bash
git clone https://github.com/lz59970062/experiment-lab.git
cd experiment-lab
python -m pip install .
```

### Option 3: Editable Development Install

Use this when you want local code changes to take effect without reinstalling:

```bash
git clone https://github.com/lz59970062/experiment-lab.git
cd experiment-lab
python -m pip install -e .
```

### Option 4: Install From An Existing Local Checkout

```bash
python -m pip install -e /path/to/experiment-lab
```

Verify the commands are available:

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-install-skill --help
```

## Full Usage Flow

### 1. Install The Package

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

### 2. Confirm Installed Commands

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-install-skill --help
```

Expected behavior:

```text
lab-queue --help              # shows enqueue/status/worker/run-task subcommands
experiment-lab-paths          # prints installed package_root and skill_md paths
experiment-lab-paths --skill-md # prints only bundled SKILL.md
```

### 2.1. Install The Skill Files For Agents

Install the bundled `SKILL.md` into both default agent skill directories:

```bash
experiment-lab-install-skill --force
```

Default output paths:

```text
~/.codex/skills/experiment-lab/SKILL.md
~/.claude/skills/experiment-lab/SKILL.md
```

Install only one target:

```bash
experiment-lab-install-skill --target codex --force
experiment-lab-install-skill --target claude --force
```

Preview writes without changing files:

```bash
experiment-lab-install-skill --dry-run
```

Print the install command detected for the current Python environment:

```bash
experiment-lab-install-skill --print-install-command
```

The copied `SKILL.md` includes a Python package installation hint using the interpreter that ran `experiment-lab-install-skill`. If `uv` is available, the generated hint prefers `uv pip install --python ...`; otherwise it uses `python -m pip install ...`.

### 3. Pick A Project Root

The project root is the repository or working directory where experiment records should live:

```bash
cd /path/to/project
```

All queue files will be created under:

```text
.experiments/_tasks/
```

### 4. Check Queue Status

```bash
lab-queue status --root .
```

If there are no tasks yet, it prints:

```text
queue empty
```

### 5. Enqueue A Task

```bash
lab-queue enqueue \
  --root . \
  --task-id 2026-04-26-example-train \
  --screen train_example_20260426 \
  --log logs/train_example_20260426.log \
  --command 'python train.py --gpu 2'
```

This only records the task in the queue. It does not immediately run the training command unless a worker is active.

### 6. Start One Queue Worker

Run one worker per project queue:

```bash
screen -dmS lab_queue_20260426 bash -lc \
  'lab-queue worker --root /path/to/project --poll-seconds 60'
```

The worker launches queued tasks one at a time in their configured `screen` sessions.

### 7. Inspect Running State

```bash
lab-queue status --root /path/to/project
screen -ls
```

Task logs are written relative to the project root, for example:

```text
/path/to/project/logs/train_example_20260426.log
```

### 8. Queue Follow-Up Tasks

To wait for an existing screen before starting the task:

```bash
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-followup-train \
  --screen train_followup_20260426 \
  --log logs/train_followup_20260426.log \
  --depends-on-screen train_current_20260426 \
  --command 'python train.py --gpu 3'
```

The worker will not start this task until `train_current_20260426` disappears from `screen -ls`.

### 9. Record The Experiment Context

For formal experiments, record at least:

```text
enqueue command
worker screen name
target task screen name
training command
log path
git commit
important config paths
expected metric/output files
```

This should go in the experiment `report.md` or run notes.

## Resource Path Design

Do not depend on the skill checkout path after installation. Use one of these instead:

```bash
experiment-lab-paths
experiment-lab-paths --skill-md
```

From Python:

```python
from experiment_lab.resources import package_root, skill_md

print(package_root())
print(skill_md())
```

`SKILL.md` is included as package data, so it can be located even when the package is installed into a virtual environment or site-packages directory.

## Codex Skill Installation

If you already installed the Python package, use the installer command:

```bash
experiment-lab-install-skill --target codex --force
```

If you want to manage the skill as a Git checkout instead, place or clone the repository under your Codex skills directory:

```bash
cd ~/.codex/skills
git clone https://github.com/lz59970062/experiment-lab.git experiment-lab
```

The skill entry file is:

```text
~/.codex/skills/experiment-lab/SKILL.md
```

The Python package can still be installed separately:

```bash
python -m pip install -e ~/.codex/skills/experiment-lab
```

This gives you both:

```text
Codex skill activation from SKILL.md
CLI commands from the Python package
```

## Claude Skill Installation

If you already installed the Python package, use:

```bash
experiment-lab-install-skill --target claude --force
```

Default target:

```text
~/.claude/skills/experiment-lab/SKILL.md
```

To install both Codex and Claude skill files in one command:

```bash
experiment-lab-install-skill --force
```

## Queue Usage

`lab-queue` manages a single-machine sequential queue for experiment tasks that should not run concurrently.

Queue state is stored in the target project, not in the installed package:

```text
/path/to/project/.experiments/_tasks/_queue.json
/path/to/project/.experiments/_tasks/_queue.lock
/path/to/project/.experiments/_tasks/_exits/
```

Enqueue a task:

```bash
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-example-train \
  --screen train_example_20260426 \
  --log logs/train_example_20260426.log \
  --command 'python train.py --gpu 2'
```

Enqueue a task that waits for an existing screen session to finish:

```bash
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-followup-train \
  --screen train_followup_20260426 \
  --log logs/train_followup_20260426.log \
  --depends-on-screen train_current_20260426 \
  --command 'python train.py --gpu 3'
```

Start one queue worker:

```bash
screen -dmS lab_queue_20260426 bash -lc \
  'lab-queue worker --root /path/to/project --poll-seconds 60'
```

Inspect status:

```bash
lab-queue status --root /path/to/project
```

Run the worker once and exit if nothing is runnable:

```bash
lab-queue worker --root /path/to/project --once
```

## Task Model

Minimal queued task:

```json
{
  "task_id": "2026-04-26-example-train",
  "status": "queued",
  "command": "python train.py --gpu 2",
  "screen": "train_example_20260426",
  "log": "logs/train_example_20260426.log"
}
```

Optional fields supported by `enqueue`:

```text
--experiment
--run-id
--objective
--depends-on-screen
--priority
```

Status lifecycle:

```text
queued -> launching -> running -> completed
queued -> launching -> running -> failed
queued -> cancelled
```

## Direct Checkout Usage

If the package has not been installed, the compatibility wrapper still works from this repository:

```bash
python scripts/lab_queue.py status --root /path/to/project
```

The wrapper adds the local `src/` directory to `sys.path` and then calls:

```text
experiment_lab.lab_queue:main
```

This keeps old skill-style usage working while making installed usage path-independent.

## Development Checks

Run syntax checks:

```bash
python -m compileall src scripts
```

Smoke test local source execution:

```bash
python scripts/lab_queue.py status --root /tmp/experiment-lab-smoke
PYTHONPATH=src python -m experiment_lab --skill-md
PYTHONPATH=src python -m experiment_lab.lab_queue status --root /tmp/experiment-lab-smoke
```

Build/install smoke test:

```bash
python -m pip install . --target /tmp/experiment-lab-install --no-deps --force-reinstall
PYTHONPATH=/tmp/experiment-lab-install /tmp/experiment-lab-install/bin/experiment-lab-paths --skill-md
PYTHONPATH=/tmp/experiment-lab-install /tmp/experiment-lab-install/bin/lab-queue status --root /tmp/experiment-lab-smoke
```

When installing normally into a virtual environment, `PYTHONPATH` is not needed.
