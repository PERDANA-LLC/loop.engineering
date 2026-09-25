# Loop Spec: john-kjv-study

<!-- Layer: Loop. The one-page design, in the nine boxes of the guide's kit/LOOP-SPEC.md, filled in the
     order the guide recommends (DONE WHEN → CHECKER → LIMITS → GOAL → ...), then shown in box order.
     Protected: the loop stops with DANGER if this file changes during a run. -->

| Header | |
|---|---|
| Name | `john-kjv-study` |
| Version | v2.0 |
| Owner | the person who runs `review.sh` (write your name here) |
| Autonomy rung | **2 · suggest.** The loop drafts units on its own branch; a person approves every unit's doctrine. It stays at rung 2 however good its numbers get: teaching Scripture to others is a person's call (CS-2, BP-6.1). |
| Risk level | **medium:** the units will be taught to others. No money, no production systems, nothing irreversible, no network for the maker. |

## 1 · GOAL
Every unit in `plan.md` (the book overview and John 1–21) exists in `study/` in the KJV72 × KJV82 format (`TEMPLATE.md`: KJV82's workbook lesson, KJV72's Berean Council study with a verse-by-verse walkthrough, KJV82's Leader's Guide), quotes Scripture only as exact KJV text, and has been approved by a person.

The loop's unit of work (TRK-1.1) is one unit per run: `study/john-NN.md`.

## 2 · DONE WHEN
- **A run is DONE** when `check.sh` exits 0: `tools/check_study.py NN` reports PASS **and** the judge scores every line of `rubric.md` 4 or 5, with R1 (faithful to the text) and R6 (honest claims) at 5. The script applies that rule to the judge's JSON; the judge's own verdict isn't trusted alone.
- **A unit is done** when a person runs `./review.sh approve NN "Name"`.
- **The study is done** when `./run.sh status` shows 22 units approved.

The checker's PASS means: every double-quoted passage of three or more words is a referenced, exact KJV quotation (word for word, punctuation for punctuation, against `kjv/kjv.tsv`); every reference exists; Read & Mark prints the whole chapter, every verse exact and in order; the walkthrough covers every verse of the chapter in order, in blocks of at most 6 verses that each quote their own text and keep Says, Means, and Asks apart; every section and labeled part of the format is present; every participant question is numbered, has write-in lines under it, and has an answer with a verse in the Leader's Guide; every practice cites a verse, with at least 3 per set and the Life and Light sets tagged inward and outward; the commitment lines and the two guards are printed; the planners, the session plan (75 minutes), the glossary (every flagged word, each in its verse), and the word study (each Greek word in its verse) have their shapes; the doctrine blocks follow the categories in order, each with five parts and 2–3 quoted cross-references, and no category is skipped; all seven scholars speak in the council; every Strong's citation names a word that is in the Textus Receptus of the verse cited, spelled and parsed as the data says; every numeral count is recomputed; and there is no placeholder, self-score, PASS/FIX list, or claim of self-verification. There is no word limit (SF-12).

## 3 · TRIGGER
**By hand** (FAQ-8: start by hand): `./run.sh --real` runs the next unit. A person may run a few in a row (`for i in 1 2 3; do ./run.sh --real || break; done`); the loop stops itself when three drafts wait for review, and chapter units wait until unit 00 is approved (KJV82's Blueprint checkpoint). No schedule yet: see "Climbing" below.

## 4 · ACTOR
- **Maker:** Claude Code headless (`claude -p`), model alias `opus` (the latest Opus model in your Claude Code version ⚠VERIFY), effort `high`, a **fresh session every iteration** (TRK-3.1). Allowed tools, and nothing else (`--permission-mode dontAsk`): Read, Grep, Glob; Write and Edit on its own unit file only; Edit on `progress.md` and `proposals/prompt-upgrades.md`; Bash only for `python3 tools/verse.py`, `greek.py`, `lexicon.py`, `concordance.py`, and `check_study.py`. Web, git, skills, subagents, MCP servers, and the user's personal settings are all off (`--disallowedTools`, `--disable-slash-commands`, `--strict-mcp-config`, `--setting-sources project,local`). Checked in the build environment: an unlisted file write and `ls /` were both refused.
- **Judge:** `claude -p --model sonnet --tools ""` (the latest Sonnet model ⚠VERIFY): a different model, no tools, a JSON schema for its answer, and only `JUDGE.md`, `rubric.md`, and the unit to read.

## 5 · CONTEXT
Each maker run reads, in order (`PROMPT.md`): the RUN CONTEXT that `tools/maker.py` appends (unit, file, iteration, date); `reviews/john-NN.check.txt`; `reviews/john-NN.judge.md`; `reviews/john-NN.human.md`; `progress.md`; `plan.md`; `TEMPLATE.md` and `rubric.md`; for a chapter, its row in unit 00's Lesson Map; the unit file. `PROMPT.md` itself never changes between runs, and passes the run-50 test: nothing in it assumes memory.

## 6 · CHECKER
Three rungs, cheapest first, and "not yet" by default (BP-2.2, BP-2.3):

1. **Deterministic** (`tools/check_study.py`, free, a few seconds): the list under DONE WHEN, plus near misses: a single-quoted phrase that is close to KJV wording but not exact fails too (SF-4). Its messages are the maker's next prompt: the first failing thing, the line, expected against actual (TIP-2.1). Example (❌ a deliberate misquote): `QUOTE-MISMATCH (line 57): "I am the resurrection and the life" (John 11:25) departs from the KJV after "I am the resurrection": the quotation has " and the life", the KJV has ", and the life: he that b"`.
2. **Model judge** (`tools/judge.py`): nine anchored rubric lines (EX-2.2), evidence quoted for every score (TRK-2.2), a pass threshold, a different model from the maker, no tools, and the unit fenced as data.
3. **A person** (`review.sh`): every unit's doctrine, before it counts.

**Where the prompts' own checks went.** KJV72 ends with a verification pass (V1–V14) and a self-audit; KJV82 with a workbook audit (V1–V18) and a conformity check per lesson. A maker checking its own work is what loop engineering removes first, so each item moved to a rung that isn't the maker:

| The prompts' check | Now checked by |
|---|---|
| Quotations exact (72 V1, 82 V1) | the checker: QUOTE-*, TEXT-* |
| References exist and support the claim (72 V2, 82 V2) | the checker: REF-INVALID; the judge: R1 |
| No invented historical quotations (72 V3, 82 V3) | the checker: double quotation marks are Scripture only (QUOTE-UNREFERENCED); the judge: R6 |
| KJV only (82 V4) | the checker: QUOTE-VERSION; the judge: R6 |
| Archaic words glossed; the Glossary aligned (72 V4, 82 V5) | the checker: GLOSSARY |
| Says, Means, and Asks kept apart (72 V5, 82 V6) | the checker: LAYERS and the ladder's sections; the judge: R4 |
| Every component present; the doctrine in detail (72 V6, 82 V6) | the checker: STRUCTURE, LABELS, DOCTRINE-*; the judge: R5 |
| The question split, open questions, the full ladder, write-in lines (72 V7, 82 V7–V8) | the checker: QUESTIONS, WRITE-IN; the judge: R3 |
| Fair views, View A and View B (72 V8, 82 V9) | the checker: the panel and its proof texts; the judge: R1, R6 |
| Case study and example complete (82 V10) | the checker: STRUCTURE, PLACEHOLDER; the judge: R8 |
| Every question answered (82 V11) | the checker: ANSWER-KEY; the judge: R8 |
| "I will" commitments (82 V12) | the checker: FIXED-LINE |
| The memory verse, verbatim, with copy lines (82 V13) | the checker: MEMORY-VERSE, QUOTE-*, WRITE-IN |
| The timing fits (72 V9, 82 V14) | the checker: SESSION-PLAN |
| Humility, and 3+ practices (72 V10, 82 V15) | the checker: PRACTICES; the judge: R2, R7 |
| The Life and Light pathways, planners, practices, guards (72 V11–V12, 82 V16–V17) | the checker: LABELS, PLANNER, PRACTICES, FIXED-LINE; the judge: R7 |
| Source discipline (72 V13, 82 V18) | the checker: a verse on every practice; the judge: R2 |
| The Life & Light Audit answered, its fix made (72 V14) | the checker: the audit's parts; the judge: R7 |
| KJV72's self-audit on twelve dimensions | the judge's nine lines (`rubric.md`) |

**Protected** (DANGER, exit 5, if any changes during a run): `kjv/`, `tools/`, `PROMPT.md`, `TEMPLATE.md`, `JUDGE.md`, `rubric.md`, `plan.md`, this file, `loop.env`, `units.tsv`, the four scripts, and every unit except the one being written (HCK-2.1).

### CALC-1 · Verifier Trust
Trust = p·S ÷ (p·S + (1 − p)·F)

- **The deterministic checker, measured.** Its test suite (`tests/test_checker.py`) holds known-good and known-bad work: 25 known-good cases, all passed (S = 25 ÷ 25 = 1.0), including the real John 2 unit and two minimal units that keep every rule of the format; and 84 known-bad cases (misquoted Scripture, a changed verse in the printed chapter, near misses in single quotes, dropped verses, invented references, wrong Greek, unbacked counts, unanswered questions, practices without a verse, missing guards, a skipped doctrinal category, a transliteration that contradicts its Greek (SF-10, SF-14), self-grading, garbage), none passed (F = 0 ÷ 84 = 0). With F = 0, trust in its PASS is 1.0 for any p: p·1.0 ÷ (p·1.0 + (1 − p)·0) = 1.0. **Band: 95%+.** Its blind spot is what it doesn't measure: a paraphrase written without quotation marks, a practice that cites a verse but runs on willpower, or a wrong interpretation. Those belong to the judge and to you.
- **The judge: FIELD WORK.** It hasn't been calibrated yet (rubric.md, "Calibration"). Until it is, use the guide's CS-2 numbers **as an example only**: p = 0.5, S = 0.8, F = 0.1 → 0.5 × 0.8 ÷ (0.4 + 0.5 × 0.1) = 0.4 ÷ 0.45 = **0.889, about 89%**: the 80–94% band, where a person checks the passes. Rung 2 does exactly that: you review every unit.

## 7 · STATE
Memory lives in files, never in a conversation (BP-3.2):
- `units.tsv`: every unit's status (`todo`, `drafting`, `review`, `revise`, `stuck`, `approved`), written only by the scripts;
- `progress.md`: decisions to follow, and two log lines per iteration;
- `study/`: the units; `reviews/`: each unit's checker report, judge verdict, the maker's last reply, your notes, any escalation;
- `loop-log.csv`: one row per iteration, in the workbook's Run Log columns; `cost-log.csv`: one row per Claude call, with tokens and dollars;
- git: one commit per iteration on the loop's branch, carrying the check result (HCK-3.1).

Every iteration is a fresh session that picks up from these files alone, so the resume test (BP-3.2) runs on every iteration.

## 8 · LIMITS
| Family | Rule |
|---|---|
| DONE | `check.sh` exits 0: the checker passes and the judge passes |
| CAP | **4 iterations** per run (CALC-2) · 180 minutes per run · **$12.00 per maker call and $1.50 per judge call** (`--max-budget-usd`), so a unit's ceiling is 4 × $13.50 = **$54.00** · a maker call is stopped after 45 minutes, a judge call after 15 |
| STUCK | the same checker result (or the same judge scores) **twice in a row** (CS-2: the same mismatch twice) |
| DANGER | a protected file changes (the list under CHECKER). A tool the maker isn't allowed is refused outright and counted in its log line. |
| HUMAN | `.loop-stop` exists · Claude's usage limit refuses the maker or the judge (the unit is paused, not stuck: SF-15) · 3 drafts are waiting for review (no new unit starts) · chapter units wait until unit 00 is approved (KJV82's Blueprint checkpoint, `BLUEPRINT_CHECKPOINT`) · every unit waits for your approval |

### CALC-2 · Tries-to-Success
Planning assumption until the log says otherwise: p = 0.6, the share of units passing the checker and the judge on a given try (CS-2's figure; replace it with the measured rate after five units, TRK-6.2). C = 0.95, because a failed unit wastes a run.

tries = ⌈ln(1 − C) ÷ ln(1 − p)⌉ = ⌈ln(0.05) ÷ ln(0.4)⌉ = ⌈−2.996 ÷ −0.916⌉ = ⌈3.27⌉ = **4 tries**. Check: 1 − 0.4⁴ = 1 − 0.0256 = **0.974**; with 3 tries, 1 − 0.064 = 0.936, which falls short. Average tries used with a cap of 4: (1 − 0.4⁴) ÷ 0.6 = **1.62**.

**The v2.0 shakedown, one data point:** John 2 passed the checker on its first try and the judge on its third; each judge failure named a new R6 problem (SF-10, SF-11), and each was fixed in a try of about a minute. One unit is not a rate: keep p = 0.6 until five units are logged.

### CALC-3 · Loop Budget
Measured on the v2.0 shakedown run (John 2, the shortest chapter at 25 verses), with the list prices of the models those aliases pointed to in the build environment (from the Claude API reference bundled with Claude Code, cached 2026-06-24; ⚠VERIFY on the pricing page, because an alias moves to each new model and prices change). Claude Code caches prompts for an hour, so input comes in three kinds, each with its own price:

| Price per million tokens | Uncached input | Cache write (1 hour) | Cache read | Output |
|---|---|---|---|---|
| Maker (the `opus` alias) | $4.00 | $8.00 | $0.20 | $20.00 |
| Judge (the `sonnet` alias) | $2.00 | $4.00 | $0.20 | $10.00 |

**Cost per iteration = (uncached × Pin + cache writes × Pwrite + cache reads × Pread + Tout × Pout) ÷ 1,000,000**, the guide's formula with the input split by kind. The measured calls (`cost-log.csv`), recomputed:

| Call | Uncached | Cache writes | Cache reads | Output | Arithmetic | Cost |
|---|---|---|---|---|---|---|
| Maker, iteration 1 (the first draft, 85 turns, 18.5 min) | 100 | 273,902 | 8,516,738 | 114,083 | (100×4 + 273,902×8 + 8,516,738×0.20 + 114,083×20) ÷ 10⁶ | **$6.18** |
| Judge, iteration 1 | 2 | 49,245 | 0 | 13,114 | (2×2 + 49,245×4 + 13,114×10) ÷ 10⁶ | **$0.33** |
| Maker, iteration 2 (one fix, 21 turns, 1.5 min) | 38 | 25,815 | 925,262 | 8,358 | (38×4 + 25,815×8 + 925,262×0.20 + 8,358×20) ÷ 10⁶ | **$0.56** |
| Judge, iteration 2 | 2 | 44,198 | 5,104 | 10,588 | (2×2 + 44,198×4 + 5,104×0.20 + 10,588×10) ÷ 10⁶ | **$0.28** |
| Maker, iteration 3 (one fix, 20 turns, 1.1 min) | 24 | 25,881 | 558,885 | 6,702 | (24×4 + 25,881×8 + 558,885×0.20 + 6,702×20) ÷ 10⁶ | **$0.45** |
| Judge, iteration 3 | 2 | 44,410 | 5,104 | 15,000 | (2×2 + 44,410×4 + 5,104×0.20 + 15,000×10) ÷ 10⁶ | **$0.33** |

Each result matches the `total_cost_usd` that Claude Code reported for that call.

- **This unit:** $6.18 + $0.33 + $0.56 + $0.28 + $0.45 + $0.33 = **$8.13** in **29 minutes**, DONE on iteration 3. (v1.0's bs3 unit of the same chapter cost $3.44 in 13 minutes: the combined format is about two and a half times the work.)
- **Typical unit (a cautious estimate):** scaling by verses, $8.13 ÷ 25 = $0.325 per verse; John averages 879 ÷ 21 = 41.9 verses per chapter, so **about $13.60 per unit**, and about $23 for John 6 (71 verses). Much of a unit (the foundations, the doctrine, the council, the guide) doesn't grow with the chapter, so this likely overstates; re-measure after five units.
- **Ceiling per unit** (the hard caps; the most a unit can cost if every try fails): N × (maker cap + judge cap) = 4 × ($12.00 + $1.50) = **$54.00**. A first draft that reaches the $12.00 maker cap stops where it is, and the next iteration continues from the file.
- **The whole study (22 units), cautious:** $0.325 × (879 verses + 41.9 for the overview) ≈ **$299**. Ceiling: 22 × $54.00 = **$1,188**.
- **Monthly, at R = 8 units a month** (two a week): cautious 8 × $13.60 ≈ **$109**; ceiling 8 × $54.00 = **$432**. Set spend alerts at 50% and 80% of the ceiling you choose (TIP-6.3).
- **Time ceiling:** the run stops starting iterations after 180 minutes; with a 45-minute maker cap and a 15-minute judge cap, the worst case is 180 + 60 = **240 minutes**.

On a Claude subscription, `claude -p` usage counts against the plan's limits rather than a bill; the dollars then measure how much of the plan a unit uses ⚠VERIFY.

## 9 · ESCALATION
When a run stops with CAP, STUCK, or DANGER, `tools/state.py escalate` writes `reviews/john-NN.escalation.md`, and the unit goes to `stuck` until a person runs `./review.sh reset NN`. The note has the guide's five parts (EX-3.2): the goal; the stop family and the rule that fired; what the maker tried (its log lines); the evidence (the last checker report, the judge's verdict, the last log rows); and the maker's best guess, marked as a guess. It ends with what the person can do next.

---

## CALC-4 · Loop Scorecard
Rated after the v2.0 shakedown run and the dry runs, as a skeptical reviewer would.

| # | Criterion | Rating | Why, and what would raise it |
|---|---|---|---|
| 1 | Goal & done condition | 5 | An end state a script checks; DONE, and four failure exits, all demonstrated |
| 2 | Checker | 4 | Deterministic checker measured at S = 25/25 and F = 0/84, now covering the whole format; a separate judge on another model, which caught a real error the script couldn't (SF-10), since fixed in the script; a person on every unit. **Not 5:** the judge isn't calibrated on your own graded sample yet (FIELD WORK 1) |
| 3 | Stop rules & budget | 5 | All five families, each demonstrated in a dry run, plus the Blueprint checkpoint; the cap from CALC-2; per-call dollar caps; time caps; ceilings from CALC-3 with measured costs |
| 4 | Safety | 4 | Its own branch (enforced), least privilege (verified: six refused calls in the shakedown, SF-13), protected files (DANGER demonstrated), no network, a stop file, dry run by default. **Not 5:** it runs on your machine, not in a disposable container (HCK-4.1) |
| 5 | State & memory | 5 | Ledger, decisions, reviews, logs, and commits in files; every iteration is a fresh session that resumes from them (iterations 2 and 3 each fixed exactly the judge's first fix) |
| 6 | Observability | 4 | A row per iteration (the workbook's Run Log columns) and a row per Claude call with tokens and dollars; escalation notes. **Not 5:** no alert when a scheduled day has no rows (AVD-5.3); only one unit measured in this format |
| 7 | Human touchpoints | 5 | Rung 2 stated; approve, revise, and reset; KJV82's Blueprint checkpoint; a five-part escalation note; the review checkpoint; the proposals channel, whose v2.0 proposals were adopted (SF-10, SF-11) |
| 8 | Reusability | 4 | This spec, versioned, with a changelog; the kit's `loop.sh` unchanged; reproducible data builds; `TEMPLATE.md` names the source of every section, so a KJV73 or KJV83 can be folded in. **Not 5:** the unit plan and some checks are specific to John |

**Score = 3 × (r1 + r2 + r3 + r4) + 2 × (r5 + r6 + r7 + r8) = 3 × (5 + 4 + 5 + 4) + 2 × (5 + 4 + 5 + 4) = 3 × 18 + 2 × 18 = 54 + 36 = 90 / 100: hero-grade.**

For comparison, the guide's CS-2 workbook loop scored 86, and this loop's v1.0 scored 90. The score raises confidence in the drafts, not the loop's permissions: this loop stays at rung 2. The cheapest path to a higher score is FIELD WORK 1 (calibrate the judge: checker to 5) and alerts on the run log (observability to 5).

## FIELD WORK before unattended runs
1. **Calibrate the judge:** grade 10 units you'd accept and 10 you'd reject, run the judge on all 20, and put S and F into CALC-1 (`rubric.md`, "Calibration").
2. **Check prices and plan limits** on Anthropic's pricing page and your plan ⚠VERIFY, and redo CALC-3 with them.
3. **Confirm the model aliases:** `claude -p --model opus --output-format json "Reply OK"` shows the model under `modelUsage` ⚠VERIFY.
4. **Check the text against your own Bible** for the verses you teach; `kjv/variants.tsv` shows every verse where the sources differed; `kjv/errata.tsv` takes your corrections.
5. **Replace p = 0.6** with the measured pass rate after five units, and recompute the cap (TRK-6.2).
6. **Name the owner** in the header, and set a review date in the registry row below.
7. **Read one unit against KJV72 and KJV82 themselves.** The combined format is the builder's reading of the two prompts (`TEMPLATE.md` names the source of every section). If a part should come from the other prompt, or appear twice, say so in `progress.md` Decisions, and change `TEMPLATE.md` and the checker together.

## ⚠VERIFY
- Claude Code flags used by the scripts, checked on Claude Code 2.1.282 in the build environment: `-p`, `--model`, `--effort`, `--output-format json`, `--json-schema`, `--max-budget-usd`, `--permission-mode dontAsk`, `--allowedTools` with path and command patterns, `--disallowedTools`, `--tools ""`, `--setting-sources`, `--strict-mcp-config`, `--disable-slash-commands`, `--no-session-persistence`. Re-check after a Claude Code update.
- Prices: from the Claude API reference bundled with Claude Code (cached 2026-06-24). Check the current pricing page.
- The KJV edition: the 1769 standard text as modern printings have it (`kjv/SOURCE.md`); a particular printed Bible may differ in a handful of places.

## Registry row (TIP-6.2)
| Loop | Version | Owner | Rung | Monthly ceiling | Review by |
|---|---|---|---|---|---|
| john-kjv-study | v2.0 | (you) | 2 | $432.00 at 8 units a month | 2026-12-01 |

## Climbing the ladder
This loop stays at rung 2: a person approves every unit's doctrine. What can grow is the **trigger**. After five units in a row are approved without a revise, and the judge is calibrated at 95% or more, a person may let it run three units back to back unattended (the review checkpoint still stops it). Record that decision here.

## Changelog
| Version | Date | What changed, and why |
|---|---|---|
| v0.9 | 2026-09-24 | First complete design: the nine boxes, the checker and its tests, the judge, the runner on the kit's `loop.sh`, and dry runs of all five stop families. Built with the guide's ten-step checklist. |
| v1.0 | 2026-09-24 | After the shakedown run on John 2 (DONE on iteration 2, $3.44, 13 minutes; the judge caught an arithmetic slip, 120–180 gallons for 108–162, that no script could see). Six findings folded in (SF-1 to SF-6, below). Approved by: the builder, pending the owner's review. |
| v2.0 | 2026-09-24 | **The format changed, at the owner's request:** bs3 v3.1 gave way to KJV72 × KJV82, one combined format drawing on the owner's two Berean Council prompts (`TEMPLATE.md`). The checker gained the format's rules; the prompts' own verification lists moved to the checker and the judge (the table under CHECKER); the rubric went from eight lines to nine; KJV82's Blueprint checkpoint became a HUMAN stop; caps rose with the longer units. After the v2.0 shakedown on John 2 (DONE on iteration 3, $8.13, 29 minutes, every judge line at 5): the checker passed the first draft; the judge caught a lexicon data error the checker had trusted (SF-10) and an unnamed source (SF-11), and both fixes are now in the loop; at the owner's decision the word limit is gone (SF-12). Seven findings (SF-7 to SF-13). Approved by: the builder, pending the owner's review. |
| v2.1 | 2026-09-25 | **The John run**, one loop run per unit at the owner's request. Units 00 and 01 passed (DONE on iterations 1 and 2; $5.48 and $7.43). Then Claude's usage limit refused the maker partway through John 3, and the loop read the refusals as failed drafts: John 3 and every unit after it went STUCK, 04 to 21 in seconds at $0 (SF-15). The John 3 draft also showed a quirk in the Greek text file (SF-14). Both are fixed, and 03 to 21 run again. Approved by: the builder, pending the owner's review. |

**Shakedown findings (SF), the outer loop at work:**
- **SF-1 · No single free KJV was clean.** The first pinned transcription read 'and hundred' at John 21:11, 'reach' at John 20:27, and 'others' at John 19:18. Fix: a four-source consensus text with every disputed verse audited (`kjv/SOURCE.md`).
- **SF-2 · Two numbering systems.** STEP numbers some forms apart from traditional Strong's: *oida* (G6063, John 21:15) is filed under *oida* (G1492, John 21:15) in Strong's own numbering. Fix: the lexicon links them, and a citation may use either.
- **SF-3 · The builder misquoted too.** Checked by the loop's own rules, the first draft of `plan.md` misquoted John 13:19 and put 'the true vine' in John 15:5. Fix: `tests/check_docs.py` now holds every design document to the loop's rules.
- **SF-4 · Scripture in single quotes went unchecked.** The maker quoted short KJV phrases in single quotation marks (every one was exact, but nothing enforced it). Fix: SCRIPTURE-NEARMISS fails any single-quoted phrase of five or more words that is close to a verse without matching it.
- **SF-5 · The maker's own proposal** (`proposals/prompt-upgrades.md`): whole-verse cross-references silently count toward a Key Verses limit, and 'John 2:20, 46 years' was read as a reference to a 46th verse of John 2. Fix: both noted in `TEMPLATE.md`, and the checker no longer reads a number followed by an ordinary word as a verse.
- **SF-6 · Never edit a running loop.** The builder edited `tools/check_study.py` during the live run; the DANGER fingerprint would have stopped the loop at the end of the iteration, and the edit was reverted in time. Rule: change the loop only between runs (README, 'Changing the loop').
- **SF-7 · The source prompts misquote Ephesians 5:11.** ❌ KJV72 and KJV82 both print "And have no fellowship with the works of darkness, but rather reprove them" (Ephesians 5:11), without "unfruitful". The loop quotes the KJV, and `TEMPLATE.md` warns the maker about the prompts' wording (a test holds it).
- **SF-8 · A format label that reads as a Strong's number.** The first draft of the format labeled the four group questions with a G and a number, and the checker read those labels as Strong's numbers (the first of them is one: alpha). Fix: they are Group question 1 to 4.
- **SF-9 · An empty folder vanishes.** With the bs3 unit removed, git kept no `study/` folder, and the maker writes into it. Fix: `tools/maker.py` creates `study/` before each call.
- **SF-10 · A lexicon entry that contradicts its own Greek.** The STEPBible lexicon gives the noun ἱερόν ('temple') the transliteration of the adjective, *hieros* (G2413, 2 Timothy 3:15). The maker copied it, the checker accepted it because it trusted the same field, and the judge caught it (R6). Worse, the correct *hieron* (G2411, John 2:15) then failed the checker, so the maker cited the verses' own forms instead. Fix: `kjvlib.greek_translit` transliterates each lemma's own Greek; the checker accepts the Greek's spelling and refuses a transliteration that contradicts it; `tools/lexicon.py` prints the corrected form with a note. Five of the 9,549 Greek entries contradict their lemma, and 24 more write a diphthong's breathing inside it ('ohutos' for *houtos* (G3778, John 1:2)), which the tools now print in the standard form. The maker's own proposal traced the same cause.
- **SF-11 · Name the source.** The judge marked R6 down a second time because the word studies leaned on an unnamed 'the lexicon'. The maker's proposal, adopted: `TEMPLATE.md` rule 4 names the STEPBible.org brief lexicon and Abbott-Smith's *Manual Greek Lexicon of the New Testament*, and so does `tools/lexicon.py`.
- **SF-12 · No word limit.** The first draft of John 2, the shortest chapter, ran 20,602 words, over the 20,000 ceiling, and the maker spent three checker runs trimming it; longer chapters could not have fit at the same depth. The owner's decision: no word limit at all. The judge still gives length no credit.
- **SF-13 · Least privilege held.** Six maker tool calls were refused across the three iterations, every one a compound shell command (pipes, a `for` loop, a redirect into a scratch folder, `awk`); each time the maker carried on with the single commands it is allowed.
- **SF-14 · The Greek text file's ῃ.** The Textus Receptus word file writes eta with iota subscript as 'ēa': 'elegchthēa' for ἐλεγχθῇ, *elegchthē* (G1651, John 3:20), in 1,468 words of the New Testament. The first John 3 draft wrote the correct forms, *elegchthē* and *gennēthē* (G1080, John 3:3), and the checker refused both because it trusted the file. Fix: as with the lexicon (SF-10), the Greek decides. `kjvlib.words_in` transliterates each word's own Greek where the file contradicts it, `tools/greek.py` prints the corrected form with a note, and the checker accepts it and refuses 'elegchthēa' (a test holds both).
- **SF-15 · Claude's usage limit is not a stuck unit.** Partway through John 3 the account reached its usage limit. The maker's calls came back refused at once (HTTP 429: 'You've hit your session limit · resets 4:10am (UTC)'). The checker failed the half-written draft the same way twice, so STUCK fired, and every later unit went STUCK in seconds at $0, its file missing twice. Nothing was wrong with the units. Fix: `tools/usage_limit.py` spots the refusal in the maker's or the judge's result, writes the stop file, and keeps the message. The loop stops HUMAN before its next iteration, and `run.sh` marks the unit paused with the reset time instead of stuck; `MOCK=limit ./run.sh` demonstrates it (exit 4). The half-written draft stays, with its checker report, for the next run.
- **Observed, not changed:** the judge's scores were the same on iterations 1 and 2 (R6 at 4), for different reasons, and the STUCK rule rightly didn't fire, because the checker's PASS line (its word and citation counts) changed with the edit. The cost: a maker that edits without making progress also escapes STUCK, and CAP (4 iterations) is the backstop.
