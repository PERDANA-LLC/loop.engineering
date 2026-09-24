#!/usr/bin/env python3
"""Hold the loop's own documents to the rules the loop enforces.

Every quotation, reference, Greek citation, and count in the Markdown files of this
folder (except study/, whose units the checker handles) must pass the same checks
as a study unit. Lines marked with a cross (the template's deliberate bad examples)
are skipped.

  python3 tests/check_docs.py        # exit 0 = every document passes
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_study as cs  # noqa: E402


def check_file(path):
    raw = open(path, encoding="utf-8").read()
    kept, fence = [], False
    for line in raw.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
            kept.append("")
            continue
        # fenced blocks hold commands and skeletons, not claims; a cross marks a deliberate bad example
        kept.append("" if fence or "❌" in line else line)
    body = cs.blank_comments("\n".join(kept))
    rep = cs.Report()
    cs.check_quotes(body, rep)
    cs.check_single_quotes(body, rep)
    cs.check_refs(body, rep)
    cs.check_greek(body, [], {}, rep)
    cs.check_counts("\n".join(kept), body, rep)
    return rep.items


def main():
    # The design documents a person writes. progress.md and proposals/ are the maker's working notes
    # (they quote its own drafts), and study/ is checked unit by unit by the checker itself.
    docs = sorted(set(glob.glob(os.path.join(ROOT, "*.md")) + glob.glob(os.path.join(ROOT, "kjv", "*.md"))
                      + glob.glob(os.path.join(ROOT, "tests", "*.md"))) - {os.path.join(ROOT, "progress.md")})
    failed = 0
    for path in docs:
        items = check_file(path)
        name = os.path.relpath(path, ROOT)
        if items:
            failed += 1
            for ln, code, msg in sorted(items):
                print(f"{name}:{ln}: {code}: {msg}")
        else:
            print(f"ok  {name}")
    print("docs: " + ("ALL PASS" if not failed else f"{failed} file(s) with problems"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
