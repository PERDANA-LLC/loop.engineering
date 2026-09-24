#!/usr/bin/env python3
"""Look up a Strong's number in the STEPBible.org brief lexicon (Tyndale House, Cambridge; CC BY 4.0), whose
Greek entries draw largely on G. Abbott-Smith, A Manual Greek Lexicon of the New Testament. Name it so when you cite it.

  python3 tools/lexicon.py G25
  python3 tools/lexicon.py H4908

Use the transliteration exactly as printed here (without any dots) in citations:
  *agapaō* (G25, John 21:15)      *mishkan* (H4908, Exodus 25:9)
"""
import sys

import kjvlib


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    entries = kjvlib.lexicon().get(kjvlib.strong_key(argv[0]))
    if not entries:
        print(f"NOT FOUND · {argv[0]} isn't in the lexicon", file=sys.stderr)
        return 1
    for e in entries:
        shown = kjvlib.display_translit(e)
        note = "" if shown == e["translit"].replace(".", "") else \
            f"  (the lexicon file reads '{e['translit']}', which doesn't match the Greek)"
        print(f"{e['strong']}  {e['lemma']}  translit: {shown}{note}  gloss: {e['gloss']}")
        print(f"    {e['definition']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
