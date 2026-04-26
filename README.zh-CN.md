# Experiment Lab

[English README](README.md)

Experiment Lab 是一个可安装的 Python 包，用于分发 `experiment-lab` Codex skill 以及配套的实验管理脚本。

它面向需要长期运行实验、训练任务、benchmark、消融实验和结果记录的研发场景。当前内置的核心工具是 `lab-queue`：一个轻量级单机顺序队列，用来避免多个实验任务同时抢占同一台机器、同一批 GPU 或同一组工作目录。

仓库地址：

```text
https://github.com/lz59970062/experiment-lab.git
```

## 为什么需要这个包

Codex skill 里经常会包含脚本、模板或辅助文件。如果直接用 skill 目录里的脚本，命令往往会依赖本机路径，例如：

```text
/home/user/.codex/skills/experiment-lab/scripts/lab_queue.py
```

这种方式在当前机器上可用，但复制到其他机器、发布到 GitHub、安装到虚拟环境或给其他用户使用时容易出问题。

Experiment Lab 把这些问题拆开处理：

- `SKILL.md` 继续作为 Codex skill 的入口文件。
- Python 脚本放进 `experiment_lab` 包内。
- 命令行工具通过稳定入口暴露，例如 `lab-queue`。
- 包内文件可以通过 `experiment-lab-paths` 定位，不依赖本地 skill 路径。
- 每个项目自己的实验队列状态仍然保存在项目目录的 `.experiments/` 下。

## 主要功能

- 支持从 GitHub 直接 `pip install`。
- 使用 `lab-queue` 管理实验任务，不需要硬编码 `~/.codex/skills/...` 路径。
- 使用 `experiment-lab-paths` 查看安装后的包资源路径。
- 每个项目启动一个 worker，按顺序运行队列任务。
- 记录任务状态、日志路径、screen 会话名、依赖关系和退出码。
- 保留 `scripts/lab_queue.py`，未安装包时也可以从源码目录直接运行。

## 适用场景

- 在共享服务器上排队运行多个模型训练任务。
- 避免多个高负载实验同时占用同一张 GPU 或同一台机器。
- 给每次实验明确记录命令、日志、screen 名称、项目根目录和输出位置。
- 把 Codex skill 打包成可安装、可版本化、可迁移的 GitHub 仓库。
- 在多台机器上复用同一套实验管理工具。

## 快速开始

从 GitHub 直接安装：

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

验证安装：

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-paths --skill-md
```

在任意实验项目中查看队列：

```bash
lab-queue status --root /path/to/project
```

如果队列文件还不存在，工具会在目标项目下创建：

```text
/path/to/project/.experiments/_tasks/
```

## 包含内容

```text
experiment-lab/
├── SKILL.md                         # Codex skill 源文件
├── scripts/
│   └── lab_queue.py                 # 源码目录直接运行的兼容包装器
├── src/
│   └── experiment_lab/
│       ├── SKILL.md                 # 打包进 Python 包的资源文件
│       ├── lab_queue.py             # 队列实现
│       ├── resources.py             # 资源路径定位工具
│       ├── __init__.py
│       └── __main__.py
├── pyproject.toml
├── README.md
└── README.zh-CN.md
```

安装后提供三个命令：

```text
lab-queue              # 实验任务队列工具
experiment-lab-paths   # 打印安装后的包资源路径
experiment-lab-install-skill # 复制 SKILL.md 到本机 Codex/Claude skill 目录
```

## 安装方式

### 方式 1：从 GitHub 安装

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

升级到最新提交：

```bash
python -m pip install --upgrade --force-reinstall git+https://github.com/lz59970062/experiment-lab.git
```

### 方式 2：clone 后安装

```bash
git clone https://github.com/lz59970062/experiment-lab.git
cd experiment-lab
python -m pip install .
```

### 方式 3：开发模式安装

如果你希望修改本地代码后立刻生效，使用 editable install：

```bash
git clone https://github.com/lz59970062/experiment-lab.git
cd experiment-lab
python -m pip install -e .
```

### 方式 4：从已有本地目录安装

```bash
python -m pip install -e /path/to/experiment-lab
```

验证命令是否可用：

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-install-skill --help
```

## 完整使用流程

### 1. 安装包

```bash
python -m pip install git+https://github.com/lz59970062/experiment-lab.git
```

### 2. 确认命令入口

```bash
lab-queue --help
experiment-lab-paths
experiment-lab-install-skill --help
```

预期效果：

```text
lab-queue --help                # 显示 enqueue/status/worker/run-task 子命令
experiment-lab-paths            # 打印 package_root 和 skill_md 路径
experiment-lab-paths --skill-md # 只打印包内 SKILL.md 路径
```

### 2.1. 自动安装 Agent Skill 文件

把包内置的 `SKILL.md` 同时写入 Codex 和 Claude 的默认 skill 目录：

```bash
experiment-lab-install-skill --force
```

默认写入路径：

```text
~/.codex/skills/experiment-lab/SKILL.md
~/.claude/skills/experiment-lab/SKILL.md
```

只安装其中一个：

```bash
experiment-lab-install-skill --target codex --force
experiment-lab-install-skill --target claude --force
```

只预览，不写文件：

```bash
experiment-lab-install-skill --dry-run
```

打印当前 Python 环境对应的安装命令：

```bash
experiment-lab-install-skill --print-install-command
```

复制出的 `SKILL.md` 会包含 Python 包安装提示。安装器会根据运行它的 Python 环境生成命令；如果检测到 `uv`，优先提示 `uv pip install --python ...`，否则提示 `python -m pip install ...`。

### 3. 选择项目根目录

项目根目录是你希望保存实验记录和队列状态的仓库或工作目录：

```bash
cd /path/to/project
```

队列文件会创建在：

```text
.experiments/_tasks/
```

### 4. 查看队列状态

```bash
lab-queue status --root .
```

如果没有任务，会输出：

```text
queue empty
```

### 5. 加入一个任务

```bash
lab-queue enqueue \
  --root . \
  --task-id 2026-04-26-example-train \
  --screen train_example_20260426 \
  --log logs/train_example_20260426.log \
  --command 'python train.py --gpu 2'
```

这一步只会把任务写入队列。除非 worker 已经在运行，否则训练命令不会立刻启动。

### 6. 启动一个队列 worker

每个项目队列通常只启动一个 worker：

```bash
screen -dmS lab_queue_20260426 bash -lc \
  'lab-queue worker --root /path/to/project --poll-seconds 60'
```

worker 会按顺序启动队列中的任务，每个任务会运行在自己配置的 `screen` 会话里。

### 7. 查看运行状态

```bash
lab-queue status --root /path/to/project
screen -ls
```

任务日志路径相对于项目根目录，例如：

```text
/path/to/project/logs/train_example_20260426.log
```

### 8. 加入依赖后续任务

如果一个任务需要等待已有 screen 结束后再启动：

```bash
lab-queue enqueue \
  --root /path/to/project \
  --task-id 2026-04-26-followup-train \
  --screen train_followup_20260426 \
  --log logs/train_followup_20260426.log \
  --depends-on-screen train_current_20260426 \
  --command 'python train.py --gpu 3'
```

只要 `screen -ls` 里还能看到 `train_current_20260426`，worker 就不会启动这个任务。

### 9. 记录实验上下文

正式实验建议至少记录：

```text
enqueue 命令
worker screen 名称
任务 screen 名称
训练命令
日志路径
git commit
关键配置文件路径
预期指标或输出文件
```

这些信息建议写入实验目录的 `report.md` 或 run notes。

## 包内资源路径

安装后不要再依赖 skill checkout 的本地路径。使用下面命令定位资源：

```bash
experiment-lab-paths
experiment-lab-paths --skill-md
```

Python 中可以这样使用：

```python
from experiment_lab.resources import package_root, skill_md

print(package_root())
print(skill_md())
```

`SKILL.md` 已经作为 package data 打进包里，所以即使包安装到虚拟环境或 site-packages 中，也可以定位到它。

## Codex Skill 安装

如果已经安装了 Python 包，直接运行：

```bash
experiment-lab-install-skill --target codex --force
```

如果希望以 Git checkout 的方式管理 skill，把仓库 clone 到 Codex skills 目录：

```bash
cd ~/.codex/skills
git clone https://github.com/lz59970062/experiment-lab.git experiment-lab
```

skill 入口文件是：

```text
~/.codex/skills/experiment-lab/SKILL.md
```

同时也可以把它作为 Python 包安装：

```bash
python -m pip install -e ~/.codex/skills/experiment-lab
```

这样可以同时获得：

```text
Codex 通过 SKILL.md 激活 skill
命令行通过 Python 包提供 lab-queue 等工具
```

## Claude Skill 安装

如果已经安装了 Python 包，直接运行：

```bash
experiment-lab-install-skill --target claude --force
```

默认目标路径：

```text
~/.claude/skills/experiment-lab/SKILL.md
```

同时安装 Codex 和 Claude：

```bash
experiment-lab-install-skill --force
```

## 队列状态文件

`lab-queue` 的状态保存在目标项目里，而不是安装包里：

```text
/path/to/project/.experiments/_tasks/_queue.json
/path/to/project/.experiments/_tasks/_queue.lock
/path/to/project/.experiments/_tasks/_exits/
```

任务状态流转：

```text
queued -> launching -> running -> completed
queued -> launching -> running -> failed
queued -> cancelled
```

最小任务结构：

```json
{
  "task_id": "2026-04-26-example-train",
  "status": "queued",
  "command": "python train.py --gpu 2",
  "screen": "train_example_20260426",
  "log": "logs/train_example_20260426.log"
}
```

`enqueue` 支持的可选字段：

```text
--experiment
--run-id
--objective
--depends-on-screen
--priority
```

## 源码目录直接运行

如果还没有安装包，也可以在源码目录中运行兼容脚本：

```bash
python scripts/lab_queue.py status --root /path/to/project
```

该脚本会把本地 `src/` 加入 `sys.path`，然后调用：

```text
experiment_lab.lab_queue:main
```

## 开发检查

语法检查：

```bash
python -m compileall src scripts
```

源码模式 smoke test：

```bash
python scripts/lab_queue.py status --root /tmp/experiment-lab-smoke
PYTHONPATH=src python -m experiment_lab --skill-md
PYTHONPATH=src python -m experiment_lab.lab_queue status --root /tmp/experiment-lab-smoke
```

构建和安装 smoke test：

```bash
python -m pip install . --target /tmp/experiment-lab-install --no-deps --force-reinstall
PYTHONPATH=/tmp/experiment-lab-install /tmp/experiment-lab-install/bin/experiment-lab-paths --skill-md
PYTHONPATH=/tmp/experiment-lab-install /tmp/experiment-lab-install/bin/lab-queue status --root /tmp/experiment-lab-smoke
```

正常安装到虚拟环境时不需要手动设置 `PYTHONPATH`。
