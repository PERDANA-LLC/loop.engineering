#!/usr/bin/env python3
"""The dry-run stand-in for the maker: no model, no network, no cost.

run.sh uses it for `./run.sh` without --real, inside a throwaway copy of the folder.
It plays unit 02 (John 2) from the fixtures in tests/fixtures/, so everything after it
(the real checker, loop.sh's stop rules, the ledger, the escalation note) runs for real.

  MOCK=fix         iteration 1 writes a flawed draft, iteration 2 the good one  -> DONE (exit 0)
  MOCK=stuck       the same flawed draft every time                          -> STUCK (exit 3)
  MOCK=cap         a different flaw every time                               -> CAP (exit 2)
  MOCK=tamper      edits kjv/errata.tsv, a protected file                    -> DANGER (exit 5)
  MOCK=judge-fail  the good draft, but the mock judge never passes it        -> STUCK (exit 3)
  MOCK=limit       part of a draft, then Claude's usage limit (SF-15)          -> HUMAN (exit 4), paused
  (MOCK=stopfile is handled by run.sh: it creates .loop-stop first           -> HUMAN (exit 4))
"""
import datetime
import os
import shutil
import sys

import usage_limit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    unit = os.environ.get("UNIT", "02")
    mock = os.environ.get("MOCK", "fix")
    state = os.path.join(ROOT, ".state")
    os.makedirs(state, exist_ok=True)
    counter = os.path.join(state, f"iter-{unit}")
    n = int(open(counter).read().strip() or 0) + 1 if os.path.exists(counter) else 1
    open(counter, "w").write(str(n))

    good = os.path.join(ROOT, "tests", "fixtures", f"john-{unit}.good.md")
    flawed = os.path.join(ROOT, "tests", "fixtures", f"john-{unit}.flawed.md")
    target = os.path.join(ROOT, "study", f"john-{unit}.md")
    os.makedirs(os.path.dirname(target), exist_ok=True)

    if mock == "fix":
        shutil.copy(flawed if n == 1 else good, target)
        did = "wrote the draft" if n == 1 else "fixed the checker's findings"
    elif mock == "stuck":
        shutil.copy(flawed, target)
        did = "rewrote the draft without fixing the mismatch"
    elif mock == "cap":
        shutil.copy(flawed, target)
        with open(target, "a", encoding="utf-8") as f:
            f.write(f'\nA new slip each time: "mock iteration {n} slip" appears here.\n')
        did = f"made a new mistake (iteration {n})"
    elif mock == "tamper":
        shutil.copy(good, target)
        with open(os.path.join(ROOT, "kjv", "errata.tsv"), "a", encoding="utf-8") as f:
            f.write("John\t3\t16\tFor God so loved the world.\t(mock) the maker tried to change the text\n")
        did = "edited kjv/errata.tsv"
    elif mock == "limit":
        shutil.copy(flawed, target)
        usage_limit.stop("maker", unit, "(mock) You've hit your session limit · resets 4:10am (UTC)")
        did = "wrote part of a draft, then hit Claude's usage limit"
    elif mock == "judge-fail":
        shutil.copy(good, target)
        did = "wrote a draft the mock judge rejects"
    else:
        print(f"mock maker: unknown MOCK={mock}")
        return 1

    today = datetime.date.today().isoformat()
    with open(os.path.join(ROOT, "progress.md"), "a", encoding="utf-8") as f:
        f.write(f"- john-{unit} iter {n}: (mock) {did} → not run\n")
        f.write(f"- {today} · john-{unit} · iteration {n} · did: (mock) {did} · next: the checker decides · blocked: none\n")
    print(f"mock maker: john-{unit} iteration {n} · {did} · STATUS: NOT YET · (dry run: no model called)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
