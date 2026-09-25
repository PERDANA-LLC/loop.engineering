# Escalation: john-04 (John 4)

**Stopped:** STUCK, because the checker gave the same result 2 times in a row. 2026-09-25T01:21:46Z
**Goal:** `study/john-04.md` passes `tools/check_study.py 04` and the judge, ready for your doctrine review.

## What it tried (from progress.md, most recent last)
(no attempts recorded)

## The last checker report (reviews/john-04.check.txt)
```text
NOT YET · john-04 · deterministic checks found 1 problem(s). Fix every one, then stop.
1. MISSING (whole file): /home/user/loop.engineering/loops/john-kjv-study/study/john-04.md does not exist yet. Write the unit following TEMPLATE.md.
NOT YET · MISSING×1
```

## The judge's last verdict
(the judge did not run: the deterministic checks never passed)

## The maker's own best guess (a guess, not a finding)
(the maker left no STATUS line)

## The last rows of the run log
```text
1,2026-09-25T00:45:30Z,agent,fail,,,,7,"JUDGE NOT YET · R1=5 R2=5 R3=5 R4=5 R5=5 R6=4 R7=4 R8=5 R9=5"
2,2026-09-25T01:07:39Z,agent,pass,DONE,,,13,"JUDGE PASS · R1=5 R2=5 R3=5 R4=5 R5=5 R6=5 R7=5 R8=5 R9=5"
1,2026-09-25T01:10:46Z,agent,fail,,,,3,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
2,2026-09-25T01:21:36Z,agent,fail,STUCK,,,5,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
1,2026-09-25T01:21:43Z,agent,fail,,,,3,"NOT YET · MISSING×1"
2,2026-09-25T01:21:44Z,agent,fail,STUCK,,,5,"NOT YET · MISSING×1"
```

## What you can do
- Fix the cause (for example, decide a question the maker can't: add a line to Decisions in `progress.md` or a note in `reviews/john-04.human.md`), then `./review.sh reset 04` and run again.
- If a protected file changed (DANGER), look at `git diff` before anything else.
- If the KJV text itself seems wrong, see `kjv/SOURCE.md` (errata are a person's decision).
