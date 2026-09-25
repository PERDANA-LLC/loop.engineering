# Escalation: john-05 (John 5)

**Stopped:** STUCK, because the checker gave the same result 2 times in a row. 2026-09-25T01:21:51Z
**Goal:** `study/john-05.md` passes `tools/check_study.py 05` and the judge, ready for your doctrine review.

## What it tried (from progress.md, most recent last)
(no attempts recorded)

## The last checker report (reviews/john-05.check.txt)
```text
NOT YET · john-05 · deterministic checks found 1 problem(s). Fix every one, then stop.
1. MISSING (whole file): /home/user/loop.engineering/loops/john-kjv-study/study/john-05.md does not exist yet. Write the unit following TEMPLATE.md.
NOT YET · MISSING×1
```

## The judge's last verdict
(the judge did not run: the deterministic checks never passed)

## The maker's own best guess (a guess, not a finding)
(the maker left no STATUS line)

## The last rows of the run log
```text
1,2026-09-25T01:10:46Z,agent,fail,,,,3,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
2,2026-09-25T01:21:36Z,agent,fail,STUCK,,,5,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
1,2026-09-25T01:21:43Z,agent,fail,,,,3,"NOT YET · MISSING×1"
2,2026-09-25T01:21:44Z,agent,fail,STUCK,,,5,"NOT YET · MISSING×1"
1,2026-09-25T01:21:48Z,agent,fail,,,,3,"NOT YET · MISSING×1"
2,2026-09-25T01:21:50Z,agent,fail,STUCK,,,5,"NOT YET · MISSING×1"
```

## What you can do
- Fix the cause (for example, decide a question the maker can't: add a line to Decisions in `progress.md` or a note in `reviews/john-05.human.md`), then `./review.sh reset 05` and run again.
- If a protected file changed (DANGER), look at `git diff` before anything else.
- If the KJV text itself seems wrong, see `kjv/SOURCE.md` (errata are a person's decision).
