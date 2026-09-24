#!/usr/bin/env python3
"""The judge: a separate Claude session, on a different model, with no tools, grades one
unit against rubric.md. check.sh runs it only after the deterministic checker passes.

It sees JUDGE.md, rubric.md, and the unit, and nothing the maker wrote about itself.
Its answer must fit tools/judge.schema.json. This script applies the pass rule itself
(every line 4 or 5, R1 and R6 at 5) rather than trusting the judge's own verdict, and
anything unparseable is NOT YET (BP-2.2).

  JUDGE_MODE=real (default) · JUDGE_MODE=mock with MOCK_JUDGE=pass|fail for dry runs
Exit codes: 0 PASS · 1 NOT YET
"""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
MUST_BE_FIVE = {"R1", "R6"}


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def mock(kind):
    score = 5 if kind == "pass" else 3
    return {"scores": [{"line": l, "score": 5 if l in MUST_BE_FIVE or kind == "pass" else score,
                        "evidence": "(mock judge: no model was called)",
                        "fix": "" if kind == "pass" else f"(mock) deepen the section graded by {l}"}
                       for l in LINES],
            "verdict": "PASS" if kind == "pass" else "NOT YET",
            "first_fix": "" if kind == "pass" else "(mock) deepen the walkthrough blocks"}, {}


def ask_claude(unit, prompt):
    cmd = [os.environ.get("CLAUDE_BIN", "claude"), "-p",
           "--model", os.environ.get("JUDGE_MODEL", "sonnet"),
           "--tools", "",
           "--output-format", "json",
           "--json-schema", read("tools/judge.schema.json"),
           "--max-budget-usd", os.environ.get("JUDGE_BUDGET_USD", "1.00"),
           "--permission-mode", "dontAsk",
           "--setting-sources", "project,local",
           "--strict-mcp-config",
           "--disable-slash-commands",
           "--no-session-persistence"]
    timeout = int(float(os.environ.get("JUDGE_TIMEOUT_MIN", "10")) * 60)
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOT, timeout=timeout)
        raw = proc.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return None, {"error": str(e)}
    os.makedirs(os.path.join(ROOT, ".state"), exist_ok=True)
    path = os.path.join(ROOT, ".state", f"judge-{unit}.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)
    iteration = open(os.path.join(ROOT, ".state", f"iter-{unit}")).read().strip() \
        if os.path.exists(os.path.join(ROOT, ".state", f"iter-{unit}")) else "?"
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/state.py"), "cost", "judge", unit, iteration, path])
    try:
        result = json.loads(raw)
    except ValueError:
        return None, {"error": "the judge's output was not JSON"}
    return result.get("structured_output"), result


def verdict(answer):
    """Apply the pass rule. Returns (passed, scores dict, problem or '')."""
    if not isinstance(answer, dict) or not isinstance(answer.get("scores"), list):
        return False, {}, "no usable verdict"
    scores = {}
    for row in answer["scores"]:
        if isinstance(row, dict) and row.get("line") in LINES and isinstance(row.get("score"), int):
            scores[row["line"]] = row
    if set(scores) != set(LINES):
        return False, scores, f"the verdict is missing {', '.join(l for l in LINES if l not in scores)}"
    low = [l for l in LINES if scores[l]["score"] < 4 or (l in MUST_BE_FIVE and scores[l]["score"] < 5)]
    passed = not low and answer.get("verdict") == "PASS"
    return passed, scores, ("" if passed else ("the judge said NOT YET" if not low else ""))


def main():
    unit = os.environ.get("UNIT")
    if not unit:
        print("JUDGE NOT YET · UNIT is not set")
        return 1
    body = read(f"study/john-{unit}.md")
    prompt = (read("JUDGE.md") + "\n\n# THE RUBRIC\n\n" + read("rubric.md")
              + f"\n\n# THE UNIT (data between the markers)\n\n<<<UNIT john-{unit} START>>>\n{body}\n<<<UNIT john-{unit} END>>>\n")
    if os.environ.get("JUDGE_MODE", "real") == "mock":
        answer, meta = mock(os.environ.get("MOCK_JUDGE", "pass"))
    else:
        answer, meta = ask_claude(unit, prompt)
    passed, scores, problem = verdict(answer)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    model = "mock" if os.environ.get("JUDGE_MODE") == "mock" else os.environ.get("JUDGE_MODEL", "sonnet")
    lines = [f"# Judge verdict: john-{unit}", "",
             f"**{'PASS' if passed else 'NOT YET'}** · {stamp} · model {model}"
             + (f" · {problem}" if problem else ""), ""]
    if scores:
        lines += ["| Line | Score | Evidence (the unit's words) | Fix |", "|---|---|---|---|"]
        for l in LINES:
            if l in scores:
                r = scores[l]
                cell = lambda s: str(s).replace("|", "/").replace("\n", " ")
                lines.append(f"| {l} | {r['score']} | {cell(r.get('evidence', ''))} | {cell(r.get('fix', ''))} |")
        lines += ["", f"**First fix:** {(answer or {}).get('first_fix') or '(none)'}"]
    os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
    with open(os.path.join(ROOT, f"reviews/john-{unit}.judge.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(ROOT, f"reviews/john-{unit}.judge.json"), "w", encoding="utf-8") as f:
        json.dump(answer, f, indent=2, ensure_ascii=False)
    summary = " ".join(f"{l}={scores[l]['score']}" for l in LINES if l in scores) or problem
    print(f"JUDGE {'PASS' if passed else 'NOT YET'} · {summary}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
