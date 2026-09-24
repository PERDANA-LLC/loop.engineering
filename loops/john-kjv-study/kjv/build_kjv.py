#!/usr/bin/env python3
"""Rebuild kjv/kjv.tsv, the loop's only source of Scripture text.

The loop never quotes Scripture from memory. Every quotation in a study is checked,
word for word and punctuation for punctuation, against kjv/kjv.tsv. This script is
how that file was made, so anyone can rebuild it and compare.

Why four sources? No single free digital KJV turned out to be clean. Compared verse
by verse, each transcription of the 1769 standard text has its own slips. One reads
"and hundred and fifty and three" at John 21:11 where the others read "an hundred";
one keeps the 1769 spellings "your's" and "their's" that modern printings dropped;
one carries marginal notes inside verses. So each verse takes the reading that the
most sources share. Ties go to the source with the fewest outliers (farskipper),
then thiagobodruk, then open-bibles, then scrollmapper. kjv/errata.tsv, which only
a person edits, can then override any verse. Every verse where the three strongest
sources don't agree is written to kjv/variants.tsv so a person can audit the choice.

All four sources are public domain. Each is pinned to a commit and a sha256.

Normalization (applied to every source before the vote): italics markers and
paragraph marks removed (the words stay), curly apostrophes made straight, the
ae ligature written as "ae", runs of spaces collapsed, no space before punctuation.

Usage:
  python3 kjv/build_kjv.py              # download the pinned sources, verify, rebuild
  python3 kjv/build_kjv.py --cache DIR  # reuse (or fill) a download cache folder
  python3 kjv/build_kjv.py --check      # rebuild in memory; exit 1 if kjv.tsv differs
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "kjv.tsv")
VARIANTS = os.path.join(HERE, "variants.tsv")
ERRATA = os.path.join(HERE, "errata.tsv")

SOURCES = {
    # name: (url at a pinned commit, sha256)
    "farskipper": (
        "https://raw.githubusercontent.com/farskipper/kjv/8f06584d580a767425d7d4b4c314b967e6d45ab5/json/verses-1769.json",
        "43fbd2fd6a7aebaf62c0c828a85072336143c1fe8233a4856a12db1d5e5df470"),
    "thiagobodruk": (
        "https://raw.githubusercontent.com/thiagobodruk/bible/093b4727bf632181c9e096f4cf4141cc387371d0/json/en_kjv.json",
        "fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b"),
    "openbibles": (
        "https://raw.githubusercontent.com/seven1m/open-bibles/f257a3559025c3f873b48a75019f53a9354ed7de/eng-kjv.osis.xml",
        "eeeae647fc28360ce47f9c0d5cc3b397b7fdd9913fe53dc9f44eb6deee50e253"),
    "scrollmapper": (
        "https://raw.githubusercontent.com/scrollmapper/bible_databases/e1b254cef86d0e65b1a5d1a94b8b112d0f296a2c/formats/csv/KJV.csv",
        "a1051b4395bee78d01e239984425f3919563db5caee6fc162d4ddc7faff7eaa8"),
}
TIE_ORDER = ["farskipper", "thiagobodruk", "openbibles", "scrollmapper"]

# (OSIS id, the name the loop uses in references)
BOOKS = [
    ("Gen", "Genesis"), ("Exod", "Exodus"), ("Lev", "Leviticus"), ("Num", "Numbers"),
    ("Deut", "Deuteronomy"), ("Josh", "Joshua"), ("Judg", "Judges"), ("Ruth", "Ruth"),
    ("1Sam", "1 Samuel"), ("2Sam", "2 Samuel"), ("1Kgs", "1 Kings"), ("2Kgs", "2 Kings"),
    ("1Chr", "1 Chronicles"), ("2Chr", "2 Chronicles"), ("Ezra", "Ezra"), ("Neh", "Nehemiah"),
    ("Esth", "Esther"), ("Job", "Job"), ("Ps", "Psalms"), ("Prov", "Proverbs"),
    ("Eccl", "Ecclesiastes"), ("Song", "Song of Solomon"), ("Isa", "Isaiah"), ("Jer", "Jeremiah"),
    ("Lam", "Lamentations"), ("Ezek", "Ezekiel"), ("Dan", "Daniel"), ("Hos", "Hosea"),
    ("Joel", "Joel"), ("Amos", "Amos"), ("Obad", "Obadiah"), ("Jonah", "Jonah"),
    ("Mic", "Micah"), ("Nah", "Nahum"), ("Hab", "Habakkuk"), ("Zeph", "Zephaniah"),
    ("Hag", "Haggai"), ("Zech", "Zechariah"), ("Mal", "Malachi"),
    ("Matt", "Matthew"), ("Mark", "Mark"), ("Luke", "Luke"), ("John", "John"),
    ("Acts", "Acts"), ("Rom", "Romans"), ("1Cor", "1 Corinthians"), ("2Cor", "2 Corinthians"),
    ("Gal", "Galatians"), ("Eph", "Ephesians"), ("Phil", "Philippians"), ("Col", "Colossians"),
    ("1Thess", "1 Thessalonians"), ("2Thess", "2 Thessalonians"), ("1Tim", "1 Timothy"),
    ("2Tim", "2 Timothy"), ("Titus", "Titus"), ("Phlm", "Philemon"), ("Heb", "Hebrews"),
    ("Jas", "James"), ("1Pet", "1 Peter"), ("2Pet", "2 Peter"), ("1John", "1 John"),
    ("2John", "2 John"), ("3John", "3 John"), ("Jude", "Jude"), ("Rev", "Revelation"),
]
NAMES = [name for _, name in BOOKS]


def normalize(s):
    s = s.replace("’", "'").replace("‘", "'").replace("¶", "")
    s = s.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
    s = re.sub(r"^#\s*", "", s.strip())
    s = s.replace("Æ", "Ae").replace("æ", "ae")
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r" ([,;:.?!)])", r"\1", s)


def fetch(name, cache):
    url, sha = SOURCES[name]
    path = os.path.join(cache, name) if cache else None
    if path and os.path.exists(path):
        data = open(path, "rb").read()
    else:
        print(f"downloading {name}: {url}", file=sys.stderr)
        data = urllib.request.urlopen(url, timeout=180).read()
        if path:
            os.makedirs(cache, exist_ok=True)
            open(path, "wb").write(data)
    got = hashlib.sha256(data).hexdigest()
    if got != sha:
        sys.exit(f"{name}: sha256 mismatch (got {got}, pinned {sha})")
    return data


def parse_farskipper(data):
    out = {}
    for key, text in json.loads(data.decode("utf-8")).items():
        m = re.match(r"^(.*) (\d+):(\d+)$", key)
        book = {"Solomon's Song": "Song of Solomon"}.get(m.group(1), m.group(1))
        out[(book, int(m.group(2)), int(m.group(3)))] = text
    return out


def parse_thiagobodruk(data):
    out = {}
    for bi, book in enumerate(json.loads(data.decode("utf-8-sig"))):
        for ci, chapter in enumerate(book["chapters"]):
            for vi, text in enumerate(chapter):
                out[(NAMES[bi], ci + 1, vi + 1)] = text
    return out


def parse_openbibles(data):
    names = dict(BOOKS)
    t = data.decode("utf-8")
    t = re.sub(r"<title\b[^>]*>.*?</title>", " ", t, flags=re.S)   # book and psalm titles
    t = re.sub(r"<note\b[^>]*>.*?</note>", " ", t, flags=re.S)
    out = {}
    for m in re.finditer(r'<verse osisID="([^"]+)" sID="([^"]+)"[^>]*/>', t):
        book, ch, vs = m.group(1).split(".")
        if book not in names:
            continue   # Apocrypha: outside this loop's canon
        end = t.find(f'<verse eID="{m.group(2)}"', m.end())
        text = re.sub(r"<[^>]+>", " ", t[m.end():end])
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        out[(names[book], int(ch), int(vs))] = text
    return out


def parse_scrollmapper(data):
    out = {}
    rows = csv.reader(io.StringIO(data.decode("utf-8")))
    next(rows)
    for book, ch, vs, text in rows:
        book = re.sub(r"^(III|II|I) ", lambda m: {"I": "1", "II": "2", "III": "3"}[m.group(1)] + " ", book)
        book = {"Revelation of John": "Revelation"}.get(book, book)
        out[(book, int(ch), int(vs))] = text
    return out


PARSERS = {"farskipper": parse_farskipper, "thiagobodruk": parse_thiagobodruk,
           "openbibles": parse_openbibles, "scrollmapper": parse_scrollmapper}


def load_errata():
    fixes = {}
    if os.path.exists(ERRATA):
        for line in open(ERRATA, encoding="utf-8").read().splitlines():
            if not line.strip() or line.startswith("#") or line.startswith("book\t"):
                continue
            book, ch, vs, text, _why = line.split("\t", 4)
            fixes[(book, int(ch), int(vs))] = text
    return fixes


def build(cache):
    texts = {name: {k: normalize(v) for k, v in PARSERS[name](fetch(name, cache)).items()}
             for name in TIE_ORDER}
    keys = list(texts["farskipper"].keys())
    order = {name: i for i, name in enumerate(NAMES)}
    keys.sort(key=lambda k: (order[k[0]], k[1], k[2]))
    for name, t in texts.items():
        if set(t) != set(keys):
            sys.exit(f"{name}: verse list differs from farskipper ({len(t)} vs {len(keys)})")
    errata = load_errata()
    rows, variants = [], []
    for k in keys:
        readings = {name: texts[name][k] for name in TIE_ORDER}
        votes = collections.Counter(readings.values())
        top = max(votes.values())
        chosen = next(readings[n] for n in TIE_ORDER if votes[readings[n]] == top)
        how = "unanimous" if len(votes) == 1 else f"plurality {top}/4"
        if k in errata:
            chosen, how = errata[k], "errata"
        rows.append((*k, chosen))
        strong = [readings[n] for n in TIE_ORDER[:3]]
        if len(set(strong)) > 1 or how == "errata":
            variants.append((*k, how, chosen, *(readings[n] for n in TIE_ORDER)))
    tsv = "book\tchapter\tverse\ttext\n" + "".join(f"{b}\t{c}\t{v}\t{t}\n" for b, c, v, t in rows)
    var = ("book\tchapter\tverse\tdecision\tchosen\t" + "\t".join(TIE_ORDER) + "\n"
           + "".join("\t".join(str(x) for x in r) + "\n" for r in variants))
    return tsv, var, len(rows)


def main():
    ap = argparse.ArgumentParser(description="Rebuild kjv/kjv.tsv from pinned public-domain sources")
    ap.add_argument("--cache", help="folder for downloaded sources (reused when present)")
    ap.add_argument("--check", action="store_true", help="exit 1 if kjv.tsv differs from a fresh build")
    a = ap.parse_args()
    tsv, var, n = build(a.cache)
    if a.check:
        same = (open(OUT, encoding="utf-8").read() == tsv and
                open(VARIANTS, encoding="utf-8").read() == var)
        print(f"kjv.tsv and variants.tsv {'match' if same else 'DIFFER FROM'} a fresh build ({n} verses)")
        sys.exit(0 if same else 1)
    open(OUT, "w", encoding="utf-8").write(tsv)
    open(VARIANTS, "w", encoding="utf-8").write(var)
    print(f"wrote kjv.tsv ({n} verses, sha256 {hashlib.sha256(tsv.encode()).hexdigest()}) "
          f"and variants.tsv ({var.count(chr(10)) - 1} rows)")


if __name__ == "__main__":
    main()
