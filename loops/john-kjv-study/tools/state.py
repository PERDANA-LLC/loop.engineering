#!/usr/bin/env python3
"""The loop's ledger: which unit is next, where each unit stands, and what a person is
handed when a run stops without success. Only the scripts write units.tsv; the maker
can't (it's protected, and the maker's permissions don't include it).

  python3 tools/state.py status                 print every unit's status
  python3 tools/state.py next                   print the next unit to run (exit 4: a person is due; 1: none left)
  python3 tools/state.py get NN                 print one unit's status
  python3 tools/state.py set NN STATUS [--stop S] [--note TEXT] [--reviewer NAME] [--inc-runs]
  python3 tools/state.py escalate NN STOP       write reviews/john-NN.escalation.md
  python3 tools/state.py cost ROLE NN ITER JSONFILE   append one row to cost-log.csv from claude's JSON output

Statuses: todo · drafting (a run started) · review (the checker and judge passed; waiting for
a person) · revise (a person asked for changes) · stuck (a run ended CAP, STUCK, or DANGER;
a person must look) · approved (a person approved the doctrine).
"""
import csv
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITS = os.path.join(ROOT, "units.tsv")
COSTS = os.path.join(ROOT, "cost-log.csv")
COLS = ["unit", "status", "runs", "last_stop", "updated", "reviewer", "note"]
STATUSES = ["todo", "drafting", "review", "revise", "stuck", "approved"]
STOP_NAMES = {"0": "DONE", "1": "ERROR", "2": "CAP", "3": "STUCK", "4": "HUMAN", "5": "DANGER"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    with open(UNITS, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def save(rows):
    tmp = UNITS + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, UNITS)


def find(rows, unit):
    for r in rows:
        if r["unit"] == unit:
            return r
    sys.exit(f"no unit {unit} in units.tsv")


def cmd_status(_args):
    rows = load()
    counts = {}
    print(f"{'unit':<5} {'passage':<12} {'status':<9} {'runs':>4}  {'last stop':<9} {'updated':<20} note")
    for r in rows:
        passage = "John 1–21" if r["unit"] == "00" else f"John {int(r['unit'])}"
        print(f"{r['unit']:<5} {passage:<12} {r['status']:<9} {r['runs']:>4}  {r['last_stop']:<9} "
              f"{r['updated']:<20} {r['note']}")
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("totals: " + " · ".join(f"{s} {counts[s]}" for s in STATUSES if s in counts))


def cmd_next(args):
    max_unreviewed = int(os.environ.get("MAX_UNREVIEWED", "3"))
    checkpoint = os.environ.get("BLUEPRINT_CHECKPOINT", "1") == "1"
    rows = load()
    for wanted in ("revise", "drafting", "todo"):
        pick = next((r for r in rows if r["status"] == wanted), None)
        if pick:
            waiting = [r["unit"] for r in rows if r["status"] == "review"]
            if wanted == "todo" and len(waiting) >= max_unreviewed:
                print(f"HUMAN: {len(waiting)} drafts wait for your review ({', '.join(waiting)}). "
                      f"Review them with ./review.sh, then run again.")
                return 4
            overview = find(rows, "00")["status"]
            if wanted == "todo" and checkpoint and pick["unit"] != "00" and overview != "approved":
                # KJV82's Blueprint checkpoint: the course plan is approved before the lessons are drafted.
                print(f"HUMAN: the Blueprint checkpoint. Unit 00 (status: {overview}) holds the Lesson Map that "
                      f"sets every lesson's title, Big Idea, and memory verse; approve it before chapter units "
                      f"start (./review.sh), or run one anyway with ./run.sh --real --unit NN.")
                return 4
            print(pick["unit"])
            return 0
    stuck = [r["unit"] for r in rows if r["status"] == "stuck"]
    if stuck:
        print(f"HUMAN: nothing runnable; stuck units need you: {', '.join(stuck)} "
              f"(read reviews/john-NN.escalation.md, then ./review.sh reset NN)")
        return 4
    print("ALL DONE: every unit is in review or approved")
    return 1


def cmd_get(args):
    print(find(load(), args[0])["status"])
    return 0


def cmd_set(args):
    unit, status = args[0], args[1]
    if status not in STATUSES:
        sys.exit(f"unknown status {status}")
    rows = load()
    r = find(rows, unit)
    r["status"] = status
    r["updated"] = now()
    rest = args[2:]
    while rest:
        flag = rest.pop(0)
        if flag == "--stop":
            r["last_stop"] = STOP_NAMES.get(rest[0], rest[0])
            rest.pop(0)
        elif flag == "--note":
            r["note"] = rest.pop(0).replace("\t", " ").replace("\n", " ")[:120]
        elif flag == "--reviewer":
            r["reviewer"] = rest.pop(0)
        elif flag == "--inc-runs":
            r["runs"] = str(int(r["runs"] or 0) + 1)
        else:
            sys.exit(f"unknown flag {flag}")
    save(rows)
    return 0


def read(path, default=""):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return default


def cmd_escalate(args):
    unit, stop = args[0], STOP_NAMES.get(args[1], args[1])
    why = {
        "CAP": f"the iteration or time cap ran out (MAX_ITERS={os.environ.get('MAX_ITERS', '?')}, "
               f"MAX_MINUTES={os.environ.get('MAX_MINUTES', '?')})",
        "STUCK": f"the checker gave the same result {os.environ.get('STUCK_LIMIT', '?')} times in a row",
        "DANGER": "a protected file changed during the run (the text, the tools, a prompt, or another unit)",
        "ERROR": "the loop script hit an error",
    }.get(stop, stop)
    attempts = [l for l in read("progress.md").splitlines() if l.startswith(f"- john-{unit} iter")]
    check = read(f"reviews/john-{unit}.check.txt", "(no checker report)").strip().splitlines()
    judge = read(f"reviews/john-{unit}.judge.md", "(the judge did not run: the deterministic checks never passed)")
    maker = read(f"reviews/john-{unit}.maker.txt", "").strip().splitlines()
    status_line = next((l for l in reversed(maker) if l.startswith("STATUS:")), "(the maker left no STATUS line)")
    log_rows = [l for l in read("loop-log.csv").splitlines()[1:]][-6:]
    passage = "John 1–21" if unit == "00" else f"John {int(unit)}"
    text = f"""# Escalation: john-{unit} ({passage})

**Stopped:** {stop}, because {why}. {now()}
**Goal:** `study/john-{unit}.md` passes `tools/check_study.py {unit}` and the judge, ready for your doctrine review.

## What it tried (from progress.md, most recent last)
{chr(10).join(attempts[-5:]) or "(no attempts recorded)"}

## The last checker report (reviews/john-{unit}.check.txt)
```text
{chr(10).join(check[:25])}{chr(10) + "..." if len(check) > 25 else ""}
```

## The judge's last verdict
{judge.strip()[:3000]}

## The maker's own best guess (a guess, not a finding)
{status_line}

## The last rows of the run log
```text
{chr(10).join(log_rows)}
```

## What you can do
- Fix the cause (for example, decide a question the maker can't: add a line to Decisions in `progress.md` or a note in `reviews/john-{unit}.human.md`), then `./review.sh reset {unit}` and run again.
- If a protected file changed (DANGER), look at `git diff` before anything else.
- If the KJV text itself seems wrong, see `kjv/SOURCE.md` (errata are a person's decision).
"""
    os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
    with open(os.path.join(ROOT, f"reviews/john-{unit}.escalation.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote reviews/john-{unit}.escalation.md")
    return 0


def cmd_cost(args):
    role, unit, iteration, path = args
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    u = d.get("usage") or {}
    tokens_in = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    models = os.environ.get("MAKER_MODEL" if role == "maker" else "JUDGE_MODEL", "")   # the configured alias
    new = not os.path.exists(COSTS)
    with open(COSTS, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["time", "unit", "iteration", "role", "model", "tokens_in", "cache_read", "tokens_out",
                        "cost_usd", "turns", "error"])
        w.writerow([now(), unit, iteration, role, models, tokens_in, int(u.get("cache_read_input_tokens") or 0),
                    int(u.get("output_tokens") or 0), round(float(d.get("total_cost_usd") or 0), 4),
                    d.get("num_turns", ""), d.get("subtype", "no-json") if d.get("is_error") or not d else ""])
    return 0


def main(argv):
    cmds = {"status": cmd_status, "next": cmd_next, "get": cmd_get, "set": cmd_set,
            "escalate": cmd_escalate, "cost": cmd_cost}
    if not argv or argv[0] not in cmds:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    return cmds[argv[0]](argv[1:]) or 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
