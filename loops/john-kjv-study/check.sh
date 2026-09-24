#!/usr/bin/env bash
# check.sh: the loop's CHECK_CMD. loop.sh runs it after every maker turn; only its exit code decides DONE.
#
#   1. The deterministic checker (tools/check_study.py): exact KJV quotations, every verse covered,
#      real Greek citations, recounted counts, the bs3 structure. Free and strict.
#   2. Only if that passes: the judge (tools/judge.py), a separate model with no tools and its own rubric.
#
# Exit 0 = both passed. Anything else = NOT YET, and the reports in reviews/ become the next prompt.
# What it prints is stable (no line numbers, no free text from the judge), so loop.sh's STUCK rule
# can recognise the same failure twice. The full reports go to reviews/john-NN.check.txt and .judge.md.
set -uo pipefail
cd "$(dirname "$0")" || exit 1
: "${UNIT:?check.sh needs UNIT; run the loop through run.sh}"
mkdir -p reviews

python3 tools/check_study.py "$UNIT" --report "reviews/john-$UNIT.check.txt"
status=$?
if [ "$status" -eq 0 ]; then
  python3 tools/judge.py
  status=$?
fi

# STATE: one commit per iteration, carrying the checker's result (HCK-3.1). Real runs on a branch only.
if [ "${MODE:-dry}" = "real" ] && [ "${COMMIT:-0}" = "1" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  iteration=$(cat ".state/iter-$UNIT" 2>/dev/null || echo "?")
  if [ "$status" -eq 0 ]; then result="PASS (checker and judge)"; else result="NOT YET"; fi
  git add -A -- . >/dev/null 2>&1 &&
    git commit -q -m "loop(john-kjv-study) john-$UNIT iter $iteration: $result" -- . >/dev/null 2>&1 || true
fi
exit "$status"
