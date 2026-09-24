# tests: checking the checker

A loop is only as good as its checker (Level 2 of the guide), so the checker has tests of its own.

| File | What it does |
|---|---|
| `test_checker.py` | Rule tests on small snippets (exact and inexact quotations, references, Greek citations, counts, empty and garbage files), and fixture tests: the good John 2 unit must pass, and every known-bad mutation of it must fail with the right code. `python3 tests/test_checker.py` |
| `check_docs.py` | Holds this folder's own documents to the loop's rules: every quotation, reference, Greek citation, and count in the Markdown files must pass. Fenced code blocks and lines marked ❌ (deliberate bad examples) are skipped. `python3 tests/check_docs.py` |
| `make_fixtures.py` | Makes the dry-run fixtures from a unit that passes the checker: `python3 tests/make_fixtures.py study/john-02.md` |
| `fixtures/john-02.good.md` | A unit that passes: the loop's own first unit, written during the shakedown run |
| `fixtures/john-02.flawed.md` | The same unit with one comma dropped from a quotation (the slip in CS-2's v1). The dry run plays it first. |

The fixture tests are also the loop's measured sample for CALC-1: every known-good case passes (S = 1.0) and no known-bad case passes (F = 0), which is why `LOOP-SPEC.md` puts the deterministic checker in the 95%+ band for what it measures.

Run everything after any change to `tools/` or `kjv/`:

```bash
python3 tests/test_checker.py && python3 tests/check_docs.py && ./run.sh
```
