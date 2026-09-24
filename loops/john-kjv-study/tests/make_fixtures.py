#!/usr/bin/env python3
"""Make the dry-run fixtures from a unit that passes the checker.

  python3 tests/make_fixtures.py study/john-02.md

Writes tests/fixtures/john-02.good.md (a copy) and tests/fixtures/john-02.flawed.md: the same
unit with one comma dropped from a quotation, the slip that CS-2's v1 made. The dry run
(./run.sh) plays the flawed draft first and the good one second, so the real checker says
NOT YET, then PASS.
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import check_study as cs  # noqa: E402


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = argv[0]
    unit = re.search(r"john-(\d\d)\.md$", src).group(1)
    rep, _ = cs.run(unit, src)
    if rep.items:
        print(f"{src} doesn't pass the checker, so it can't be the good fixture", file=sys.stderr)
        return 1
    text = open(src, encoding="utf-8").read()
    m = re.search(rf'"([^"]*?),([^"]*)" \((John {int(unit)}:\d+)\)', text)
    if not m:
        print("found no quotation with a comma to drop", file=sys.stderr)
        return 1
    flawed = text.replace(m.group(0), f'"{m.group(1)}{m.group(2)}" ({m.group(3)})', 1)
    out = os.path.join(HERE, "fixtures")
    os.makedirs(out, exist_ok=True)
    shutil.copy(src, os.path.join(out, f"john-{unit}.good.md"))
    with open(os.path.join(out, f"john-{unit}.flawed.md"), "w", encoding="utf-8") as f:
        f.write(flawed)
    print(f"wrote fixtures/john-{unit}.good.md and fixtures/john-{unit}.flawed.md "
          f"(dropped a comma from the quotation of {m.group(3)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
