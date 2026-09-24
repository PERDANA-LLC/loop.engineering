#!/usr/bin/env bash
# review.sh: your checkpoint. The loop drafts; a person decides (autonomy rung 2, suggest).
#
#   ./review.sh                       list the units waiting for you, and any that are stuck
#   ./review.sh approve 03 "Your Name"   approve unit 03's doctrine: recorded in units.tsv and progress.md,
#                                     and the unit's header changes from DRAFT to APPROVED
#   ./review.sh revise 03 "notes"     send unit 03 back with your notes; the next ./run.sh --real revises it
#   ./review.sh reset 03              after a stuck run (read reviews/john-03.escalation.md first): run it again
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1

action="${1:-list}"
unit="${2:-}"
if [ "$action" != "list" ]; then
  case "$unit" in
    0[0-9]|1[0-9]|2[01]) ;;
    *) echo "review.sh: give a unit 00-21, for example: ./review.sh $action 03" >&2; exit 1 ;;
  esac
fi
today="$(date +%Y-%m-%d)"

case "$action" in
  list)
    python3 tools/state.py status | awk -F'  +' 'NR==1 || /review|stuck|revise/'
    echo "Read a draft: study/john-NN.md · the judge's scores: reviews/john-NN.judge.md" ;;
  approve)
    name="${3:?review.sh approve NN \"Your Name\"}"
    [ "$(python3 tools/state.py get "$unit")" = "review" ] || { echo "review.sh: john-$unit isn't waiting for review" >&2; exit 1; }
    python3 tools/check_study.py "$unit" >/dev/null || { echo "review.sh: john-$unit no longer passes the checker; run ./run.sh --real --unit $unit" >&2; exit 1; }
    python3 - "$unit" "$name" "$today" <<'EOF'
import sys
unit, name, today = sys.argv[1:]
path = f"study/john-{unit}.md"
text = open(path, encoding="utf-8").read()
text = text.replace("DRAFT for human doctrine review", f"APPROVED by {name} on {today}", 1)
open(path, "w", encoding="utf-8").write(text)
with open("progress.md", "a", encoding="utf-8") as f:
    f.write(f"- {today} · john-{unit} · approved by {name} (doctrine review)\n")
EOF
    python3 tools/state.py set "$unit" approved --reviewer "$name" --note "approved $today" >/dev/null
    echo "review.sh: john-$unit approved by $name. Commit it when you're ready: git add -A && git commit -m \"Approve john-$unit\"" ;;
  revise)
    notes="${3:?review.sh revise NN \"your notes\"}"
    mkdir -p reviews
    printf '\n## %s · notes from your review\n\n%s\n' "$today" "$notes" >> "reviews/john-$unit.human.md"
    python3 tools/state.py set "$unit" revise --note "your notes: reviews/john-$unit.human.md" >/dev/null
    echo "review.sh: john-$unit goes back to the maker with your notes (reviews/john-$unit.human.md)" ;;
  reset)
    rm -f ".state/iter-$unit"
    if [ -f "reviews/john-$unit.human.md" ]; then next="revise"; else next="todo"; fi
    python3 tools/state.py set "$unit" "$next" --note "reset $today" >/dev/null
    echo "review.sh: john-$unit is back in the queue as '$next'" ;;
  *) echo "review.sh: unknown action '$action' (list, approve, revise, reset)" >&2; exit 1 ;;
esac
