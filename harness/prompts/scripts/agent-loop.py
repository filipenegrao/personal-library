#!/usr/bin/env python3
"""
Agent Harness — file-based orchestration loop.

This script is intentionally conservative:
- It never commits or pushes.
- It can run in manual mode, generating prompts only.
- In builder mode, it can invoke a configured CLI builder and capture output.
- QA/security can be kept manual or enabled in config.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

ROOT = Path.cwd()
HARNESS_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = HARNESS_DIR / "agent-harness.config.json"
EXAMPLE_CONFIG_PATH = HARNESS_DIR / "agent-harness.config.example.json"

BuilderKind = Literal["frontend", "backend"]
Mode = Literal["manual", "builder", "full"]


@dataclass
class AgentConfig:
    enabled: bool
    command: str
    input: str = "stdin"


DEFAULT_CONFIG: dict[str, Any] = {
    "max_turns": 3,
    "run_dir": ".harness/runs",
    "diff_paths": ["."],
    "diff_exclude": [".harness/runs", "harness/prompts/agent-harness.config.json"],
    "routing": {
        "frontend_keywords": [
            "frontend",
            "ui",
            "page",
            "component",
            "css",
            "tailwind",
            "next",
            "react",
            "login",
        ],
        "backend_keywords": [
            "api",
            "backend",
            "endpoint",
            "database",
            "model",
            "schema",
            "migration",
            "export",
            "import",
        ],
    },
    "agents": {
        "builder_backend": {"enabled": False, "command": "", "input": "stdin"},
        "builder_frontend": {"enabled": False, "command": "", "input": "stdin"},
        "qa": {"enabled": False, "command": "", "input": "stdin"},
        "security": {"enabled": False, "command": "", "input": "stdin"},
    },
}


def load_config() -> dict[str, Any]:
    path = CONFIG_PATH if CONFIG_PATH.exists() else EXAMPLE_CONFIG_PATH
    if not path.exists():
        return DEFAULT_CONFIG
    with path.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    return merge_config(DEFAULT_CONFIG, loaded)


def merge_config(default: dict[str, Any], loaded: dict[str, Any]) -> dict[str, Any]:
    merged = dict(default)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_template(name: str) -> str:
    path = HARNESS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_shell(command: str, input_text: str | None = None) -> tuple[int, str]:
    """Run a shell command, optionally piping text to stdin."""
    proc = subprocess.run(
        command,
        input=input_text,
        text=True,
        shell=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout


def run_agent(command: str, prompt: str, prompt_file: Path, input_mode: str) -> tuple[int, str]:
    root = str(ROOT)
    substitutions = {
        "root": shlex.quote(root),
        "prompt_file": shlex.quote(str(prompt_file)),
        "prompt": shlex.quote(prompt),
    }
    prepared = command.format(**substitutions)
    stdin = prompt if input_mode == "stdin" and "{prompt}" not in command else None
    return run_shell(prepared, input_text=stdin)


def git_diff(config: dict[str, Any]) -> str:
    paths = config.get("diff_paths", ["."])
    excludes = config.get("diff_exclude", [])
    pathspecs = [shlex.quote(str(path)) for path in paths]
    pathspecs += [shlex.quote(f":!{path}") for path in excludes]
    code, out = run_shell("git diff -- " + " ".join(pathspecs))
    if code != 0:
        return f"[git diff failed]\n{out}"
    return out


def git_status() -> str:
    code, out = run_shell("git status --short")
    if code != 0:
        return f"[git status failed]\n{out}"
    return out


def choose_builder(task: str, config: dict[str, Any], explicit: str | None) -> BuilderKind:
    if explicit in {"frontend", "backend"}:
        return explicit  # type: ignore[return-value]

    routing = config.get("routing", {})
    text = task.lower()
    frontend_hits = sum(1 for k in routing.get("frontend_keywords", []) if k.lower() in text)
    backend_hits = sum(1 for k in routing.get("backend_keywords", []) if k.lower() in text)
    return "frontend" if frontend_hits >= backend_hits else "backend"


def render_builder_prompt(task: str, builder_kind: BuilderKind, attempt: int, prior_feedback: str = "") -> str:
    base = read_template("builder.md")
    return f"""{base}

---

# Current task

Task: {task}

Builder profile: {builder_kind}
Attempt: {attempt}

## Additional operating rules for this harness run

- Work only in the current repository.
- Do not commit, push, or create pull requests.
- Prefer the smallest coherent diff that satisfies the task.
- At the end, provide:
  1. Summary of changes
  2. Files changed
  3. Commands/sensors run and results
  4. Any blocker or assumption

{f"## Prior feedback to address\n\n{prior_feedback}" if prior_feedback else ""}
"""


def render_qa_prompt(task: str, diff: str, builder_output: str) -> str:
    base = read_template("qa.md")
    return f"""{base}

---

# Task under review

{task}

# Builder output

```text
{builder_output}
```

# Diff under review

```diff
{diff}
```
"""


def render_security_prompt(task: str, diff: str, qa_output: str) -> str:
    base = read_template("security.md")
    return f"""{base}

---

# Task under security review

{task}

# QA result

```text
{qa_output}
```

# Diff under review

```diff
{diff}
```
"""


def parse_qa_verdict(text: str) -> str:
    m = re.search(r"^QA_VERDICT:\s*(APPROVED_WITH_RESERVATIONS|APPROVED|REJECTED)\s*$", text, re.M)
    return m.group(1) if m else "UNKNOWN"


def parse_security_verdict(text: str) -> str:
    m = re.search(r"^VERDICT:\s*(CLEAN|ADVISORY|CRITICAL)\s*$", text, re.M)
    return m.group(1) if m else "UNKNOWN"


def command_for_builder(config: dict[str, Any], kind: BuilderKind) -> AgentConfig:
    key = "builder_frontend" if kind == "frontend" else "builder_backend"
    raw = config["agents"].get(key, {})
    return AgentConfig(
        enabled=bool(raw.get("enabled", False)),
        command=str(raw.get("command", "")),
        input=str(raw.get("input", "stdin")),
    )


def command_for_agent(config: dict[str, Any], key: str) -> AgentConfig:
    raw = config["agents"].get(key, {})
    return AgentConfig(
        enabled=bool(raw.get("enabled", False)),
        command=str(raw.get("command", "")),
        input=str(raw.get("input", "stdin")),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local file-based agent loop.")
    parser.add_argument("task", help="Task to implement")
    parser.add_argument("--mode", choices=["manual", "builder", "full"], default="manual")
    parser.add_argument("--builder", choices=["frontend", "backend"], default=None)
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument(
        "--diff-path",
        action="append",
        default=None,
        help="Limit the diff sent to QA/Security. Repeat for multiple paths.",
    )
    args = parser.parse_args()

    config = load_config()
    if args.diff_path:
        config["diff_paths"] = args.diff_path
    max_turns = args.max_turns or int(config.get("max_turns", 3))
    run_base = ROOT / config.get("run_dir", ".harness/runs")
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = run_base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    builder_kind = choose_builder(args.task, config, args.builder)
    write(run_dir / "task.md", f"# Task\n\n{args.task}\n\nBuilder: {builder_kind}\nMode: {args.mode}\n")

    prior_feedback = ""
    final_lines = [f"# Final report — {run_id}", "", f"Task: {args.task}", f"Builder: {builder_kind}", ""]

    for attempt in range(1, max_turns + 1):
        builder_prompt = render_builder_prompt(args.task, builder_kind, attempt, prior_feedback)
        write(run_dir / "builder.prompt.md", builder_prompt)

        builder_output = ""
        if args.mode in {"builder", "full"}:
            agent = command_for_builder(config, builder_kind)
            if agent.enabled and agent.command:
                print(f"[harness] Running {builder_kind} builder: {agent.command}")
                code, builder_output = run_agent(agent.command, builder_prompt, run_dir / "builder.prompt.md", agent.input)
                builder_output = f"[exit_code={code}]\n\n{builder_output}"
                if code != 0:
                    write(run_dir / "builder.output.md", builder_output)
                    final_lines += [f"## Attempt {attempt}", "", f"Builder failed with exit code {code}", ""]
                    break
            else:
                builder_output = "[builder not executed: disabled or missing command in config]"
        else:
            builder_output = "[manual mode: paste builder.prompt.md into your builder and save the result here]"

        write(run_dir / "builder.output.md", builder_output)

        diff = git_diff(config)
        status = git_status()
        write(run_dir / "diff.patch", diff)
        write(run_dir / "git-status.txt", status)

        qa_prompt = render_qa_prompt(args.task, diff, builder_output)
        write(run_dir / "qa.prompt.md", qa_prompt)

        qa_output = ""
        qa_agent = command_for_agent(config, "qa")
        if args.mode == "full" and qa_agent.enabled and qa_agent.command:
            print(f"[harness] Running QA: {qa_agent.command}")
            code, qa_output = run_agent(qa_agent.command, qa_prompt, run_dir / "qa.prompt.md", qa_agent.input)
            qa_output = f"[exit_code={code}]\n\n{qa_output}"
            if code != 0:
                final_lines += [f"## Attempt {attempt}", "", f"QA failed with exit code {code}", ""]
                write(run_dir / "qa.output.md", qa_output)
                break
        else:
            qa_output = "[manual gate: paste qa.prompt.md into QA agent and save verdict here]"
        write(run_dir / "qa.output.md", qa_output)

        qa_verdict = parse_qa_verdict(qa_output)
        final_lines += [f"## Attempt {attempt}", "", f"QA verdict: {qa_verdict}", ""]

        if args.mode != "full":
            break

        if qa_verdict == "REJECTED":
            prior_feedback = qa_output
            continue

        security_prompt = render_security_prompt(args.task, diff, qa_output)
        write(run_dir / "security.prompt.md", security_prompt)

        security_output = ""
        sec_agent = command_for_agent(config, "security")
        if sec_agent.enabled and sec_agent.command:
            print(f"[harness] Running Security: {sec_agent.command}")
            code, security_output = run_agent(
                sec_agent.command,
                security_prompt,
                run_dir / "security.prompt.md",
                sec_agent.input,
            )
            security_output = f"[exit_code={code}]\n\n{security_output}"
            if code != 0:
                final_lines += [f"Security failed with exit code {code}", ""]
                write(run_dir / "security.output.md", security_output)
                break
        else:
            security_output = "[manual gate: paste security.prompt.md into Security agent and save verdict here]"
        write(run_dir / "security.output.md", security_output)

        security_verdict = parse_security_verdict(security_output)
        final_lines += [f"Security verdict: {security_verdict}", ""]

        if security_verdict == "CRITICAL":
            prior_feedback = security_output
            continue

        break

    final_lines += ["## Files", "", f"Run directory: `{run_dir}`", "", "## Current git status", "", "```", git_status(), "```", ""]
    write(run_dir / "final-report.md", "\n".join(final_lines))

    print(f"\n[harness] Run created: {run_dir}")
    print("[harness] Next files to inspect:")
    print(f"- {run_dir / 'builder.prompt.md'}")
    print(f"- {run_dir / 'qa.prompt.md'}")
    print(f"- {run_dir / 'security.prompt.md'}")
    print(f"- {run_dir / 'final-report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
