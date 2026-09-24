#!/usr/bin/env python3
"""The deterministic checker for one unit of the John KJV study.

It answers PASS or NOT YET, never "probably fine". Its report is the maker's next
prompt, so every problem says what failed, where (line number), and what was
expected. Nothing here is the maker's opinion: quotations are compared with
kjv/kjv.tsv, Greek citations with kjv/greek-nt.tsv.gz and kjv/lexicon.tsv.gz,
and counts are recomputed.

  python3 tools/check_study.py 03                  # checks study/john-03.md
  python3 tools/check_study.py 03 --file draft.md  # checks another file as unit 03
Exit codes: 0 PASS · 1 NOT YET · 2 usage error (treated as NOT YET by check.sh)

What it checks (TEMPLATE.md explains each rule to the maker):
  TITLE, UNIT-LINE      the header lines name this unit
  STRUCTURE             every bs3 section and subsection, in order
  QUOTE-*               every "quotation" (Book C:V) is exact KJV text; no unreferenced
                        double-quoted text of 3+ words; KJV only
  SCRIPTURE-NEARMISS    no 'single-quoted phrase' that is almost, but not exactly, KJV wording
  REF-INVALID           every reference anywhere points to a verse that exists
  COVERAGE-*            the walkthrough covers every verse of the chapter (or, for the
                        overview, every chapter of John), in order, each block quoting its text
  KEY-VERSES, ROOT      bs3's quotation counts per tier; the root quotes a Gospel
  LIST-*, TABLE-*       bs3's item counts (diagnostic, questions, titles, topics, errors table)
  GREEK-*, HEBREW-*     every Strong's citation is real, in the verse cited, spelled and parsed right
  COUNT-*               every "N times" is backed by a recomputed concordance count
  LENGTH, PLACEHOLDER, SELF-GRADE, SELF-CLAIM
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kjvlib  # noqa: E402

# ---- limits (a person changes these, never the loop; see LOOP-SPEC.md) ----
MAX_BLOCK_VERSES = 6                       # verse-by-verse blocks stay small enough to be in-depth
WORDS = {"chapter": (4500, 12000), "overview": (3000, 10000)}
KEY_VERSES = {"tier 1": (3, 5), "tier 2": (5, 8), "tier 3": (8, 99)}   # whole-verse quotations; fragments are unlimited
LISTS = [  # (tier, subsection, min, max, must end with "?")
    ("tier 1", "personal diagnostic", 4, 5, True),
    ("tier 2", "discussion questions", 3, 5, True),
    ("tier 3", "preaching titles", 3, 3, False),
    ("spiral", "follow up topics", 3, 3, False),
]
MAX_REPORTED = 60
OTHER_VERSIONS = r"\b(ESV|NIV|NIrV|NASB(?:95)?|NKJV|NLT|RSV|NRSV|CSB|HCSB|AMP|MSG|NET|ASV|YLT|WEB|BSB|LSB|TB2?|GNT|CEV|TLB|Darby|Geneva)\b"

WALK = {"chapter": "verse by verse walkthrough", "overview": "chapter by chapter breakdown"}


def structure(kind):
    return [
        ("passage map", []),
        ("christological root", ["what jesus said did", "the bridge", "the progression line",
                                 "what gets lost without this root"]),
        ("tier 1", ["core concept", "key verses", "analogy", "tip", "hack", "personal diagnostic",
                    "prayer response", "action step"]),
        ("tier 2", ["deeper dive", WALK[kind], "key verses", "original language insight",
                    "common misconception", "common errors quick reference", "tip", "hack",
                    "teaching angle", "discussion questions", "action step"]),
        ("tier 3", ["theological framework", "key verses", "scholarly insight", "debate corner",
                    "original language deep dive", "tip", "hack", "teaching angle",
                    "preaching titles", "action step"]),
        ("cross tier connectors", ["golden thread", "progress map", "unlock moments"]),
        ("spiral", ["follow up topics", "next in john"]),
    ]


def key(heading):
    """'🟢 Tier 1 — Easy (The Foundation)' -> 'tier 1 easy the foundation'."""
    s = re.sub(r"[^0-9A-Za-z ]+", " ", heading.replace("/", " ").replace("-", " "))
    return re.sub(r"\s+", " ", s).strip().lower()


class Report:
    def __init__(self):
        self.items = []

    def add(self, code, line, message):
        self.items.append((line or 0, code, message))


def blank_comments(text):
    """HTML comments (the counts block) are invisible to the other checks; newlines are kept
    so line numbers still match."""
    return re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def parse_headings(lines):
    heads = []
    fence = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m and not fence:
            heads.append((i, len(m.group(1)), m.group(2), key(m.group(2))))
    return heads


# ---------------------------------------------------------------- checks

def check_header(lines, unit, kind, chapter, rep):
    first = next((i for i, l in enumerate(lines, 1) if l.strip()), None)
    if first is None:
        rep.add("EMPTY", 1, "the file is empty. Write the whole unit following TEMPLATE.md.")
        return False
    title = lines[first - 1].strip()
    if kind == "chapter":
        ok = re.match(rf"^#\s+John\s+{chapter}\s*[·:—–-]\s*\S.*\(KJV\)\s*$", title)
        want = f"# John {chapter} · <title> (KJV)"
    else:
        ok = re.match(r"^#\s+The Gospel of John\s*[·:—–-]\s*Book Overview\s*\(KJV\)\s*$", title)
        want = "# The Gospel of John · Book Overview (KJV)"
    if not ok:
        rep.add("TITLE", first, f'the first line should be "{want}", found "{title[:80]}"')
    head = "\n".join(lines[first:first + 5])
    if not re.search(rf"^>\s*Unit\s+john-{unit}\b", head, flags=re.M):
        rep.add("UNIT-LINE", first + 1,
                f'the unit line is missing: put "> Unit john-{unit} · ..." (see TEMPLATE.md) right under the title')
    return True


def check_structure(heads, kind, rep):
    required = structure(kind)
    h2 = [(ln, k) for ln, level, _r, k in heads if level == 2]
    pos = 0
    found = {}
    for prefix, subs in required:
        idx = next((i for i in range(pos, len(h2)) if h2[i][1].startswith(prefix)), None)
        if idx is None:
            rep.add("STRUCTURE", 0, f'missing the "## ... {prefix.title()}" section (or it is out of order); '
                                    "sections must follow TEMPLATE.md's order")
            continue
        pos = idx + 1
        start = h2[idx][0]
        end = h2[idx + 1][0] if idx + 1 < len(h2) else 10 ** 9
        found[prefix] = (start, end)
        h3 = [(ln, k) for ln, level, _r, k in heads if level == 3 and start < ln < end]
        p3 = 0
        prev = None
        for sub in subs:
            j = next((i for i in range(p3, len(h3)) if h3[i][1].endswith(sub) or h3[i][1] == sub), None)
            if j is None:
                where = f'after "{prev}"' if prev else "at the start of the section"
                rep.add("STRUCTURE", start, f'"{prefix.title()}" is missing the "### ... {sub}" subsection ({where})')
                continue
            p3 = j + 1
            prev = sub
    return found


def sub_span(heads, found, prefix, sub):
    if prefix not in found:
        return None
    start, end = found[prefix]
    h3 = [(ln, k) for ln, level, _r, k in heads if level == 3 and start < ln < end]
    for i, (ln, k) in enumerate(h3):
        if k.endswith(sub) or k == sub:
            nxt = h3[i + 1][0] if i + 1 < len(h3) else end
            return (ln, nxt - 1)
    return None


def find_quotes(body, rep):
    """Every double-quoted span: [(line, quote, ref-or-None, raw_paren, start, end)]."""
    quotes = []
    offset = 0
    for ln, line in enumerate(body.split("\n"), 1):
        marks = [m.start() for m in re.finditer(r'["“”]', line)]
        if len(marks) % 2:
            rep.add("QUOTE-UNBALANCED", ln, "this line has an odd number of double quotation marks; "
                                            "keep each quotation on one line, opened and closed")
            marks = marks[:-1]
        for a, b in zip(marks[0::2], marks[1::2]):
            inner = line[a + 1:b]
            rest = line[b + 1:]
            m = re.match(r"^\s*\(([^()]*)\)", rest)
            quotes.append((ln, inner, m.group(1).strip() if m else None, offset + a, offset + b + 1))
        offset += len(line) + 1
    return quotes


def check_quotes(body, rep):
    """Returns [(line, quote, Ref, is_full)] for every exact, referenced quotation."""
    good = []
    for ln, inner, paren, _a, _b in find_quotes(body, rep):
        words = len(inner.split())
        if paren is None:
            if words >= 3:
                rep.add("QUOTE-UNREFERENCED", ln,
                        f'"{inner[:70]}" has no reference. Double quotation marks are only for Scripture, '
                        "followed by (Book C:V). If it isn't Scripture, use single quotation marks or italics.")
            continue
        if re.search(OTHER_VERSIONS, paren):
            rep.add("QUOTE-VERSION", ln, f'"({paren})" names another translation. Quote only the KJV.')
            continue
        refstr = re.sub(r",?\s*KJV\s*$", "", paren).strip()
        try:
            refs = kjvlib.parse_ref_list(refstr)   # "John 1:39, 46": the words must be in each verse listed
        except kjvlib.RefError as e:
            if words >= 3 or re.search(r"\d+:\d+", paren):
                rep.add("QUOTE-BADREF", ln, f'the reference after "{inner[:50]}" is not usable: {e}. '
                                            "Use one reference, (Book C:V) or (Book C:V–W), or verses of one "
                                            "chapter that all contain the words, (Book C:V, V).")
            continue
        if refs[0].v1 is None:
            rep.add("QUOTE-BADREF", ln, f'"({paren})" names a whole chapter; a quotation needs verse numbers')
            continue
        bad = None
        for ref in refs:
            ok, why = kjvlib.match_quote(inner, ref)
            if not ok:
                bad = (ref, why)
                break
        if bad:
            ref, why = bad
            rep.add("QUOTE-MISMATCH", ln, f'"{inner[:90]}" ({ref}) {why} '
                                          f'Copy the text from: python3 tools/verse.py "{ref}"')
            continue
        good.append((ln, inner, refs[0], all(kjvlib.is_full_quote(inner, r) for r in refs)))
    return good


# A phrase in single quotation marks: opened at the start of a word, closed before a space or punctuation.
# Apostrophes inside words (Father's) are neither, so they don't break a phrase.
SINGLE_QUOTE = re.compile(r"(?:^|(?<=[\s(\[—–-]))['‘]([^'‘’\n]{8,200}?)['’](?=[\s.,;:!?)\]—–-]|$)", re.M)


def check_single_quotes(body, rep):
    """Single quotation marks are for the maker's own words and terms. When a phrase in them is
    close to KJV wording but not exact, it's a misquotation in disguise (SF-4 from the shakedown)."""
    for m in SINGLE_QUOTE.finditer(body):
        phrase = m.group(1)
        miss = kjvlib.near_miss(phrase)
        if miss:
            key, _words, ratio = miss
            ref = f"{key[0]} {key[1]}:{key[2]}"
            rep.add("SCRIPTURE-NEARMISS", line_of(body, m.start()),
                    f"'{phrase[:80]}' looks like {ref} ({ratio:.0%} alike) but isn't its exact wording. The KJV reads: "
                    f"\"{kjvlib.kjv()[key]}\" Quote Scripture exactly (in double quotation marks with the reference), "
                    "or put the thought in your own words without quotation marks.")


def check_refs(body, rep):
    seen = set()
    for start, _end, raw, ref in kjvlib.find_refs(body):
        if isinstance(ref, kjvlib.RefError) and (start, raw) not in seen:
            seen.add((start, raw))
            rep.add("REF-INVALID", line_of(body, start), f'"{raw}" is not a real reference: {ref}')


def in_span(ln, span):
    return span is not None and span[0] <= ln <= span[1]


def check_coverage(lines, heads, found, kind, chapter, quotes, rep):
    span = sub_span(heads, found, "tier 2", WALK[kind])
    if span is None:
        return None
    blocks = []
    for ln, level, raw, _k in heads:
        if level != 4 or not in_span(ln, span):
            continue
        text = re.sub(r"^[^\w]+", "", raw).strip()
        if kind == "chapter":
            m = re.match(rf"^John\s+(\d+):(\d+)(?:\s*{kjvlib.DASH}\s*(\d+))?\s*[·•|:—–-]\s*(\S.*)$", text)
            if not m:
                rep.add("COVERAGE-HEADING", ln, f'walkthrough headings must read "#### John {chapter}:V–W · short title", '
                                                f'found "#### {raw[:60]}"')
                continue
            c, v1 = int(m.group(1)), int(m.group(2))
            v2 = int(m.group(3)) if m.group(3) else v1
            if c != chapter:
                rep.add("COVERAGE-HEADING", ln, f'"{text[:40]}" is not in John {chapter}')
                continue
            blocks.append((ln, v1, v2))
        else:
            m = re.match(r"^John\s+(\d+)\s*[·•|:—–-]\s*(\S.*)$", text)
            if not m:
                rep.add("COVERAGE-HEADING", ln, f'breakdown headings must read "#### John N · short title", found "#### {raw[:60]}"')
                continue
            blocks.append((ln, int(m.group(1)), int(m.group(1))))
    ends = [b[0] for b in blocks[1:]] + [span[1] + 1]
    if kind == "chapter":
        size = kjvlib.chapter_sizes()[("John", chapter)]
        expect = 1
        for (ln, v1, v2), stop in zip(blocks, ends):
            if v1 != expect:
                what = f"John {chapter}:{expect}–{v1 - 1} is not covered" if v1 > expect else \
                    f"John {chapter}:{v1} is covered twice (or out of order)"
                rep.add("COVERAGE-GAP", ln, f"{what}; blocks must run 1 to {size} in order with no gaps or overlaps")
            if v2 < v1 or v2 > size:
                rep.add("COVERAGE-GAP", ln, f"John {chapter}:{v1}–{v2} is not a valid range (the chapter has {size} verses)")
            elif v2 - v1 + 1 > MAX_BLOCK_VERSES:
                rep.add("COVERAGE-BLOCK", ln, f"John {chapter}:{v1}–{v2} covers {v2 - v1 + 1} verses; "
                                              f"split it so no block covers more than {MAX_BLOCK_VERSES}")
            own = [q for q in quotes if ln < q[0] < stop and q[2].book == "John" and q[2].c1 == chapter
                   and v1 <= q[2].v1 and q[2].v2 <= v2]
            if not own:
                rep.add("COVERAGE-QUOTE", ln, f"the block for John {chapter}:{v1}–{v2} quotes none of its own verses; "
                                              "quote at least one phrase from them, with its reference")
            expect = max(expect, v2 + 1)
        if expect <= size:
            rep.add("COVERAGE-GAP", span[1], f"John {chapter}:{expect}–{size} is not covered by the walkthrough")
        return (len(blocks), size)
    expect = 1
    for (ln, c, _c), stop in zip(blocks, ends):
        if c != expect:
            rep.add("COVERAGE-GAP", ln, f"expected John {expect} next, found John {c}; the breakdown runs John 1 to John 21 in order")
        own = [q for q in quotes if ln < q[0] < stop and q[2].book == "John" and q[2].c1 == c]
        if not own:
            rep.add("COVERAGE-QUOTE", ln, f"the John {c} entry quotes nothing from John {c}")
        expect = c + 1
    if expect <= 21:
        rep.add("COVERAGE-GAP", span[1], f"the breakdown stops before John {expect}; it must cover John 1 to John 21")
    return (len(blocks), 21)


def check_key_verses(heads, found, quotes, rep):
    for tier, (lo, hi) in KEY_VERSES.items():
        span = sub_span(heads, found, tier, "key verses")
        if span is None:
            continue
        n = len([q for q in quotes if in_span(q[0], span) and q[3]])
        if not lo <= n <= hi:
            rng = f"{lo}–{hi}" if hi < 99 else f"at least {lo}"
            rep.add("KEY-VERSES", span[0], f"{tier.title()} Key Verses quotes {n} whole verses; bs3 asks for {rng} "
                                           "(a whole-verse quotation is the complete verse text, with its reference)")
    span = sub_span(heads, found, "christological root", "what jesus said did")
    if span is not None:
        full = [q for q in quotes if in_span(q[0], span) and q[3] and q[2].book in kjvlib.GOSPELS]
        if not full:
            rep.add("ROOT", span[0], "What Jesus Said/Did must quote at least one Gospel passage in full "
                                     "(whole verses, with the reference)")


def list_items(lines, span):
    return [l for l in lines[span[0]:span[1]] if re.match(r"^(?:[-*+]|\d+[.)])\s+\S", l)]   # top level only


def check_lists(lines, heads, found, rep):
    for tier, sub, lo, hi, question in LISTS:
        span = sub_span(heads, found, tier, sub)
        if span is None:
            continue
        items = list_items(lines, span)
        if question:
            items = [i for i in items if "?" in i]
        if not lo <= len(items) <= hi:
            what = "questions (list items ending in ?)" if question else "list items"
            rng = f"{lo}" if lo == hi else f"{lo}–{hi}"
            rep.add("LIST-COUNT", span[0], f'"{sub.title()}" has {len(items)} {what}; bs3 asks for {rng}')
    span = sub_span(heads, found, "tier 2", "common errors quick reference")
    if span is not None:
        rows = [l for l in lines[span[0]:span[1]] if l.strip().startswith("|")]
        data = [r for r in rows[1:] if not re.match(r"^\s*\|[\s:|-]+\|\s*$", r)]
        if not 2 <= len(data) <= 3:
            rep.add("TABLE-ERRORS", span[0], f"Common Errors Quick-Reference needs a table (Error | Definition | "
                                             f"Corrective Verse) with 2–3 rows; found {len(data)}")
        for r in data:
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            if len(cells) < 3 or not [x for x in kjvlib.find_refs(cells[-1]) if not isinstance(x[3], kjvlib.RefError)]:
                rep.add("TABLE-ERRORS", span[0], "each Common Errors row needs 3 cells, the last holding a corrective verse reference")
                break


def check_map(lines, heads, found, kind, chapter, rep):
    if "passage map" not in found:
        return
    start, end = found["passage map"]
    rows = [(i, l) for i, l in enumerate(lines[start:end - 1], start + 1) if l.strip().startswith("|")]
    data = [(i, r) for i, r in rows[1:] if not re.match(r"^\s*\|[\s:|-]+\|\s*$", r)]
    if len(data) < 2:
        rep.add("TABLE-MAP", start, "the Passage Map needs a table (Section/Verses | Theme | One-Line Summary) with at least 2 rows")
        return
    if kind != "chapter":
        return
    size = kjvlib.chapter_sizes()[("John", chapter)]
    covered = set()
    for i, r in data:
        cell = r.strip().strip("|").split("|")[0]
        m = re.search(rf"(?:(\d+):)?(\d+)(?:\s*{kjvlib.DASH}\s*(?:(\d+):)?(\d+))?", cell)
        if not m or (m.group(1) and int(m.group(1)) != chapter) or (m.group(3) and int(m.group(3)) != chapter):
            rep.add("TABLE-MAP", i, f'the first cell should give verses of John {chapter}, like "{chapter}:1–15"; found "{cell.strip()[:40]}"')
            continue
        v1 = int(m.group(2))
        v2 = int(m.group(4)) if m.group(4) else v1
        if not 1 <= v1 <= v2 <= size:
            rep.add("TABLE-MAP", i, f'"{cell.strip()[:30]}" is outside John {chapter}:1–{size}')
            continue
        covered |= set(range(v1, v2 + 1))
    missing = sorted(set(range(1, size + 1)) - covered)
    if missing and len(missing) < size:
        rep.add("TABLE-MAP", start, f"the Passage Map leaves out John {chapter}:{_ranges(missing)}; its rows should cover the whole chapter")


def _ranges(nums):
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"{nums[i]}" if i == j else f"{nums[i]}–{nums[j]}")
        i = j + 1
    return ", ".join(out)


# *agapaō* (G25, John 21:15) · *agapas* (G25, John 21:15, V-PAI-2S) · *mishkan* (H4908) — bold is accepted too
CITE = re.compile(r"\*{1,2}([^*\n]{1,40})\*{1,2}\s*\(\s*([GH]\d{1,4}[A-Za-z]?)\s*(?:[,·;]\s*([^,·;()]+?)\s*)?"
                  r"(?:[,·;]\s*([A-Z0-9]+(?:-[A-Z0-9]+)*)\s*)?\)")
GREEK_SCRIPT = re.compile(r"[Ͱ-Ͽἀ-῿]")    # Greek and Coptic U+0370–03FF, Greek Extended U+1F00–1FFF
HEBREW_SCRIPT = re.compile(r"[֐-׿]")        # Hebrew U+0590–05FF


def check_greek(body, heads, found, rep):
    spans = []
    cites = []
    cite_lines = set()   # lines holding any citation attempt; a failed one is reported on its own
    for m in CITE.finditer(body):
        ln = line_of(body, m.start())
        cite_lines.add((ln, m.group(2)[0].upper()))
        translit, strong, refstr, morph = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
        spans.append((m.start(), m.end()))
        skey = kjvlib.strong_key(strong)
        entries = kjvlib.lexicon().get(skey)
        if not entries:
            rep.add("GREEK-UNKNOWN" if skey.startswith("G") else "HEBREW-UNKNOWN", ln,
                    f"{strong} is not in the lexicon. Look it up: python3 tools/lexicon.py {strong}")
            continue
        lemma_keys = {kjvlib.translit_key(e["translit"]) for e in entries}
        ref = None
        if refstr:
            try:
                ref = kjvlib.parse_ref(refstr)
            except kjvlib.RefError as e:
                rep.add("GREEK-BADREF", ln, f"the citation *{translit}* ({strong}, {refstr}) has a bad reference: {e}")
                continue
        if skey.startswith("H"):
            if kjvlib.translit_key(translit) not in lemma_keys:
                want = entries[0]["translit"].replace(".", "")
                rep.add("HEBREW-TRANSLIT", ln, f"*{translit}* doesn't match {strong}, which is {entries[0]['lemma']} "
                                               f"({want}); write *{want}*")
            continue
        if ref is None:
            rep.add("GREEK-NOREF", ln, f"*{translit}* ({strong}) needs a verse where the word occurs: "
                                       f"*{translit}* ({strong}, Book C:V). Find one with tools/greek.py")
            continue
        if ref.book not in kjvlib.NT_BOOKS or ref.v1 is None:
            rep.add("GREEK-BADREF", ln, f"{ref} is not a New Testament verse; Greek citations need an NT verse")
            continue
        words = [w for b, c, v in ref.verses() for w in kjvlib.words_in(f"{b} {c}:{v}", strong)]
        if not words:
            present = kjvlib.words_in(f"{ref.book} {ref.c1}:{ref.v1}")
            sample = ", ".join(f"{w['translit']} {kjvlib.strong_key(w['strongs'].split()[0])}" for w in present[:14] if w['strongs'])
            rep.add("GREEK-NOTINVERSE", ln, f"{strong} ({entries[0]['lemma']}) is not in the Textus Receptus of {ref}. "
                                            f"Words there include: {sample} ... Check with: python3 tools/greek.py \"{ref}\"")
            continue
        forms = {kjvlib.translit_key(w["translit"]) for w in words}
        # the word's own STEP number may have its own lemma (οἶδα, G6063, is a form filed under G1492)
        forms |= {kjvlib.translit_key(e["translit"]) for w in words for s in w["strongs"].split()
                  for e in kjvlib.lexicon().get(kjvlib.strong_key(s), [])}
        if kjvlib.translit_key(translit) not in lemma_keys | forms:
            rep.add("GREEK-TRANSLIT", ln, f"*{translit}* doesn't spell {strong}: the lemma is "
                                          f"{entries[0]['translit']} and the form in {ref} is "
                                          f"{', '.join(sorted({w['translit'] for w in words}))}")
            continue
        if morph and morph not in {mm for w in words for mm in w["morphs"].split()}:
            rep.add("GREEK-MORPH", ln, f"{morph} is not the parsing of {strong} in {ref}; the text has "
                                       f"{', '.join(sorted({mm for w in words for mm in w['morphs'].split()}))}")
            continue
        cites.append((ln, skey, morph))
    # Strong's numbers outside a citation can't be checked, so they aren't allowed.
    for m in re.finditer(r"(?<![\w/])([GH]\d{1,4}[A-Za-z]?)(?![\w])", body):
        if not any(a <= m.start() < b for a, b in spans):
            rep.add("STRONGS-LOOSE", line_of(body, m.start()),
                    f"{m.group(1)} appears outside a citation. Cite it as *translit* ({m.group(1)}, Book C:V)")
    for ln, line in enumerate(body.split("\n"), 1):
        if GREEK_SCRIPT.search(line) and (ln, "G") not in cite_lines:
            rep.add("GREEK-UNCITED", ln, "Greek script needs a checked citation on the same line: *translit* (G####, Book C:V)")
        if HEBREW_SCRIPT.search(line) and (ln, "H") not in cite_lines:
            rep.add("HEBREW-UNCITED", ln, "Hebrew script needs a citation on the same line: *translit* (H####)")
    for tier, sub, need_morph in (("tier 2", "original language insight", False),
                                  ("tier 3", "original language deep dive", True)):
        span = sub_span(heads, found, tier, sub)
        if span is None:
            continue
        here = [c for c in cites if in_span(c[0], span) and c[1].startswith("G") and (c[2] or not need_morph)]
        if not here:
            what = "with a parsing code, like *agapas* (G25, John 21:15, V-PAI-2S)" if need_morph else \
                "like *logos* (G3056, John 1:1)"
            rep.add("GREEK-MISSING", span[0], f'"{sub.title()}" needs at least one checked Greek citation {what}')
    return len(cites)


def check_counts(raw, body, rep):
    backed = set()
    for block in re.finditer(r"<!--\s*counts\b(.*?)-->", raw, flags=re.S):
        for off, line in enumerate(block.group(1).split("\n")):
            if not line.strip():
                continue
            ln = line_of(raw, block.start()) + off
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 3 or not parts[2].isdigit():
                rep.add("COUNT-FORMAT", ln, f'counts lines read "query | scope | number", found "{line.strip()[:60]}"')
                continue
            try:
                total, _hits = kjvlib.count(parts[0], parts[1])
            except (kjvlib.RefError, ValueError) as e:
                rep.add("COUNT-FORMAT", ln, f"can't recount \"{line.strip()}\": {e}")
                continue
            if total != int(parts[2]):
                rep.add("COUNT-WRONG", ln, f'"{parts[0]}" occurs {total} times in {parts[1]}, not {parts[2]} '
                                           f'(python3 tools/concordance.py "{parts[0]}" "{parts[1]}")')
                continue
            backed.add(total)
    for m in re.finditer(r"\b(\d{1,4})\s+times\b", body):
        if int(m.group(1)) not in backed:
            rep.add("COUNT-UNBACKED", line_of(body, m.start()),
                    f'"{m.group(0)}" is a count. Compute it with tools/concordance.py and add its line to the '
                    "<!-- counts --> block, or write the number in words if it's a detail of the story")


def check_misc(body, kind, heads, rep):
    words = len(re.findall(r"\S+", body))
    lo, hi = WORDS[kind]
    if not lo <= words <= hi:
        rep.add("LENGTH", 0, f"the unit has {words:,} words; it must have {lo:,}–{hi:,}. "
                             + ("Deepen thin sections rather than padding." if words < lo else
                                "Cut repetition; length earns nothing."))
    for m in re.finditer(r"\{\{|\bTODO\b|\bTBD\b|\[insert|lorem ipsum|\bXXX\b", body, flags=re.I):
        rep.add("PLACEHOLDER", line_of(body, m.start()), f'placeholder text "{m.group(0)}" is still in the unit')
    for ln, _level, raw, k in heads:
        if "self audit" in k or "flywheel" in k:
            rep.add("SELF-GRADE", ln, f'"{raw[:40]}": the maker never grades its own work here; the checker '
                                      "and the judge do. Remove this section.")
    for m in re.finditer(r"\|\s*\d{1,2}\s*/\s*10\s*\|", body):
        rep.add("SELF-GRADE", line_of(body, m.start()), "a /10 self-score table; remove it (the judge scores the unit)")
    claim = (r"\b(all|every)\s+(of\s+the\s+)?(verses?|quotes?|quotations?|scriptures?|references?|citations?)\s+"
             r"(have\s+been\s+|has\s+been\s+|were\s+|are\s+|is\s+)?(verified|checked|confirmed|accurate)\b")
    for m in re.finditer(claim, body, flags=re.I):
        rep.add("SELF-CLAIM", line_of(body, m.start()),
                f'"{m.group(0)}": only the checker can say that; remove the claim')


def run(unit, path):
    rep = Report()
    kind = "overview" if unit == "00" else "chapter"
    chapter = int(unit)
    if not os.path.exists(path):
        rep.add("MISSING", 0, f"{path} does not exist yet. Write the unit following TEMPLATE.md.")
        return rep, {}
    raw = open(path, encoding="utf-8").read()
    if not raw.strip():
        rep.add("EMPTY", 0, "the file is empty. Write the unit following TEMPLATE.md.")
        return rep, {}
    body = blank_comments(raw)
    lines = body.split("\n")
    if not check_header(lines, unit, kind, chapter, rep):
        return rep, {}
    heads = parse_headings(lines)
    found = check_structure(heads, kind, rep)
    quotes = check_quotes(body, rep)
    check_single_quotes(body, rep)
    check_refs(body, rep)
    covered = check_coverage(lines, heads, found, kind, chapter, quotes, rep)
    check_key_verses(heads, found, quotes, rep)
    check_lists(lines, heads, found, rep)
    check_map(lines, heads, found, kind, chapter, rep)
    ncites = check_greek(body, heads, found, rep)
    check_counts(raw, body, rep)
    check_misc(body, kind, heads, rep)
    stats = {"quotes": len(quotes), "covered": covered, "greek": ncites,
             "words": len(re.findall(r"\S+", body))}
    return rep, stats


def main(argv):
    ap = argparse.ArgumentParser(description="Deterministic checks for one unit of the John KJV study")
    ap.add_argument("unit", help="00 (book overview) or 01-21 (John's chapters)")
    ap.add_argument("--file", help="check this file instead of study/john-UNIT.md")
    ap.add_argument("--report", help="write the full report (with line numbers) to this file, and print only a "
                                     "stable summary: the same problems always print the same way, so the "
                                     "loop's STUCK rule can recognise a repeat")
    a = ap.parse_args(argv)
    if not re.fullmatch(r"\d{2}", a.unit) or not 0 <= int(a.unit) <= 21:
        print("NOT YET · usage: the unit is 00-21", file=sys.stderr)
        return 2
    path = a.file or os.path.join(kjvlib.ROOT, "study", f"john-{a.unit}.md")
    rep, stats = run(a.unit, path)
    out = []
    if rep.items:
        items = sorted(rep.items, key=lambda x: (x[0], x[1], x[2]))
        out.append(f"NOT YET · john-{a.unit} · deterministic checks found {len(items)} problem(s). Fix every one, then stop.")
        for n, (ln, code, msg) in enumerate(items[:MAX_REPORTED], 1):
            where = f"line {ln}" if ln else "whole file"
            out.append(f"{n}. {code} ({where}): {msg}")
        if len(items) > MAX_REPORTED:
            out.append(f"... and {len(items) - MAX_REPORTED} more; fix these first.")
        codes = {}
        for _ln, code, _m in items:
            codes[code] = codes.get(code, 0) + 1
        summary = "NOT YET · " + " ".join(f"{c}×{n}" for c, n in sorted(codes.items()))
        out.append(summary)
        stable = sorted({f"{code}: {msg}" for _ln, code, msg in items}) + [summary]
        status = 1
    else:
        blocks, total = stats["covered"] or (0, 0)
        unit_word = "verses" if a.unit != "00" else "chapters"
        out.append(f"PASS · john-{a.unit} · deterministic checks · {stats['quotes']} quotations exact · "
                   f"{total}/{total} {unit_word} covered in {blocks} blocks · {stats['greek']} Greek/Hebrew "
                   f"citations verified · {stats['words']:,} words")
        stable = out
        status = 0
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
        print("\n".join(stable))
    else:
        print("\n".join(out))
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
