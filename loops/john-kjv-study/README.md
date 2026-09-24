# The John KJV Study Loop

A Claude loop that writes an in-depth King James Version study of the Gospel of John, one unit at a time, checks every word of Scripture against the KJV text, and hands each unit to a person for doctrine review. It was designed with the guide in [`docs/loop-engineering`](../../docs/loop-engineering/README.md), following its ten-step build checklist, and it runs on the guide's own [`kit/loop.sh`](../../docs/loop-engineering/kit/loop.sh), copied here unchanged.

**What it produces:** 22 units in `study/`. `john-00.md` is the book overview; `john-01.md` to `john-21.md` cover John's chapters. Each unit follows **bs3 v3.1**, the TONA Bible Study Flywheel: a passage map, the Christological Root, then three tiers (Easy, Medium, Expert). It adds a **verse-by-verse walkthrough** that covers every verse of the chapter. Together the units make a commentary and a teaching guide. The first unit, John 2, was written by the loop itself during the shakedown run: [`study/john-02.md`](study/john-02.md).

**The one-page design** is [`LOOP-SPEC.md`](LOOP-SPEC.md): the nine boxes, the four calculators with their arithmetic, the score, and the changelog.

---

## How one run works

```text
./run.sh --real
  └─ picks the next unit from units.tsv; refuses to run on main; fingerprints the protected files
     └─ loop.sh (the kit's runner): up to 4 iterations, stopping on DONE, CAP, STUCK, HUMAN, or DANGER
        ├─ MAKER  tools/maker.py → a fresh `claude -p` session (Opus) reads PROMPT.md and the files,
        │         writes or fixes study/john-NN.md; it may write only that file and run only the lookup tools
        └─ CHECK  check.sh
                  ├─ 1. tools/check_study.py   exact KJV quotations, every verse covered, Greek citations,
                  │                            counts, bs3 structure (free, deterministic)
                  └─ 2. tools/judge.py         a separate `claude -p` session (Sonnet, no tools) grades
                                               the unit against rubric.md; the script applies the pass rule
  └─ DONE → the unit waits for you:  ./review.sh approve NN "Your Name"   or   ./review.sh revise NN "notes"
     anything else → reviews/john-NN.escalation.md tells you why it stopped and what it tried
```

Whatever the checker or the judge finds becomes the maker's next prompt. The maker never decides it's done: the checker, the judge, and you do.

---

## Quick start

**1 · Dry run first (free, changes nothing).** It copies the folder to a throwaway directory, plays the maker with fixtures, and runs the real checker, so you can watch every stop rule work:

```bash
cd loops/john-kjv-study
./run.sh                    # DONE on iteration 2: a flawed draft, then a fixed one (exit 0)
MOCK=stuck ./run.sh         # the same mistake twice: STUCK (exit 3), with an escalation note
MOCK=cap ./run.sh           # a new mistake every time: CAP after 4 iterations (exit 2)
MOCK=tamper ./run.sh        # the maker edits the KJV text: DANGER (exit 5)
MOCK=stopfile ./run.sh      # the stop file is present: HUMAN (exit 4)
MOCK=judge-fail ./run.sh    # the checker passes but the judge never does: STUCK (exit 3)
```

(During a dry run, `loop.sh` announces itself as "real": it's running this loop's mock maker and the real checker, rather than its own built-in mock. `run.sh` says "dry run" on the line before.)

**2 · Run it for real, on its own branch.** You need Claude Code (`claude`) signed in, and Python 3.

```bash
git switch -c loop/john-kjv     # run.sh refuses to run on main or master
./run.sh --real                 # writes, checks, and judges the next unit (John 2 took 13 minutes)
./run.sh status                 # where every unit stands
```

**3 · Review each unit.** Nothing counts until you approve it. Read `study/john-NN.md` and the judge's scores in `reviews/john-NN.judge.md`, then:

```bash
./review.sh approve 00 "Your Name"        # or:
./review.sh revise 00 'In Tier 3, the word study on 1:1 claims too much; soften it'
```

**4 · Keep going.** Run units one at a time, or a few in a row. The loop stops by itself when three drafts are waiting for your review:

```bash
for i in 1 2 3; do ./run.sh --real || break; done
```

**Stop it at any time:** `touch .loop-stop` in this folder (it stops before the next iteration), or Ctrl+C.

---

## What checks what

| Check | Who | What it catches |
|---|---|---|
| Every quotation is exact KJV | `tools/check_study.py`, against `kjv/kjv.tsv` | A dropped comma, a changed word, a modern translation, a quotation without a reference |
| Every reference exists | the same | ❌ `John 22:1`, `Psalm 151`, a verse past the end of a chapter |
| Every verse is covered | the same | Gaps, overlaps, blocks longer than 6 verses, a block that never quotes its own text |
| bs3 structure and counts | the same | Missing sections; 3–5 whole verses in Tier 1, 5–8 in Tier 2, 8+ in Tier 3; 4–5 diagnostic questions, and so on |
| Greek and Hebrew citations | the same, against the Textus Receptus word index | A Strong's number that isn't in the verse cited, a misspelled word, a wrong parsing, an uncited Greek word |
| Counts | the same, by recounting | ❌ 'Believe occurs 98 times', when the KJV of John has 101 words starting believ- and the Greek *pisteuō* (G4100, John 20:31) occurs 100 times in John's Textus Receptus |
| Faithfulness, depth, tiers, honesty about sources | the judge, `rubric.md` | What a script can't see: misreadings, thin exposition, overclaiming, tiers that read alike |
| Doctrine | **you**, `review.sh` | Everything the loop must never decide on its own |

The checker's own tests are in [`tests/`](tests/): `python3 tests/test_checker.py` (33 tests: 19 known-good and 36 known-bad cases) and `python3 tests/check_docs.py`, which holds these documents to the same rules.

---

## Before a real run: the safety checklist

This is the kit's checklist, filled in for this loop.

- [x] **Its own branch.** `run.sh` refuses `main` and `master`, and commits each iteration with its check result (set `COMMIT=0` to skip).
- [x] **Caps from the calculators.** 4 iterations per unit (CALC-2), 120 minutes per run, and hard dollar caps per Claude call (`--max-budget-usd`: $6.00 for the maker, $1.00 for the judge). The worst a unit can cost is 4 × ($6.00 + $1.00) = $28.00; typical costs are in `LOOP-SPEC.md` (CALC-3).
- [x] **Protected checker files.** The KJV text, the Greek data, the tools, the prompts, the plan, the settings, the ledger, and every other unit are fingerprinted; any change stops the run with DANGER (exit 5).
- [x] **Least privilege, verified.** The maker may write only its own unit file (plus notes in `progress.md` and `proposals/`) and run only `python3 tools/…` lookups. `--permission-mode dontAsk` refuses anything else. Your personal Claude Code settings, MCP servers, and skills are not loaded (`--setting-sources project,local --strict-mcp-config --disable-slash-commands`), so nothing you've allowed elsewhere widens what the loop may do. No web, no git, no network for the maker.
- [x] **No permission-skipping flags anywhere.**
- [x] **No secrets.** The loop needs none; your Claude Code sign-in stays where it is.
- [x] **A known off switch:** `.loop-stop` or Ctrl+C.
- [x] **The right rung.** Rung 2 (suggest): the loop drafts, you approve. Teaching Scripture to others is a person's responsibility, so this loop stays at rung 2 however good its numbers get (CS-2 in the guide).

---

## Files

| Path | What it is | Who writes it |
|---|---|---|
| `LOOP-SPEC.md` | The nine-box design, calculators, score, changelog | A person |
| `PROMPT.md` | The maker's prompt, the same on every run | A person (protected) |
| `TEMPLATE.md` | The unit format (bs3 plus the walkthrough) and the rules the checker enforces | A person (protected) |
| `plan.md` | The 22 units, their focus, and the study-wide decisions | A person (protected) |
| `rubric.md`, `JUDGE.md` | The judge's anchored rubric and instructions | A person (protected) |
| `loop.env` | Models, caps, budgets, the review checkpoint | A person (protected) |
| `run.sh`, `check.sh`, `review.sh`, `loop.sh` | The runner, the check command, your checkpoint, the kit's loop | A person (protected) |
| `tools/` | The checker, lookup tools (`verse.py`, `greek.py`, `lexicon.py`, `concordance.py`), maker, judge, ledger | A person (protected) |
| `kjv/` | The KJV text, the Greek word index, the lexicon, and how they were built ([`kjv/SOURCE.md`](kjv/SOURCE.md)) | Rebuilt by script; errata by a person |
| `study/` | The units | The maker |
| `reviews/` | Each unit's checker report, judge verdict, your notes, and any escalation | The scripts, and you |
| `units.tsv` | The ledger: every unit's status | The scripts only |
| `progress.md` | Decisions to follow, and one log line per iteration | The maker appends; a person decides |
| `proposals/prompt-upgrades.md` | The maker's suggestions for improving the prompts (bs3's Step C, made safe) | The maker proposes; a person decides |
| `loop-log.csv`, `cost-log.csv` | One row per iteration (the workbook's Run Log columns); one row per Claude call with tokens and cost | The scripts |
| `tests/` | The checker's tests and fixtures, and the documents check | A person |

## Looking things up by hand

The maker's lookup tools work for you too:

```bash
python3 tools/verse.py "John 3:16-18"              # exact KJV text
python3 tools/greek.py "John 21:15"                # the Greek words of a verse, with Strong's numbers and parsing
python3 tools/lexicon.py G5368                     # a lexicon entry
python3 tools/concordance.py "abide" "John 15" --list   # counts, with the verses
python3 tools/check_study.py 02                    # check a unit yourself
```

## Changing the loop

Change one thing at a time, and record it in `LOOP-SPEC.md`'s changelog with the reason and the result (BP-5.2). Run `./run.sh` (dry) after every change (BP-4.2). If you change `rubric.md`, `JUDGE.md`, or a model, re-calibrate the judge (FIELD WORK in `LOOP-SPEC.md`). The maker's ideas for improving the prompts collect in `proposals/prompt-upgrades.md`; try a promising one on a unit or two before adopting it (EX-6.1).
