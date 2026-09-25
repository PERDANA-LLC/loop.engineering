# Escalation: john-03 (John 3)

**Stopped:** STUCK, because the checker gave the same result 2 times in a row. 2026-09-25T01:21:40Z
**Goal:** `study/john-03.md` passes `tools/check_study.py 03` and the judge, ready for your doctrine review.

## What it tried (from progress.md, most recent last)
(no attempts recorded)

## The last checker report (reviews/john-03.check.txt)
```text
NOT YET · john-03 · deterministic checks found 14 problem(s). Fix every one, then stop.
1. STRUCTURE (whole file): missing the "## Doctrine" section (or it is out of order); sections must follow TEMPLATE.md's order
2. STRUCTURE (whole file): missing the "## Leader's Guide" section (or it is out of order); sections must follow TEMPLATE.md's order
3. STRUCTURE (whole file): missing the "## The Council" section (or it is out of order); sections must follow TEMPLATE.md's order
4. COUNT-UNBACKED (line 471): "25 times" is a count. Compute it with tools/concordance.py and add its line to the <!-- counts --> block, or write the number in words if it's a detail of the story
5. COUNT-UNBACKED (line 475): "2 times" is a count. Compute it with tools/concordance.py and add its line to the <!-- counts --> block, or write the number in words if it's a detail of the story
6. QUOTE-UNREFERENCED (line 517): "like the Son of man" has no reference. Double quotation marks are only for Scripture, followed by (Book C:V). If it isn't Scripture, use single quotation marks or italics.
7. COUNT-UNBACKED (line 556): "5 times" is a count. Compute it with tools/concordance.py and add its line to the <!-- counts --> block, or write the number in words if it's a detail of the story
8. GREEK-TRANSLIT (line 558): *elegchthē* doesn't spell G1651: the lemma is elegchō and the form in John 3:20 is elegchthēa
9. QUOTE-UNREFERENCED (line 664): "the washing of regeneration" has no reference. Double quotation marks are only for Scripture, followed by (Book C:V). If it isn't Scripture, use single quotation marks or italics.
10. COUNT-UNBACKED (line 677): "13 times" is a count. Compute it with tools/concordance.py and add its line to the <!-- counts --> block, or write the number in words if it's a detail of the story
11. COUNT-UNBACKED (line 679): "8 times" is a count. Compute it with tools/concordance.py and add its line to the <!-- counts --> block, or write the number in words if it's a detail of the story
12. GREEK-TRANSLIT (line 679): *gennēthē* doesn't spell G1080: the lemma is gennaō and the form in John 3:3 is gennēthēa
13. GREEK-TRANSLIT (line 691): *Elegchthē* doesn't spell G1651: the lemma is elegchō and the form in John 3:20 is elegchthēa
14. SCRIPTURE-NEARMISS (line 691): 'lest his deeds be exposed' looks like John 3:20 (80% alike) but isn't its exact wording. The KJV reads: "For every one that doeth evil hateth the light, neither cometh to the light, lest his deeds should be reproved." Quote Scripture exactly (in double quotation marks with the reference), or put the thought in your own words without quotation marks.
NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3
```

## The judge's last verdict
(the judge did not run: the deterministic checks never passed)

## The maker's own best guess (a guess, not a finding)
(the maker left no STATUS line)

## The last rows of the run log
```text
3,2026-09-24T23:32:40Z,agent,pass,DONE,,,17,"JUDGE PASS · R1=5 R2=5 R3=5 R4=5 R5=5 R6=5 R7=5 R8=5 R9=5"
1,2026-09-25T00:26:31Z,agent,pass,DONE,,,7,"JUDGE PASS · R1=5 R2=5 R3=4 R4=4 R5=5 R6=5 R7=5 R8=5 R9=5"
1,2026-09-25T00:45:30Z,agent,fail,,,,7,"JUDGE NOT YET · R1=5 R2=5 R3=5 R4=5 R5=5 R6=4 R7=4 R8=5 R9=5"
2,2026-09-25T01:07:39Z,agent,pass,DONE,,,13,"JUDGE PASS · R1=5 R2=5 R3=5 R4=5 R5=5 R6=5 R7=5 R8=5 R9=5"
1,2026-09-25T01:10:46Z,agent,fail,,,,3,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
2,2026-09-25T01:21:36Z,agent,fail,STUCK,,,5,"NOT YET · COUNT-UNBACKED×5 GREEK-TRANSLIT×3 QUOTE-UNREFERENCED×2 SCRIPTURE-NEARMISS×1 STRUCTURE×3"
```

## What you can do
- Fix the cause (for example, decide a question the maker can't: add a line to Decisions in `progress.md` or a note in `reviews/john-03.human.md`), then `./review.sh reset 03` and run again.
- If a protected file changed (DANGER), look at `git diff` before anything else.
- If the KJV text itself seems wrong, see `kjv/SOURCE.md` (errata are a person's decision).
