# progress.md: john-kjv-study

<!-- The loop's memory between runs (BP-3.2). Every maker run reads this first and appends to it last.
     Unit status lives in units.tsv, which only the scripts write: see it with ./run.sh status.
     This file holds the decisions to follow and the history of attempts. Keep entries to one line. -->

**Goal:** an in-depth KJV study of the Gospel of John in 22 units (`00` the book overview, `01`–`21` the chapters), each passing the checker and the judge, and each approved by a person.
**Where things stand:** `./run.sh status`. Don't record unit status in this file.

## Decisions (follow these; only a person adds or changes them)
- 2026-09-24: KJV only. Every quotation is copied from `kjv/kjv.tsv` through `tools/verse.py` (plan.md D1). Decided by: the owner.
- 2026-09-24: bs3 v3.1 structure, with the verse-by-verse walkthrough added in Tier 2; Tier 3 reads through Reformed hermeneutics with other views stated fairly (plan.md D2, TEMPLATE.md). Decided by: the owner. **Replaced on 2026-09-24 by the next line.**
- 2026-09-24: The format is KJV72 × KJV82, one combined format drawing on both prompts: KJV82's workbook lesson for participants, KJV72's Berean Council study for the leader, and KJV82's Leader's Guide (plan.md D8, TEMPLATE.md). Life, Light, humility, source discipline, and detailed doctrines are in every unit. Decided by: the owner.
- 2026-09-24: Sessions are 75 minutes for an adult small group of mixed Bible familiarity, balanced emphasis (plan.md D7). Unit 00's Lesson Map is approved before chapter units start (plan.md D9). Decided by: the owner.
- 2026-09-24: The KJV's text at John 1:18, John 5:3–4, and John 7:53–8:11 is taught as printed; the textual questions are explained at Tier 3 (plan.md D3). Decided by: the owner.
- 2026-09-24: One unit per run; a person reviews every unit's doctrine before it counts (autonomy rung 2). Decided by: the owner.

## Log
<!-- Each maker iteration appends two lines at the end of this file:
- <date> · john-NN · iteration <n> · did: <what> · next: <what> · blocked: <none or what>
- john-NN iter <n>: <what you changed> → <what check_study.py last said, or "not run">
-->
- 2026-09-24 · john-02 · iteration 1 · did: wrote the whole unit (10 walkthrough blocks, Debate Corner on one vs two temple cleansings, pisteuō word study) · next: judge review; a person should check the six (verify)-flagged commentator attributions (Augustine, Chrysostom, Calvin, Ryle, Brown ×2) against the works · blocked: none
- john-02 iter 1: first draft; fixed 3 unreferenced quotes and 1 compound quote reference; corrected loose claims (first plague vs first sign, whip contested, idiom examples, Deut 14 tithe) → PASS · 71 quotations exact · 25/25 verses in 10 blocks · 18 citations · 9,938 words
- 2026-09-24 · john-02 · iteration 2 · did: fixed the judge's R6 first_fix (waterpot volume math in Tier 2 Background) · next: judge re-review; a person should still check the six (verify)-flagged commentator attributions · blocked: none
- john-02 iter 2: changed "roughly 120 to 180 gallons" to "roughly 108 to 162 gallons" (6 jars × 2–3 firkins × ~9 gal); nothing else touched → PASS · 71 quotations exact · 25/25 verses in 10 blocks · 18 citations · 9,944 words
