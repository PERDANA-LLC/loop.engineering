# Loop Spec: john-kjv-study

<!-- Layer: Loop. The one-page design, in the nine boxes of the guide's kit/LOOP-SPEC.md, filled in the
     order the guide recommends (DONE WHEN → CHECKER → LIMITS → GOAL → ...), then shown in box order.
     Protected: the loop stops with DANGER if this file changes during a run. -->

| Header | |
|---|---|
| Name | `john-kjv-study` |
| Version | v1.0 |
| Owner | the person who runs `review.sh` (write your name here) |
| Autonomy rung | **2 · suggest.** The loop drafts units on its own branch; a person approves every unit's doctrine. It stays at rung 2 however good its numbers get: teaching Scripture to others is a person's call (CS-2, BP-6.1). |
| Risk level | **medium:** the units will be taught to others. No money, no production systems, nothing irreversible, no network for the maker. |

## 1 · GOAL
Every unit in `plan.md` (the book overview and John 1–21) exists in `study/` in the bs3 format with a verse-by-verse walkthrough, quotes Scripture only as exact KJV text, and has been approved by a person.

The loop's unit of work (TRK-1.1) is one unit per run: `study/john-NN.md`.

## 2 · DONE WHEN
- **A run is DONE** when `check.sh` exits 0: `tools/check_study.py NN` reports PASS **and** the judge scores every line of `rubric.md` 4 or 5, with R1 (faithful to the text) and R6 (honest claims) at 5. The script applies that rule to the judge's JSON; the judge's own verdict isn't trusted alone.
- **A unit is done** when a person runs `./review.sh approve NN "Name"`.
- **The study is done** when `./run.sh status` shows 22 units approved.

The checker's PASS means: every double-quoted passage of three or more words is a referenced, exact KJV quotation (word for word, punctuation for punctuation, against `kjv/kjv.tsv`); every reference exists; the walkthrough covers every verse of the chapter in order, in blocks of at most 6 verses that each quote their own text; every bs3 section is present with its counts (3–5 whole verses in Tier 1, 5–8 in Tier 2, 8+ in Tier 3; 4–5 diagnostic questions; 3–5 discussion questions; 3 preaching titles; 3 follow-up topics; a 2–3 row errors table); every Strong's citation names a word that is in the Textus Receptus of the verse cited, spelled and parsed as the data says; every numeral count is recomputed; the length is 4,500–12,000 words; and there is no placeholder, self-score, or claim of self-verification.

## 3 · TRIGGER
**By hand** (FAQ-8: start by hand): `./run.sh --real` runs the next unit. A person may run a few in a row (`for i in 1 2 3; do ./run.sh --real || break; done`); the loop stops itself when three drafts wait for review. No schedule yet: see "Climbing" below.

## 4 · ACTOR
- **Maker:** Claude Code headless (`claude -p`), model alias `opus` (the latest Opus model in your Claude Code version ⚠VERIFY), effort `high`, a **fresh session every iteration** (TRK-3.1). Allowed tools, and nothing else (`--permission-mode dontAsk`): Read, Grep, Glob; Write and Edit on its own unit file only; Edit on `progress.md` and `proposals/prompt-upgrades.md`; Bash only for `python3 tools/verse.py`, `greek.py`, `lexicon.py`, `concordance.py`, and `check_study.py`. Web, git, skills, subagents, MCP servers, and the user's personal settings are all off (`--disallowedTools`, `--disable-slash-commands`, `--strict-mcp-config`, `--setting-sources project,local`). Checked in the build environment: an unlisted file write and `ls /` were both refused.
- **Judge:** `claude -p --model sonnet --tools ""` (the latest Sonnet model ⚠VERIFY): a different model, no tools, a JSON schema for its answer, and only `JUDGE.md`, `rubric.md`, and the unit to read.

## 5 · CONTEXT
Each maker run reads, in order (`PROMPT.md`): the RUN CONTEXT that `tools/maker.py` appends (unit, file, iteration, date); `reviews/john-NN.check.txt`; `reviews/john-NN.judge.md`; `reviews/john-NN.human.md`; `progress.md`; `plan.md`; `TEMPLATE.md` and `rubric.md`; the unit file. `PROMPT.md` itself never changes between runs, and passes the run-50 test: nothing in it assumes memory.

## 6 · CHECKER
Three rungs, cheapest first, and "not yet" by default (BP-2.2, BP-2.3):

1. **Deterministic** (`tools/check_study.py`, free, about 3 seconds): the list under DONE WHEN, plus near misses: a single-quoted phrase that is close to KJV wording but not exact fails too (SF-4). Its messages are the maker's next prompt: the first failing thing, the line, expected against actual (TIP-2.1). Example (❌ a deliberate misquote): `QUOTE-MISMATCH (line 57): "I am the resurrection and the life" (John 11:25) departs from the KJV after "I am the resurrection": the quotation has " and the life", the KJV has ", and the life: he that b"`.
2. **Model judge** (`tools/judge.py`): eight anchored rubric lines (EX-2.2), evidence quoted for every score (TRK-2.2), a pass threshold, a different model from the maker, no tools, and the unit fenced as data.
3. **A person** (`review.sh`): every unit's doctrine, before it counts.

**Protected** (DANGER, exit 5, if any changes during a run): `kjv/`, `tools/`, `PROMPT.md`, `TEMPLATE.md`, `JUDGE.md`, `rubric.md`, `plan.md`, this file, `loop.env`, `units.tsv`, the four scripts, and every unit except the one being written (HCK-2.1).

### CALC-1 · Verifier Trust
Trust = p·S ÷ (p·S + (1 − p)·F)

- **The deterministic checker, measured.** Its test suite (`tests/test_checker.py`) holds known-good and known-bad work: 19 known-good cases, all passed (S = 19 ÷ 19 = 1.0), including the real John 2 unit; and 36 known-bad cases (misquoted Scripture, near misses in single quotes, dropped verses, invented references, wrong Greek, unbacked counts, self-grading, garbage), none passed (F = 0 ÷ 36 = 0). With F = 0, trust in its PASS is 1.0 for any p: p·1.0 ÷ (p·1.0 + (1 − p)·0) = 1.0. **Band: 95%+.** Its blind spot is what it doesn't measure: a paraphrase written without quotation marks, or a wrong interpretation. Those belong to the judge and to you.
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
| CAP | **4 iterations** per run (CALC-2) · 120 minutes per run · **$6.00 per maker call and $1.00 per judge call** (`--max-budget-usd`), so a unit's ceiling is 4 × $7.00 = **$28.00** · a maker call is stopped after 30 minutes, a judge call after 10 |
| STUCK | the same checker result (or the same judge scores) **twice in a row** (CS-2: the same mismatch twice) |
| DANGER | a protected file changes (the list under CHECKER). A tool the maker isn't allowed is refused outright and counted in its log line (two in the shakedown: a shell `for` loop and a `grep`). |
| HUMAN | `.loop-stop` exists · 3 drafts are waiting for review (no new unit starts) · every unit waits for your approval |

### CALC-2 · Tries-to-Success
Planning assumption until the log says otherwise: p = 0.6, the share of units passing the checker and the judge on a given try (CS-2's figure; replace it with the measured rate after five units, TRK-6.2). C = 0.95, because a failed unit wastes a run.

tries = ⌈ln(1 − C) ÷ ln(1 − p)⌉ = ⌈ln(0.05) ÷ ln(0.4)⌉ = ⌈−2.996 ÷ −0.916⌉ = ⌈3.27⌉ = **4 tries**. Check: 1 − 0.4⁴ = 1 − 0.0256 = **0.974**; with 3 tries, 1 − 0.064 = 0.936, which falls short. Average tries used with a cap of 4: (1 − 0.4⁴) ÷ 0.6 = **1.62**.

### CALC-3 · Loop Budget
Measured on the shakedown run (John 2, the shortest chapter at 25 verses), with the list prices of the models those aliases pointed to in the build environment (from the Claude API reference bundled with Claude Code, cached 2026-06-24; ⚠VERIFY on the pricing page, because an alias moves to each new model and prices change). Claude Code caches prompts for an hour, so input comes in three kinds, each with its own price:

| Price per million tokens | Uncached input | Cache write (1 hour) | Cache read | Output |
|---|---|---|---|---|
| Maker (the `opus` alias) | $4.00 | $8.00 | $0.20 | $20.00 |
| Judge (the `sonnet` alias) | $2.00 | $4.00 | $0.20 | $10.00 |

**Cost per iteration = (uncached × Pin + cache writes × Pwrite + cache reads × Pread + Tout × Pout) ÷ 1,000,000**, the guide's formula with the input split by kind. The measured calls (`cost-log.csv`), recomputed:

| Call | Uncached | Cache writes | Cache reads | Output | Arithmetic | Cost |
|---|---|---|---|---|---|---|
| Maker, iteration 1 (the first draft, 45 turns, 9.5 min) | 56 | 156,211 | 2,561,192 | 55,029 | (56×4 + 156,211×8 + 2,561,192×0.20 + 55,029×20) ÷ 10⁶ | **$2.86** |
| Judge, iteration 1 | 0 | 29,469 | 0 | 10,850 | (29,469×4 + 10,850×10) ÷ 10⁶ | **$0.23** |
| Maker, iteration 2 (one fix, 10 turns, 0.4 min) | 16 | 8,963 | 304,977 | 1,945 | (16×4 + 8,963×8 + 304,977×0.20 + 1,945×20) ÷ 10⁶ | **$0.17** |
| Judge, iteration 2 | 2 | 24,375 | 5,100 | 8,392 | (2×2 + 24,375×4 + 5,100×0.20 + 8,392×10) ÷ 10⁶ | **$0.18** |

Each result matches the `total_cost_usd` that Claude Code reported for that call.

- **This unit:** $2.86 + $0.23 + $0.17 + $0.18 = **$3.44** in **13 minutes**, DONE on iteration 2.
- **Typical unit (estimate):** the first draft dominates, and it grows with the chapter. Scaling by verses, $3.44 ÷ 25 = $0.138 per verse; John averages 879 ÷ 21 = 41.9 verses per chapter, so **about $5.76 per unit**, and about $9.78 for John 6 (71 verses). An estimate from one unit; re-measure after five.
- **Ceiling per unit** (the hard caps; the most a unit can cost if every try fails): N × (maker cap + judge cap) = 4 × ($6.00 + $1.00) = **$28.00**.
- **The whole study (22 units), typical:** $0.138 × (879 verses + 41.9 for the overview) ≈ **$127**. Ceiling: 22 × $28.00 = **$616**.
- **Monthly, at R = 8 units a month** (two a week): typical 8 × $5.76 ≈ **$46**; ceiling 8 × $28.00 = **$224**. Set spend alerts at 50% and 80% of the ceiling you choose (TIP-6.3).
- **Time ceiling:** the run stops starting iterations after 120 minutes; with a 30-minute maker cap and a 10-minute judge cap, the worst case is 120 + 40 = **160 minutes**.

On a Claude subscription, `claude -p` usage counts against the plan's limits rather than a bill; the dollars then measure how much of the plan a unit uses ⚠VERIFY.

## 9 · ESCALATION
When a run stops with CAP, STUCK, or DANGER, `tools/state.py escalate` writes `reviews/john-NN.escalation.md`, and the unit goes to `stuck` until a person runs `./review.sh reset NN`. The note has the guide's five parts (EX-3.2): the goal; the stop family and the rule that fired; what the maker tried (its log lines); the evidence (the last checker report, the judge's verdict, the last log rows); and the maker's best guess, marked as a guess. It ends with what the person can do next.

---

## CALC-4 · Loop Scorecard
Rated after the shakedown run and the dry runs, as a skeptical reviewer would.

| # | Criterion | Rating | Why, and what would raise it |
|---|---|---|---|
| 1 | Goal & done condition | 5 | An end state a script checks; DONE, and four failure exits, all demonstrated |
| 2 | Checker | 4 | Deterministic checker measured at S = 19/19 and F = 0/36; a separate judge on another model, which caught a real error the script couldn't; a person on every unit. **Not 5:** the judge isn't calibrated on your own graded sample yet (FIELD WORK 1) |
| 3 | Stop rules & budget | 5 | All five families, each demonstrated in a dry run; the cap from CALC-2; per-call dollar caps; time caps; ceilings from CALC-3 with measured costs |
| 4 | Safety | 4 | Its own branch (enforced), least privilege (verified: two refused calls in the shakedown), protected files (DANGER demonstrated), no network, a stop file, dry run by default. **Not 5:** it runs on your machine, not in a disposable container (HCK-4.1) |
| 5 | State & memory | 5 | Ledger, decisions, reviews, logs, and commits in files; every iteration is a fresh session that resumes from them (iteration 2 fixed exactly the judge's first fix) |
| 6 | Observability | 4 | A row per iteration (the workbook's Run Log columns) and a row per Claude call with tokens and dollars; escalation notes. **Not 5:** no alert when a scheduled day has no rows (AVD-5.3); only one unit measured so far |
| 7 | Human touchpoints | 5 | Rung 2 stated; approve, revise, and reset; a five-part escalation note; the review checkpoint; the proposals channel |
| 8 | Reusability | 4 | This spec, versioned, with a changelog; the kit's `loop.sh` unchanged; reproducible data builds. **Not 5:** the unit plan and some checks are specific to John |

**Score = 3 × (r1 + r2 + r3 + r4) + 2 × (r5 + r6 + r7 + r8) = 3 × (5 + 4 + 5 + 4) + 2 × (5 + 4 + 5 + 4) = 3 × 18 + 2 × 18 = 54 + 36 = 90 / 100: hero-grade.**

For comparison, the guide's CS-2 workbook loop scored 86. The score raises confidence in the drafts, not the loop's permissions: this loop stays at rung 2. The cheapest path to a higher score is FIELD WORK 1 (calibrate the judge: checker to 5) and alerts on the run log (observability to 5).

## FIELD WORK before unattended runs
1. **Calibrate the judge:** grade 10 units you'd accept and 10 you'd reject, run the judge on all 20, and put S and F into CALC-1 (`rubric.md`, "Calibration").
2. **Check prices and plan limits** on Anthropic's pricing page and your plan ⚠VERIFY, and redo CALC-3 with them.
3. **Confirm the model aliases:** `claude -p --model opus --output-format json "Reply OK"` shows the model under `modelUsage` ⚠VERIFY.
4. **Check the text against your own Bible** for the verses you teach; `kjv/variants.tsv` shows every verse where the sources differed; `kjv/errata.tsv` takes your corrections.
5. **Replace p = 0.6** with the measured pass rate after five units, and recompute the cap (TRK-6.2).
6. **Name the owner** in the header, and set a review date in the registry row below.

## ⚠VERIFY
- Claude Code flags used by the scripts, checked on Claude Code 2.1.282 in the build environment: `-p`, `--model`, `--effort`, `--output-format json`, `--json-schema`, `--max-budget-usd`, `--permission-mode dontAsk`, `--allowedTools` with path and command patterns, `--disallowedTools`, `--tools ""`, `--setting-sources`, `--strict-mcp-config`, `--disable-slash-commands`, `--no-session-persistence`. Re-check after a Claude Code update.
- Prices: from the Claude API reference bundled with Claude Code (cached 2026-06-24). Check the current pricing page.
- The KJV edition: the 1769 standard text as modern printings have it (`kjv/SOURCE.md`); a particular printed Bible may differ in a handful of places.

## Registry row (TIP-6.2)
| Loop | Version | Owner | Rung | Monthly ceiling | Review by |
|---|---|---|---|---|---|
| john-kjv-study | v1.0 | (you) | 2 | $224.00 at 8 units a month | 2026-12-01 |

## Climbing the ladder
This loop stays at rung 2: a person approves every unit's doctrine. What can grow is the **trigger**. After five units in a row are approved without a revise, and the judge is calibrated at 95% or more, a person may let it run three units back to back unattended (the review checkpoint still stops it). Record that decision here.

## Changelog
| Version | Date | What changed, and why |
|---|---|---|
| v0.9 | 2026-09-24 | First complete design: the nine boxes, the checker and its tests, the judge, the runner on the kit's `loop.sh`, and dry runs of all five stop families. Built with the guide's ten-step checklist. |
| v1.0 | 2026-09-24 | After the shakedown run on John 2 (DONE on iteration 2, $3.44, 13 minutes; the judge caught an arithmetic slip, 120–180 gallons for 108–162, that no script could see). Six findings folded in (SF-1 to SF-6, below). Approved by: the builder, pending the owner's review. |

**Shakedown findings (SF), the outer loop at work:**
- **SF-1 · No single free KJV was clean.** The first pinned transcription read 'and hundred' at John 21:11, 'reach' at John 20:27, and 'others' at John 19:18. Fix: a four-source consensus text with every disputed verse audited (`kjv/SOURCE.md`).
- **SF-2 · Two numbering systems.** STEP numbers some forms apart from traditional Strong's: *oida* (G6063, John 21:15) is filed under *oida* (G1492, John 21:15) in Strong's own numbering. Fix: the lexicon links them, and a citation may use either.
- **SF-3 · The builder misquoted too.** Checked by the loop's own rules, the first draft of `plan.md` misquoted John 13:19 and put 'the true vine' in John 15:5. Fix: `tests/check_docs.py` now holds every design document to the loop's rules.
- **SF-4 · Scripture in single quotes went unchecked.** The maker quoted short KJV phrases in single quotation marks (every one was exact, but nothing enforced it). Fix: SCRIPTURE-NEARMISS fails any single-quoted phrase of five or more words that is close to a verse without matching it.
- **SF-5 · The maker's own proposal** (`proposals/prompt-upgrades.md`): whole-verse cross-references silently count toward a Key Verses limit, and 'John 2:20, 46 years' was read as a reference to a 46th verse of John 2. Fix: both noted in `TEMPLATE.md`, and the checker no longer reads a number followed by an ordinary word as a verse.
- **SF-6 · Never edit a running loop.** The builder edited `tools/check_study.py` during the live run; the DANGER fingerprint would have stopped the loop at the end of the iteration, and the edit was reverted in time. Rule: change the loop only between runs (README, 'Changing the loop').
