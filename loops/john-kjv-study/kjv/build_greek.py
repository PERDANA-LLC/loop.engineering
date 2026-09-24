#!/usr/bin/env python3
"""Rebuild the Greek word index and the lexicon the loop checks word studies against.

Why: a word study can go wrong in quiet ways (a wrong Strong's number, a word that
isn't in the verse, a wrong parsing). The loop treats those like misquoted verses:
the maker looks words up with tools/greek.py and tools/lexicon.py, and the checker
confirms every citation against these files.

Source: STEPBible.org data (Tyndale House, Cambridge), CC BY 4.0, pinned to a
commit and a sha256 in SOURCES below:
  * TAGNT: Translators Amalgamated Greek NT, word by word with Strong's numbers,
    morphology, lemmas, glosses, and which printed editions contain each word.
  * TBESG / TBESH: Translators Brief lexicons of Extended Strong's (Greek, Hebrew).

The KJV New Testament was translated from the Textus Receptus (TR), so only words
that TAGNT marks as present in the TR go into the index. Where the TR reads a
different word from the modern critical text (John 1:18 has "Son" where NA28 has
"God"), TAGNT lists the TR word as a variant, and the index takes that variant.

Outputs (gzipped TSV, read by tools/kjvlib.py):
  kjv/greek-nt.tsv.gz  ref, n, greek, translit, strongs, morphs, lemma, gloss, english, alt, src
  kjv/lexicon.tsv.gz   strong, lemma, translit, gloss, definition, form_of

Attribution (required by CC BY 4.0): data from STEPBible.org, Tyndale House Cambridge,
https://github.com/STEPBible/STEPBible-Data. Changed: filtered to TR words, columns
reduced, definitions shortened and stripped of markup.

Usage:
  python3 kjv/build_greek.py              # download the pinned files, verify, rebuild
  python3 kjv/build_greek.py --cache DIR  # reuse (or fill) a download cache folder
  python3 kjv/build_greek.py --check      # rebuild in memory; exit 1 if the outputs differ
"""
import argparse
import gzip
import hashlib
import html
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GREEK_OUT = os.path.join(HERE, "greek-nt.tsv.gz")
LEX_OUT = os.path.join(HERE, "lexicon.tsv.gz")

COMMIT = "b99716b0cddb648ddb95cc786a197180f2f97d48"
BASE = f"https://raw.githubusercontent.com/STEPBible/STEPBible-Data/{COMMIT}/"
SOURCES = {
    "tagnt-mat-jhn": ("Translators Amalgamated OT+NT/TAGNT Mat-Jhn - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
                      "ab8eaaeb68e17a1dcfa34e1e9350358f22f03bc2a97244d848750ad81044bc8e"),
    "tagnt-act-rev": ("Translators Amalgamated OT+NT/TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
                      "524e32375361e6d3fa2f7ef00b87605fdc4317a762f395651a05fdc31ad031b7"),
    "tbesg": ("Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt",
              "312f723d7b8ef263bbdfb0451c9b8057125804dfff390b6f8544cff2a84b57f4"),
    "tbesh": ("Lexicons/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt",
              "464dccadd95fd8620dd05fa0d7a4caba58ec3c4d5db3ebf38e43d046ca25b591"),
}

BOOK = {
    "Mat": "Matthew", "Mrk": "Mark", "Luk": "Luke", "Jhn": "John", "Act": "Acts",
    "Rom": "Romans", "1Co": "1 Corinthians", "2Co": "2 Corinthians", "Gal": "Galatians",
    "Eph": "Ephesians", "Php": "Philippians", "Col": "Colossians", "1Th": "1 Thessalonians",
    "2Th": "2 Thessalonians", "1Ti": "1 Timothy", "2Ti": "2 Timothy", "Tit": "Titus",
    "Phm": "Philemon", "Heb": "Hebrews", "Jas": "James", "1Pe": "1 Peter", "2Pe": "2 Peter",
    "1Jn": "1 John", "2Jn": "2 John", "3Jn": "3 John", "Jud": "Jude", "Rev": "Revelation",
}

# Jhn.7.53{8.1}: another tradition's number in braces or parentheses; the main number is the KJV's.
# 2Co.13.13[13.14]: square brackets hold the KJV/English number, so it wins.
ROW = re.compile(r"^([1-3]?[A-Za-z]{2,3})\.(\d+)\.(\d+)(?:\{[^}]*\}|\([^)]*\)|\[(\d+)\.(\d+)\])?#(\d+)=\S*\t")
PAIR = re.compile(r"\b([GH]\d{4}[A-Za-z]?)=([A-Z0-9][A-Z0-9-]*)")
VARIANT = re.compile(r"^\s*(\S+)\s+\((?:[A-Za-z]=)?([^)]*)\)\s*(.*?)\s+-\s+(.+?)\s+in:\s*(\S+)\s*$")


def fetch(key, cache):
    path_in_repo, sha = SOURCES[key]
    local = os.path.join(cache, key) if cache else None
    if local and os.path.exists(local):
        data = open(local, "rb").read()
    else:
        url = BASE + urllib.parse.quote(path_in_repo)
        print(f"downloading {key}", file=sys.stderr)
        data = urllib.request.urlopen(url, timeout=300).read()
        if local:
            os.makedirs(cache, exist_ok=True)
            open(local, "wb").write(data)
    got = hashlib.sha256(data).hexdigest()
    if got != sha:
        sys.exit(f"{key}: sha256 mismatch (got {got}, pinned {sha})")
    return data.decode("utf-8-sig")


def clean_form(s):
    return re.sub(r"[\[\]¶.,;:··?!;'\"()«»—–]+", "", s).strip()


def split_form(cell):
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", cell)
    return (clean_form(m.group(1)), m.group(2).strip()) if m else (clean_form(cell), "")


def greek_rows(text):
    out = []
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        f = line.split("\t")
        book, ch, vs, n = BOOK[m.group(1)], int(m.group(2)), int(m.group(3)), int(m.group(6))
        if m.group(4):
            ch, vs = int(m.group(4)), int(m.group(5))
        ref = f"{book} {ch}:{vs}"
        editions = f[5].split("+")
        if "TR" in editions:
            greek, translit = split_form(f[1])
            pairs = PAIR.findall(f[3])
            lemma, _, gloss = f[4].partition("=")
            alt = " ".join(re.findall(r"[GH]\d{4}[A-Za-z]?", f[12])) if len(f) > 12 else ""
            out.append((ref, n, greek, translit, " ".join(p[0] for p in pairs),
                        " ".join(p[1] for p in pairs), lemma.split(" + ")[0].strip(),
                        gloss.strip(), f[2].strip(), alt, "tr"))
        else:
            # The printed TR reads another word here; TAGNT lists it as a variant.
            for part in f[6].split(";") if len(f) > 6 else []:
                v = VARIANT.match(part)
                if not v or "TR" not in v.group(5).split("+"):
                    continue
                pairs = PAIR.findall(v.group(4))
                out.append((ref, n, clean_form(v.group(1)), v.group(2).strip(),
                            " ".join(p[0] for p in pairs), " ".join(p[1] for p in pairs),
                            "", "", v.group(3).strip(), "", "tr-variant"))
    return out


def lexicon_rows(text):
    out = []
    for line in text.splitlines():
        f = line.split("\t")
        if len(f) < 8 or not re.match(r"^[GH]\d{4}", f[0]):
            continue
        dstrong, _, relation = (x.strip() for x in f[1].partition("="))
        if not re.match(r"^[GH]\d{4}[A-Za-z]?$", dstrong):
            continue
        # "G6063 = a Form of G1492H": STEP gives οἶδα its own number; traditional Strong's files it
        # under G1492. Keeping the link lets a citation use either number.
        form_of = f[2].strip() if relation == "a Form of" else ""
        definition = re.sub(r"<[^>]+>", " ", f[7])
        definition = re.sub(r"\s+", " ", html.unescape(definition)).strip()
        if len(definition) > 600:
            definition = definition[:600].rsplit(" ", 1)[0] + " ..."
        out.append((dstrong, f[3].strip(), f[4].strip(), f[6].strip(), definition, form_of))
    return out


def to_tsv(header, rows):
    clean = lambda x: str(x).replace("\t", " ").replace("\n", " ")
    return header + "\n" + "".join("\t".join(clean(x) for x in r) + "\n" for r in rows)


def build(cache):
    greek = greek_rows(fetch("tagnt-mat-jhn", cache)) + greek_rows(fetch("tagnt-act-rev", cache))
    lex = lexicon_rows(fetch("tbesg", cache)) + lexicon_rows(fetch("tbesh", cache))
    g = to_tsv("ref\tn\tgreek\ttranslit\tstrongs\tmorphs\tlemma\tgloss\tenglish\talt\tsrc", greek)
    x = to_tsv("strong\tlemma\ttranslit\tgloss\tdefinition\tform_of", lex)
    return g, x, len(greek), len(lex)


def gz(text):
    return gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0)


def main():
    ap = argparse.ArgumentParser(description="Rebuild kjv/greek-nt.tsv.gz and kjv/lexicon.tsv.gz")
    ap.add_argument("--cache", help="folder for downloaded sources (reused when present)")
    ap.add_argument("--check", action="store_true", help="exit 1 if the outputs differ from a fresh build")
    a = ap.parse_args()
    g, x, ng, nx = build(a.cache)
    if a.check:
        same = (gzip.open(GREEK_OUT, "rt", encoding="utf-8").read() == g and
                gzip.open(LEX_OUT, "rt", encoding="utf-8").read() == x)
        print(f"greek-nt and lexicon {'match' if same else 'DIFFER FROM'} a fresh build")
        sys.exit(0 if same else 1)
    open(GREEK_OUT, "wb").write(gz(g))
    open(LEX_OUT, "wb").write(gz(x))
    print(f"wrote greek-nt.tsv.gz ({ng} TR words) and lexicon.tsv.gz ({nx} entries)")


if __name__ == "__main__":
    main()
