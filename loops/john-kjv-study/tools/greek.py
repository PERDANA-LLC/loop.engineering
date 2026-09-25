#!/usr/bin/env python3
"""Show the Greek words (Textus Receptus, the text behind the KJV New Testament)
of a verse, with Strong's numbers, parsing, lemma, and gloss.

Cite a Greek word only after looking it up here, and cite it in this exact form:
  *agapaō* (G25, John 21:15)             transliteration, Strong's number, a verse where it occurs
  *agapas* (G25, John 21:15, V-PAI-2S)   the same, plus the parsing code when you discuss the form

  python3 tools/greek.py "John 21:15"
  python3 tools/greek.py "John 21:15-17" --strong G25
"""
import sys

import kjvlib


def main(argv):
    strong = None
    if "--strong" in argv:
        i = argv.index("--strong")
        strong = argv[i + 1] if i + 1 < len(argv) else None
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        ref = kjvlib.parse_ref(argv[0])
    except kjvlib.RefError as e:
        print(f"NOT FOUND · {e}", file=sys.stderr)
        return 1
    if ref.book not in kjvlib.NT_BOOKS:
        print("NOT FOUND · Greek words exist only for New Testament verses", file=sys.stderr)
        return 1
    shown = 0
    for book, c, v in ref.verses():
        key = f"{book} {c}:{v}"
        words = kjvlib.words_in(key, strong)
        if not words:
            continue
        print(f"{key}\t{kjvlib.kjv()[(book, c, v)]}")
        for w in words:
            strongs = " + ".join(kjvlib.strong_key(s) for s in w["strongs"].split())
            others = sorted(kjvlib.word_strongs(w) - {kjvlib.strong_key(s) for s in w["strongs"].split()})
            alt = f" (also numbered {' '.join(others)})" if others else ""
            morphs = " + ".join(f"{m} = {kjvlib.expand_morph(m)}" for m in w["morphs"].split())
            lemma = f"{w['lemma']} '{w['gloss']}'" if w["lemma"] else "(TR reading)"
            note = f"  (the data file reads '{w['translit_file']}', which doesn't match the Greek)" \
                if "translit_file" in w else ""
            print(f"  #{w['n']:>2}  {w['greek']} ({w['translit']})  {strongs}{alt}  {morphs}  "
                  f"lemma {lemma}  KJV-area gloss: {w['english']}{note}")
            shown += 1
    if not shown:
        print("NOT FOUND · no Textus Receptus word matches", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
