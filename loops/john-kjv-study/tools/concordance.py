#!/usr/bin/env python3
"""Count how often a word, phrase, or Greek word occurs, from the loop's own texts.

Any number you write before the word "times" must come from this tool, in this run,
and must be recorded in the study's counts block (the tool prints the exact line).

  python3 tools/concordance.py "believ*" John          # English, whole words; * matches any ending
  python3 tools/concordance.py "verily, verily" John
  python3 tools/concordance.py G4100 John              # a Greek word by Strong's number (Textus Receptus)
  python3 tools/concordance.py "abide" "John 15" --list
Scopes: a book (John), a chapter (John 15), NT, OT, or Bible.
"""
import sys

import kjvlib


def main(argv):
    listing = "--list" in argv
    argv = [a for a in argv if a != "--list"]
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    query, scope = argv
    try:
        total, hits = kjvlib.count(query, scope)
    except (kjvlib.RefError, ValueError) as e:
        print(f"NOT COUNTED · {e}", file=sys.stderr)
        return 1
    print(f"{total} occurrences in {len(hits)} verses")
    print(f"counts-block line:  {query.strip()} | {scope.strip()} | {total}")
    if listing:
        for key, n in hits:
            ref = key if isinstance(key, str) else f"{key[0]} {key[1]}:{key[2]}"
            print(f"  {ref} ({n})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
