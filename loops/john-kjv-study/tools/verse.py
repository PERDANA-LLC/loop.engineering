#!/usr/bin/env python3
"""Print the exact KJV text of one or more references, from kjv/kjv.tsv.

Quote Scripture only by copying from this output: never from memory.

  python3 tools/verse.py "John 3:16"
  python3 tools/verse.py "John 3:16-18" "Numbers 21:8-9"
  python3 tools/verse.py "John 3"            # a whole chapter
  python3 tools/verse.py --joined "John 3:16-17"   # one line, verses joined, ready to quote
  python3 tools/verse.py --read-mark "John 3"      # **1** text, one verse per paragraph, for Read & Mark
"""
import sys

import kjvlib


def main(argv):
    joined = "--joined" in argv
    read_mark = "--read-mark" in argv
    refs = [a for a in argv if a not in ("--joined", "--read-mark")]
    if not refs:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    status = 0
    for raw in refs:
        try:
            ref = kjvlib.parse_ref(raw)
        except kjvlib.RefError as e:
            print(f"NOT FOUND · {e}", file=sys.stderr)
            status = 1
            continue
        if joined:
            print(f'"{ref.text()}" ({ref})')
            continue
        if read_mark:
            print("\n\n".join(f"**{v}** {kjvlib.kjv()[(book, c, v)]}" for book, c, v in ref.verses()))
            continue
        for book, c, v in ref.verses():
            print(f"{book} {c}:{v}\t{kjvlib.kjv()[(book, c, v)]}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
