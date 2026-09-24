#!/usr/bin/env bash
# run.sh: run the John KJV study loop, one unit per run. Built on the guide's kit/loop.sh (unchanged).
#
#   ./run.sh                       DRY RUN (the default): a throwaway copy, a mock maker, the real checker,
#                                  a mock judge. No model is called; it costs nothing and changes nothing here.
#   ./run.sh --real                write the next unit with Claude, check it, judge it, and stop
#   ./run.sh --real --unit 03      the same, for unit 03 (00 = the book overview, 01-21 = John's chapters)
#   ./run.sh status                where every unit stands
#
# Dry-run scenarios, one per stop family (like the kit's MOCK_* demos):
#   ./run.sh                  DONE on iteration 2 (exit 0)      MOCK=stuck ./run.sh   STUCK (exit 3)
#   MOCK=cap ./run.sh         CAP after MAX_ITERS (exit 2)      MOCK=tamper ./run.sh  DANGER (exit 5)
#   MOCK=stopfile ./run.sh    HUMAN (exit 4)                    MOCK=judge-fail ./run.sh  STUCK on the judge (exit 3)
#
# Exit codes (loop.sh's): 0 DONE · 1 error · 2 CAP · 3 STUCK · 4 HUMAN · 5 DANGER
# Settings: loop.env. Stop a running loop from another window: touch .loop-stop
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cd "$here"
# shellcheck source=loop.env
. ./loop.env
export PYTHONDONTWRITEBYTECODE=1 MAX_UNREVIEWED BLUEPRINT_CHECKPOINT

mode="dry"; unit=""; keep=0
while [ $# -gt 0 ]; do
  case "$1" in
    --real) mode="real" ;;
    --unit) unit="${2:-}"; shift ;;
    --keep) keep=1 ;;
    status) exec python3 tools/state.py status ;;
    -h|--help) sed -n '2,19p' "$0"; exit 0 ;;
    *) echo "run.sh: unknown argument '$1' (try --help)" >&2; exit 1 ;;
  esac
  shift
done

# ---- dry run: work in a throwaway copy so nothing here can change ----
if [ "$mode" = "dry" ]; then
  if [ ! -f tests/fixtures/john-02.good.md ]; then
    echo "run.sh: the dry run needs tests/fixtures/john-02.good.md (see tests/README.md)" >&2; exit 1
  fi
  sandbox="$(mktemp -d "${TMPDIR:-/tmp}/john-kjv-dry.XXXXXX")"
  tar cf - --exclude ./.git --exclude ./.state --exclude "./$STOP_FILE" . | (cd "$sandbox" && tar xf -)
  cd "$sandbox"
  unit="02"
  rm -f "study/john-$unit.md" reviews/john-"$unit".* loop-log.csv cost-log.csv
  python3 tools/state.py set "$unit" todo --note "dry run" >/dev/null
  export MOCK="${MOCK:-fix}"
  [ "$MOCK" = "stopfile" ] && touch "$STOP_FILE"
  agent="python3 tools/mock_maker.py"
  export JUDGE_MODE="mock"
  if [ "$MOCK" = "judge-fail" ]; then export MOCK_JUDGE="fail"; else export MOCK_JUDGE="pass"; fi
  COMMIT=0
  echo "run.sh: DRY RUN (MOCK=$MOCK) in $sandbox · no model is called"
else
  command -v "$CLAUDE_BIN" >/dev/null 2>&1 || { echo "run.sh: Claude Code ('$CLAUDE_BIN') isn't installed or isn't on PATH" >&2; exit 1; }
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch="$(git rev-parse --abbrev-ref HEAD)"
    case "$branch" in
      main|master) echo "run.sh: refusing to run on '$branch'. Give the loop its own branch first (BP-3.3):" >&2
                   echo "        git switch -c loop/john-kjv" >&2; exit 1 ;;
    esac
  else
    COMMIT=0
  fi
  agent="python3 tools/maker.py"
  export JUDGE_MODE="real"
fi

# ---- pick the unit ----
if [ -z "$unit" ]; then
  set +e; picked="$(python3 tools/state.py next)"; rc=$?; set -e
  if [ "$rc" -ne 0 ]; then echo "$picked"; exit "$rc"; fi   # 4 = your review is due; 1 = nothing left
  unit="$picked"
fi
case "$unit" in
  0[0-9]|1[0-9]|2[01]) ;;
  *) echo "run.sh: the unit must be 00-21, got '$unit'" >&2; exit 1 ;;
esac

# ---- DANGER: fingerprint everything the maker must never change ----
protect="PROMPT.md TEMPLATE.md JUDGE.md rubric.md plan.md LOOP-SPEC.md loop.env units.tsv loop.sh run.sh check.sh review.sh"
protect="$protect $(find kjv tools -type f ! -path '*/__pycache__/*' | sort | tr '\n' ' ')"
for f in study/john-*.md; do
  if [ -e "$f" ] && [ "$f" != "study/john-$unit.md" ]; then protect="$protect $f"; fi
done

# ---- run ----
python3 tools/state.py set "$unit" drafting --inc-runs --note "run started ($mode)" >/dev/null
rm -f ".state/iter-$unit"
export UNIT="$unit" MODE="$mode" COMMIT MAX_ITERS MAX_MINUTES STUCK_LIMIT MAKER_MODEL MAKER_EFFORT JUDGE_MODEL \
  MAKER_BUDGET_USD JUDGE_BUDGET_USD MAKER_TIMEOUT_MIN JUDGE_TIMEOUT_MIN CLAUDE_BIN
echo "run.sh: john-$unit · $mode · MAX_ITERS=$MAX_ITERS · STUCK_LIMIT=$STUCK_LIMIT · maker $MAKER_MODEL · judge $JUDGE_MODEL"
set +e
DRY_RUN=0 AGENT_CMD="$agent" CHECK_CMD="./check.sh" PROTECT="$protect" STOP_FILE="$STOP_FILE" \
  MAX_ITERS="$MAX_ITERS" MAX_MINUTES="$MAX_MINUTES" STUCK_LIMIT="$STUCK_LIMIT" LOG_FILE="loop-log.csv" bash ./loop.sh
rc=$?
set -e

# ---- record the outcome ----
case "$rc" in
  0) python3 tools/state.py set "$unit" review --stop 0 --note "checker and judge passed; waiting for your review" >/dev/null
     echo "run.sh: john-$unit is ready for your doctrine review: study/john-$unit.md, then ./review.sh approve $unit" ;;
  2|3|5) python3 tools/state.py set "$unit" stuck --stop "$rc" --note "read reviews/john-$unit.escalation.md" >/dev/null
     python3 tools/state.py escalate "$unit" "$rc" ;;
  4) python3 tools/state.py set "$unit" drafting --stop 4 --note "stopped by you ($STOP_FILE); rm it to resume" >/dev/null ;;
  *) python3 tools/state.py set "$unit" drafting --stop 1 --note "loop.sh exited $rc" >/dev/null ;;
esac
if [ "$mode" = "real" ] && [ "$COMMIT" = "1" ]; then
  git add -A -- . >/dev/null 2>&1 &&
    git commit -q -m "loop(john-kjv-study) john-$unit: run ended with exit $rc" -- . >/dev/null 2>&1 || true
fi
if [ -f cost-log.csv ]; then
  python3 - "$unit" <<'EOF'
import csv, sys
rows = [r for r in csv.DictReader(open("cost-log.csv")) if r["unit"] == sys.argv[1]]
total = sum(float(r["cost_usd"] or 0) for r in rows)
print(f"run.sh: john-{sys.argv[1]} Claude calls so far: {len(rows)} · ${total:.2f} total (cost-log.csv)")
EOF
fi
if [ "$mode" = "dry" ]; then
  echo "run.sh: loop-log.csv from the dry run:"; cat loop-log.csv
  if [ "$keep" = "1" ]; then echo "run.sh: kept the sandbox at $sandbox"; else cd "$here" && rm -rf "$sandbox"; fi
fi
exit "$rc"
