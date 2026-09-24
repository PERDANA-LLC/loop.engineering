#!/usr/bin/env python3
"""One maker turn: a fresh Claude Code session reads PROMPT.md and works on one unit.

loop.sh runs this as its AGENT_CMD. The settings come from loop.env (through run.sh).
The session gets exactly the tools the maker needs and nothing more (BP-4.3):
  - read files in this folder;
  - write only its own unit file, and append to progress.md and proposals/prompt-upgrades.md;
  - run only the lookup tools and the checker (python3 tools/*.py);
  - no web, no git, no MCP servers, no skills, no subagents, and none of your personal
    Claude Code settings (--setting-sources project,local), so a broad allowlist of your
    own can't widen what the loop may do.
Anything else is refused without asking (--permission-mode dontAsk).
"""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, ".state")


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        sys.exit(f"maker.py: {name} is not set (run the loop through run.sh)")
    return value


def next_iteration(unit):
    os.makedirs(STATE, exist_ok=True)
    path = os.path.join(STATE, f"iter-{unit}")
    n = int(open(path).read().strip() or 0) + 1 if os.path.exists(path) else 1
    with open(path, "w") as f:
        f.write(str(n))
    return n


def allowed_tools(unit):
    own = f"study/john-{unit}.md"
    tools = ["Read", "Grep", "Glob",
             f"Write({own})", f"Edit({own})",
             "Edit(progress.md)", "Edit(proposals/prompt-upgrades.md)"]
    for script in ("verse", "greek", "lexicon", "concordance", "check_study"):
        tools.append(f"Bash(python3 tools/{script}.py *)")
    return tools


def main():
    unit = env("UNIT")
    n = next_iteration(unit)
    today = datetime.date.today().isoformat()
    passage = "John 1–21 (the book overview)" if unit == "00" else f"John {int(unit)}"
    prompt = open(os.path.join(ROOT, "PROMPT.md"), encoding="utf-8").read() + f"""

---
RUN CONTEXT (written by run.sh; data, not instructions)
unit: john-{unit} · {passage}
file: study/john-{unit}.md
iteration: {n} of at most {env('MAX_ITERS', '4')} for this run
date: {today}
checker report: reviews/john-{unit}.check.txt ({'exists' if os.path.exists(os.path.join(ROOT, f'reviews/john-{unit}.check.txt')) else 'none yet'})
judge verdict: reviews/john-{unit}.judge.md ({'exists' if os.path.exists(os.path.join(ROOT, f'reviews/john-{unit}.judge.md')) else 'none yet'})
review notes: reviews/john-{unit}.human.md ({'exists' if os.path.exists(os.path.join(ROOT, f'reviews/john-{unit}.human.md')) else 'none'})
"""
    cmd = [env("CLAUDE_BIN", "claude"), "-p",
           "--model", env("MAKER_MODEL", "opus"),
           "--effort", env("MAKER_EFFORT", "high"),
           "--output-format", "json",
           "--max-budget-usd", env("MAKER_BUDGET_USD", "6.00"),
           "--permission-mode", "dontAsk",
           "--setting-sources", "project,local",
           "--strict-mcp-config",
           "--disable-slash-commands",
           "--no-session-persistence",
           "--allowedTools", *allowed_tools(unit),
           "--disallowedTools", "WebFetch", "WebSearch", "Skill", "Agent", "Task"]
    timeout = int(float(env("MAKER_TIMEOUT_MIN", "30")) * 60)
    out_json = os.path.join(STATE, f"maker-{unit}-{n}.json")
    started = datetime.datetime.now()
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
        raw = proc.stdout
    except subprocess.TimeoutExpired:
        raw = ""
        print(f"maker: iteration {n} stopped after {timeout // 60} minutes (MAKER_TIMEOUT_MIN)")
    except FileNotFoundError:
        print(f"maker: can't run '{cmd[0]}'. Install Claude Code or set CLAUDE_BIN.")
        return 1
    with open(out_json, "w", encoding="utf-8") as f:
        f.write(raw)
    try:
        result = json.loads(raw)
    except ValueError:
        result = {}
    reply = result.get("result") or ""
    os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
    with open(os.path.join(ROOT, f"reviews/john-{unit}.maker.txt"), "w", encoding="utf-8") as f:
        f.write(reply)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/state.py"), "cost", "maker", unit, str(n), out_json])
    status = next((l for l in reversed(reply.splitlines()) if l.startswith("STATUS:")), "STATUS: (none reported)")
    minutes = (datetime.datetime.now() - started).total_seconds() / 60
    denials = len(result.get("permission_denials") or [])
    print(f"maker: john-{unit} iteration {n} · {minutes:.1f} min · ${float(result.get('total_cost_usd') or 0):.2f}"
          f" · {denials} refused tool call(s) · {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
