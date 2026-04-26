#!/usr/bin/env python3
"""Lightweight sequential experiment queue for .experiments/_tasks/_queue.json."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path


TERMINAL = {"completed", "failed", "cancelled", "skipped"}
ACTIVE = {"launching", "running"}
WAITING = {"queued", "pending", "waiting"}
TZ = timezone(timedelta(hours=8))


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def paths(root: Path) -> tuple[Path, Path, Path]:
    tasks = root / ".experiments" / "_tasks"
    tasks.mkdir(parents=True, exist_ok=True)
    queue = tasks / "_queue.json"
    lock = tasks / "_queue.lock"
    exits = tasks / "_exits"
    exits.mkdir(parents=True, exist_ok=True)
    if not queue.exists():
        queue.write_text("[]\n", encoding="utf-8")
    return queue, lock, exits


@contextmanager
def locked_queue(root: Path):
    queue_path, lock_path, _ = paths(root)
    with lock_path.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            queue = json.loads(queue_path.read_text(encoding="utf-8") or "[]")
            yield queue
            tmp = queue_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(tmp, queue_path)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def append_note(item: dict, message: str) -> None:
    item.setdefault("notes", []).append({"timestamp": now(), "message": message})
    item["updated_at"] = now()


def find_task(queue: list[dict], task_id: str) -> dict:
    for item in queue:
        if item.get("task_id") == task_id:
            return item
    raise SystemExit(f"task_id not found: {task_id}")


def screen_exists(name: str) -> bool:
    if not name:
        return False
    proc = subprocess.run(["screen", "-ls"], text=True, capture_output=True, check=False)
    needle = f".{name}"
    return any(needle in line for line in proc.stdout.splitlines())


def set_status(root: Path, task_id: str, status: str, note: str = "") -> None:
    with locked_queue(root) as queue:
        item = find_task(queue, task_id)
        item["status"] = status
        item["updated_at"] = now()
        if status == "queued":
            item.setdefault("queued_at", now())
        elif status == "launching":
            item["launching_at"] = now()
        elif status == "running":
            item["started_at"] = now()
        elif status in TERMINAL:
            item["finished_at"] = now()
        if note:
            append_note(item, note)


def enqueue(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    with locked_queue(root) as queue:
        if any(item.get("task_id") == args.task_id for item in queue):
            raise SystemExit(f"task_id already exists: {args.task_id}")
        item = {
            "task_id": args.task_id,
            "status": "queued",
            "created_at": now(),
            "queued_at": now(),
            "priority": args.priority,
            "command": args.command,
            "screen": args.screen,
            "log": args.log,
        }
        optional = {
            "experiment": args.experiment,
            "run_id": args.run_id,
            "objective": args.objective,
            "depends_on_screen": args.depends_on_screen,
        }
        item.update({k: v for k, v in optional.items() if v})
        append_note(item, "Enqueued by lab_queue.")
        queue.append(item)
    print(f"queued {args.task_id}")


def status(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    queue_path, _, _ = paths(root)
    queue = json.loads(queue_path.read_text(encoding="utf-8") or "[]")
    if not queue:
        print("queue empty")
        return
    for item in queue:
        fields = [
            item.get("task_id", ""),
            item.get("status", ""),
            f"screen={item.get('screen', '')}",
            f"log={item.get('log', '')}",
        ]
        dep = item.get("depends_on_screen")
        if dep:
            fields.append(f"depends_on={dep}")
        print(" | ".join(fields))


def task_exit_path(root: Path, task_id: str) -> Path:
    _, _, exits = paths(root)
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in task_id)
    return exits / f"{safe}.exitcode"


def run_task(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    with locked_queue(root) as queue:
        item = find_task(queue, args.task_id)
        command = item["command"]
        log_path = root / item.get("log", f"logs/{args.task_id}.log")
        item["status"] = "running"
        item["started_at"] = now()
        append_note(item, "Task command started inside screen.")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", buffering=1) as log:
        log.write(f"\n===== lab_queue start {now()} task={args.task_id} =====\n")
        rc = subprocess.run(command, shell=True, cwd=root, executable="/bin/bash", stdout=log, stderr=subprocess.STDOUT).returncode
        log.write(f"===== lab_queue end {now()} task={args.task_id} exit={rc} =====\n")

    task_exit_path(root, args.task_id).write_text(str(rc), encoding="utf-8")
    if rc == 0:
        set_status(root, args.task_id, "completed", f"Task completed with exit code {rc}.")
    else:
        set_status(root, args.task_id, "failed", f"Task failed with exit code {rc}.")
    return rc


def first_runnable(queue: list[dict]) -> dict | None:
    for item in queue:
        if item.get("status") not in WAITING:
            continue
        dep = item.get("depends_on_screen")
        if dep and screen_exists(dep):
            continue
        return item
    return None


def sync_disappeared_running(root: Path, queue: list[dict], grace_seconds: int = 30) -> None:
    for item in queue:
        if item.get("status") not in ACTIVE:
            continue
        screen = item.get("screen", "")
        if screen and screen_exists(screen):
            continue
        exit_path = task_exit_path(root, item.get("task_id", ""))
        if exit_path.exists():
            rc_text = exit_path.read_text(encoding="utf-8").strip()
            if rc_text == "0":
                item["status"] = "completed"
                append_note(item, "Worker observed screen exit and exit code 0.")
            else:
                item["status"] = "failed"
                append_note(item, f"Worker observed screen exit and exit code {rc_text}.")
            item.pop("screen_missing_since", None)
        else:
            missing_since = item.get("screen_missing_since")
            if not missing_since:
                item["screen_missing_since"] = now()
                append_note(item, "Screen disappeared; waiting briefly for exit code file.")
                continue
            elapsed = (datetime.now(TZ) - parse_time(missing_since)).total_seconds()
            if elapsed < grace_seconds:
                continue
            item["status"] = "failed"
            item.pop("screen_missing_since", None)
            append_note(item, "Screen disappeared before an exit code was recorded.")
        if item.get("status") in TERMINAL:
            item["finished_at"] = now()


def launch_task(root: Path, task_id: str) -> None:
    script = Path(__file__).resolve()
    with locked_queue(root) as queue:
        item = find_task(queue, task_id)
        screen = item["screen"]
        if screen_exists(screen):
            item["status"] = "running"
            append_note(item, "Screen already exists; worker will monitor it.")
            return
        item["status"] = "launching"
        item["launching_at"] = now()
        append_note(item, "Worker launching screen.")

    cmd = [
        "screen",
        "-dmS",
        screen,
        sys.executable,
        str(script),
        "run-task",
        "--root",
        str(root),
        "--task-id",
        task_id,
    ]
    subprocess.run(cmd, check=True)
    time.sleep(2)
    if not screen_exists(screen):
        with locked_queue(root) as queue:
            item = find_task(queue, task_id)
            if item.get("status") in TERMINAL or task_exit_path(root, task_id).exists():
                return
        set_status(root, task_id, "failed", "screen -dmS returned but target screen was not found.")


def worker(args: argparse.Namespace) -> None:
    root = Path(args.root).resolve()
    print(f"{now()} lab_queue worker started root={root}", flush=True)
    while True:
        with locked_queue(root) as queue:
            sync_disappeared_running(root, queue)
            active = any(item.get("status") in ACTIVE for item in queue)
            task = None if active else first_runnable(queue)
            task_id = task.get("task_id") if task else None

        if task_id:
            print(f"{now()} launching {task_id}", flush=True)
            launch_task(root, task_id)
        elif args.once:
            print(f"{now()} no runnable task; exiting --once worker", flush=True)
            return
        else:
            time.sleep(args.poll_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=".", help="Project root containing .experiments/")

    p = sub.add_parser("enqueue", parents=[common])
    p.add_argument("--task-id", required=True)
    p.add_argument("--command", required=True)
    p.add_argument("--screen", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--experiment")
    p.add_argument("--run-id")
    p.add_argument("--objective")
    p.add_argument("--depends-on-screen")
    p.add_argument("--priority", default="normal")
    p.set_defaults(func=enqueue)

    p = sub.add_parser("status", parents=[common])
    p.set_defaults(func=status)

    p = sub.add_parser("worker", parents=[common])
    p.add_argument("--poll-seconds", type=int, default=60)
    p.add_argument("--once", action="store_true")
    p.set_defaults(func=worker)

    p = sub.add_parser("run-task", parents=[common])
    p.add_argument("--task-id", required=True)
    p.set_defaults(func=run_task)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = args.func(args)
    return int(result or 0)


if __name__ == "__main__":
    raise SystemExit(main())
