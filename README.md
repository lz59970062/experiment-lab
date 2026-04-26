# Experiment Lab

Experiment Lab is an installable Python package for the `experiment-lab` Codex skill and its helper scripts.

The package exists mainly to remove hard-coded local paths such as:

```text
/home/user/.codex/skills/experiment-lab/scripts/lab_queue.py
```

After installation, callers can use stable command-line entry points and package resource helpers instead.

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
└── README.md
```

Installed console commands:

```text
lab-queue              # Experiment task queue helper
experiment-lab-paths   # Print installed package resource paths
```

## Install

Install from a local checkout:

```bash
python -m pip install /path/to/experiment-lab
```

Install in editable mode while developing:

```bash
python -m pip install -e /path/to/experiment-lab
```

Verify the commands are available:

```bash
lab-queue --help
experiment-lab-paths
```

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
