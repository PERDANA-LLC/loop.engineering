#!/usr/bin/env python3
"""The deterministic checker for one unit of the John KJV study.

It answers PASS or NOT YET, never "probably fine". Its report is the maker's next
prompt, so every problem says what failed, where (line number), and what was
expected. Nothing here is the maker's opinion: quotations and the printed chapter are
compared with kjv/kjv.tsv, Greek citations with kjv/greek-nt.tsv.gz and
kjv/lexicon.tsv.gz, and counts are recomputed.

  python3 tools/check_study.py 03                  # checks study/john-03.md
  python3 tools/check_study.py 03 --file draft.md  # checks another file as unit 03
Exit codes: 0 PASS · 1 NOT YET · 2 usage error (treated as NOT YET by check.sh)

The format is KJV72 x KJV82 (TEMPLATE.md). What it checks:
  TITLE, UNIT-LINE      the header lines name this unit
  STRUCTURE             every section and subsection, in order
  QUOTE-*               every "quotation" (Book C:V) is exact KJV text; no unreferenced
                        double-quoted text of 3+ words; KJV only
  SCRIPTURE-NEARMISS    no 'single-quoted phrase' that is almost, but not exactly, KJV wording
  REF-INVALID           every reference anywhere points to a verse that exists
  TEXT-*                Read & Mark prints the whole chapter, in order, every verse exact
  COVERAGE-*, LAYERS    the walkthrough covers every verse (the overview's breakdown, every
                        chapter), in order, each block quoting its text; each walkthrough block
                        keeps Says, Means, and Asks apart
  QUESTIONS, WRITE-IN, ANSWER-KEY   participant questions are numbered, counted per level,
                        followed by write-in lines, and every one is answered with a verse
  LABELS                the labeled parts: foundations, pathways, panels, council, guide
  PRACTICES             3+ per set, each traced to a verse; Life and Light sets tagged Inward/Outward
  FIXED-LINE            the commitment lines and the two guards
  AT-A-GLANCE, PLANNER, SESSION-PLAN, GLOSSARY, WORD-STUDY, TABLE-*   the tables
  DOCTRINE-*            doctrine blocks: categories in order, five parts, quoted cross-references,
                        no category skipped
  COUNCIL               three hard questions with resolutions; all seven scholars speak
  BLUEPRINT, LEDGER     the overview's Lesson Map and Life & Light Ledger
  KEY-VERSES, ROOT, MEMORY-VERSE, LIST-COUNT   whole-verse quotations and list sizes
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
MAX_BLOCK_VERSES = 6                       # walkthrough blocks stay small enough to be in-depth
WORDS = {"chapter": (8000, 20000), "overview": (8000, 18000)}
SESSION_MINUTES = 75                       # the prompts' default session (plan.md D7)
SCENE_WORDS = (150, 300)                   # KJV82 P3 asks for 150-250 words; KJV72 C2 for 2-3 paragraphs
MAX_REPORTED = 60
OTHER_VERSIONS = r"\b(ESV|NIV|NIrV|NASB(?:95)?|NKJV|NLT|RSV|NRSV|CSB|HCSB|AMP|MSG|NET|ASV|YLT|WEB|BSB|LSB|TB2?|GNT|CEV|TLB|Darby|Geneva)\b"

CATEGORIES = ["Theology Proper", "Christology", "Pneumatology", "Anthropology & Sin",
              "Soteriology & Grace", "Ecclesiology", "Eschatology", "Christian Walk"]
SCHOLARS = ["Philologist", "Historian", "Literary Scholar", "Theologian", "Church Historian", "Pastor", "Teacher"]
DOCTRINE_PARTS = ["Proposition", "Textual Anchor", "Cross-References", "Errors Refuted", "Pastoral Fruit"]

# ---- the format (TEMPLATE.md, parts 3 and 5): sections and their subsections, in order ----
AT_A_GLANCE = {"chapter": ["Golden Thread", "Life & Light Line", "Objectives", "Life & Light At-a-Glance",
                           "Passage Map"],
               "overview": ["Golden Thread", "Life & Light Frame", "Course Outcomes", "Life & Light At-a-Glance",
                            "Passage Map"]}
FOUNDATIONS = {"Christological Root": ["Gospel Foundation", "The Bridge", "Canonical Echoes", "What Gets Lost"],
               "Spiritual Warfare": ["The Lie", "The Truth", "The Battleground", "The Weapon"],
               "Life Pathway": ["The Theft", "The Source", "The Channel", "The Abundance Guard"],
               "Light Pathway": ["The Darkness", "The Source", "The Lamp", "The Love Guard"]}
LESSON = ["Open", "Setting the Scene", "Read & Mark", "Observe", "Mind the Language", "Word Study",
          "Search the Scriptures", "Interpret", "Case Study", "Modern Example", "Voices from Church History",
          "Doctrine in My Own Words", "Apply", "Christocentric & Humility", "Bring Life", "Bring Light",
          "Memory Verse", "Gather", "Closing & Going Deeper"]
BLUEPRINT = ["Lesson Map", "How to Use This Workbook", "Life & Light Ledger"]
TIER1 = ["Core Concept", "Key Verses", "Analogy", "Diagnostic Check", "Action Step", "Life and Light, Simply"]
TIER2 = {"chapter": ["Walkthrough", "Common Errors Quick-Reference", "Cultural Landmines and Misconceptions"],
         "overview": ["Setting the Scene", "Chapter-by-Chapter Breakdown", "Common Errors Quick-Reference",
                      "Cultural Landmines and Misconceptions"]}
TIER3 = ["Theological Framework", "Scholarly Insights", "Debate Corner", "Original Language Deep Dive",
         "Preaching Mistakes to Avoid"]
TIER4 = ["Every Answer in Jesus", "Humility Practices", "Life Practices", "Light Practices"]
COUNCIL = ["Question 1", "Question 2", "Question 3", "The Life & Light Audit"]
GUIDE = {"chapter": ["Session Plan", "Answer Key", "Glossary", "Life & Light Leader's Map", "Shepherding Notes",
                     "Teaching Angles"],
         "overview": ["Teacher FAQ", "Advanced Teacher Hacks", "Shepherding Notes", "Teaching Angles",
                      "Going Deeper"]}
WALK = {"chapter": "Walkthrough", "overview": "Chapter-by-Chapter Breakdown"}

# participant questions per lesson subsection: (subsection, min, max)
QUESTION_COUNTS = [("Observe", 5, 8), ("Search the Scriptures", 1, 99), ("Interpret", 3, 5), ("Case Study", 1, 99),
                   ("Modern Example", 1, 99), ("Voices from Church History", 1, 99), ("Apply", 3, 99),
                   ("Christocentric & Humility", 1, 99), ("Bring Life", 3, 4), ("Bring Light", 3, 4)]


def structure(kind):
    out = [("At a Glance", AT_A_GLANCE[kind]), ("Core Foundations", list(FOUNDATIONS))]
    out.append(("The Lesson", LESSON) if kind == "chapter" else ("Workbook Blueprint", BLUEPRINT))
    out += [("Tier 1", TIER1), ("Tier 2", TIER2[kind]), ("Tier 3", TIER3), ("Tier 4", TIER4), ("Doctrine", []),
            ("The Council", COUNCIL), ("Leader's Guide", GUIDE[kind])]
    return out


def key(heading):
    """'🟢 Tier 1 — Easy' -> 'tier 1 easy'. '&' and 'and' are the same, and apostrophes vanish:
    'Anthropology & Sin' and 'Anthropology and Sin' -> 'anthropology sin'; "Leader's" -> 'leaders'."""
    s = heading.replace("'", "").replace("’", "")
    s = re.sub(r"[^0-9A-Za-z ]+", " ", s).lower()
    s = re.sub(r"\band\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


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


# ---------------------------------------------------------------- helpers

LABEL = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?\*\*([^*\n]{1,90}?)\*\*")
QLINE = re.compile(r"^\*\*Q(\d+)[.:]?\*\*")
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+\S")
WRITE_IN = re.compile(r"^\s*_{10,}\s*$")
BLANK = re.compile(r"_{5,}")
TAG = re.compile(r"^(?:[-*+]|\d+[.)])\s+\*\*(Inward|Outward)\s*[:.]?\s*\*\*", re.I)


def lines_in(lines, span):
    return range(span[0], min(span[1], len(lines)) + 1)


def text_of(lines, span):
    return "\n".join(lines[i - 1] for i in lines_in(lines, span))


def strip_md(s):
    return re.sub(r"[*_`]", "", s).strip()


def valid_refs(text):
    return [r for _s, _e, _raw, r in kjvlib.find_refs(text) if not isinstance(r, kjvlib.RefError)]


def labels(lines, span):
    """[(line, key)] for every bold label that starts a line of the span."""
    out = []
    for i in lines_in(lines, span):
        m = LABEL.match(lines[i - 1])
        if m:
            out.append((i, key(m.group(1).strip().rstrip(":.").strip())))
    return out


def parts(lines, span):
    """{label key: (first line, last line)}: each labeled part runs from its label to the next label."""
    labs = labels(lines, span)
    out = {}
    for n, (i, k) in enumerate(labs):
        end = labs[n + 1][0] - 1 if n + 1 < len(labs) else span[1]
        out.setdefault(k, (i, end))
    return out


def part(pmap, name, *alternatives):
    for want in (key(name),) + tuple(key(a) for a in alternatives):
        for k, sp in pmap.items():
            if k == want or k.startswith(want + " ") or k == "the " + want:
                return sp
    return None


def need_labels(lines, span, names, where, rep):
    """Report the labels a span lacks; return {name: part span} for those it has."""
    pmap = parts(lines, span)
    got, missing = {}, []
    for name in names:
        sp = part(pmap, name)
        if sp is None:
            missing.append(name)
        else:
            got[name] = sp
    if missing:
        rep.add("LABELS", span[0], f"{where} is missing the bold label{'s' if len(missing) > 1 else ''} "
                + ", ".join(f"**{n}**" for n in missing) + " at the start of a line (see TEMPLATE.md)")
    return got


def label_line(lines, span, name):
    sp = part(parts(lines, span), name)
    return sp[0] if sp else None


def list_blocks(lines, a, b, contiguous=False):
    """Top-level list items from line a to line b: [(line, text including its indented continuation)].
    contiguous: the list must start at once and ends at the first line that is neither an item,
    an indented continuation, nor blank (used for a list that follows a label)."""
    out = []
    for i in range(a, min(b, len(lines)) + 1):
        s = lines[i - 1]
        if LIST_ITEM.match(s):
            out.append([i, s])
        elif s.strip() and s[:1] in (" ", "\t") and out:
            out[-1][1] += "\n" + s
        elif s.strip() and contiguous:
            break
    return [(i, t) for i, t in out]


def q_lines(lines, span):
    out = []
    for i in lines_in(lines, span):
        m = QLINE.match(lines[i - 1])
        if m:
            out.append((i, int(m.group(1))))
    return out


def writeins(lines, span):
    return sum(1 for i in lines_in(lines, span) if WRITE_IN.match(lines[i - 1]))


def writeins_after(lines, ln, end):
    """Write-in lines under a question (the question may run onto a second line)."""
    i = ln + 1
    end = min(end, len(lines))
    while i <= end and not WRITE_IN.match(lines[i - 1]):
        s = lines[i - 1].strip()
        if s and (s.startswith(("#", "|")) or LIST_ITEM.match(s) or LABEL.match(lines[i - 1])):
            return 0
        i += 1
    n = 0
    while i <= end:
        if WRITE_IN.match(lines[i - 1]):
            n += 1
        elif lines[i - 1].strip():
            break
        i += 1
    return n


def tables(lines, span):
    """[(header cells, [(line, cells), ...])] for every table in the span."""
    out, cur = [], None
    for i in lines_in(lines, span):
        s = lines[i - 1].strip()
        if not s.startswith("|"):
            cur = None
            continue
        if re.match(r"^\|[\s:|-]+\|$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cur is None:
            cur = (cells, [])
            out.append(cur)
        else:
            cur[1].append((i, cells))
    return out


def verse_cell(cell, chapter=None):
    """'John 2:6' (or '2:6' in a chapter unit) -> Ref, else None."""
    c = strip_md(cell)
    if chapter is not None and re.fullmatch(r"\d+:\d+", c):
        c = f"John {c}"
    try:
        ref = kjvlib.parse_ref(c)
    except kjvlib.RefError:
        return None
    return ref if ref.v1 is not None else None


def word_key(s):
    return " ".join(kjvlib.words_of(strip_md(s)))


def word_in_verse(word, ref):
    w = word_key(word)
    return bool(w) and f" {w} " in " " + " ".join(kjvlib.words_of(ref.text())) + " "


# ---------------------------------------------------------------- the header and the skeleton

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


def check_structure(heads, kind, nlines, rep):
    """{section key: (heading line, end line exclusive)} for the sections found, in TEMPLATE.md's order."""
    h2 = [(ln, k) for ln, level, _r, k in heads if level == 2]
    pos = 0
    found = {}
    for section, subs in structure(kind):
        sk = key(section)
        idx = next((i for i in range(pos, len(h2)) if h2[i][1].startswith(sk)), None)
        if idx is None:
            rep.add("STRUCTURE", 0, f'missing the "## {section}" section (or it is out of order); '
                                    "sections must follow TEMPLATE.md's order")
            continue
        pos = idx + 1
        start = h2[idx][0]
        end = h2[idx + 1][0] if idx + 1 < len(h2) else nlines + 1
        found[sk] = (start, end)
        h3 = [(ln, k) for ln, level, _r, k in heads if level == 3 and start < ln < end]
        p3 = 0
        prev = None
        for sub in subs:
            want = key(sub)
            j = next((i for i in range(p3, len(h3)) if h3[i][1].startswith(want)), None)
            if j is None:
                where = f'after "{prev}"' if prev else "at the start of the section"
                rep.add("STRUCTURE", start, f'"{section}" is missing the "### {sub}" subsection ({where})')
                continue
            p3 = j + 1
            prev = sub
    return found


def section_span(found, section):
    sk = key(section)
    return (found[sk][0], found[sk][1] - 1) if sk in found else None


def sub_span(heads, found, section, sub):
    sk = key(section)
    if sk not in found:
        return None
    start, end = found[sk]
    h3 = [(ln, k) for ln, level, _r, k in heads if level == 3 and start < ln < end]
    want = key(sub)
    for i, (ln, k) in enumerate(h3):
        if k.startswith(want):
            nxt = h3[i + 1][0] if i + 1 < len(h3) else end
            return (ln, nxt - 1)
    return None


# ---------------------------------------------------------------- Scripture

def find_quotes(body, rep):
    """Every double-quoted span: [(line, quote, ref-or-None, start, end)]."""
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
            vkey, _words, ratio = miss
            ref = f"{vkey[0]} {vkey[1]}:{vkey[2]}"
            rep.add("SCRIPTURE-NEARMISS", line_of(body, m.start()),
                    f"'{phrase[:80]}' looks like {ref} ({ratio:.0%} alike) but isn't its exact wording. The KJV reads: "
                    f"\"{kjvlib.kjv()[vkey]}\" Quote Scripture exactly (in double quotation marks with the reference), "
                    "or put the thought in your own words without quotation marks.")


def check_refs(body, rep):
    seen = set()
    for start, _end, raw, ref in kjvlib.find_refs(body):
        if isinstance(ref, kjvlib.RefError) and (start, raw) not in seen:
            seen.add((start, raw))
            rep.add("REF-INVALID", line_of(body, start), f'"{raw}" is not a real reference: {ref}')


def in_span(ln, span):
    return span is not None and span[0] <= ln <= span[1]


def whole_verses(quotes, span, gospel=False):
    return [q for q in quotes if in_span(q[0], span) and q[3] and (not gospel or q[2].book in kjvlib.GOSPELS)]


VERSE_LINE = re.compile(r"^\s*\*\*(\d{1,3})\*\*\s+(.*?)\s*\\?\s*$")


def check_text(lines, span, chapter, rep):
    """Read & Mark: every verse of the chapter, in order, each exactly as the KJV prints it."""
    size = kjvlib.chapter_sizes()[("John", chapter)]
    printed = [(i, int(m.group(1)), m.group(2)) for i in lines_in(lines, span)
               if (m := VERSE_LINE.match(lines[i - 1]))]
    if not printed:
        rep.add("TEXT-MISSING", span[0], f"Read & Mark must print the whole of John {chapter}, one verse per paragraph "
                                         f'as **1** text: python3 tools/verse.py "John {chapter}" --read-mark')
        return 0
    expect = 1
    exact = 0
    for ln, v, text in printed:
        if v > size:
            rep.add("TEXT-EXTRA", ln, f"John {chapter} has {size} verses; there is no verse {v}")
            continue
        if v < expect:
            rep.add("TEXT-ORDER", ln, f"verse {v} is printed again, or out of order; print verses 1 to {size} once each")
            continue
        if v > expect:
            rep.add("TEXT-MISSING", ln, f"John {chapter}:{_ranges(list(range(expect, v)))} is missing before verse {v}")
        want = kjvlib.norm_text(kjvlib.kjv()[("John", chapter, v)])
        got = kjvlib.norm_text(text)
        if got != want:
            rep.add("TEXT-MISMATCH", ln, f"John {chapter}:{v} {kjvlib._explain(got, want)} "
                                         f'Copy it from: python3 tools/verse.py "John {chapter}" --read-mark')
        else:
            exact += 1
        expect = v + 1
    if expect <= size:
        rep.add("TEXT-MISSING", span[1], f"John {chapter}:{_ranges(list(range(expect, size + 1)))} is not printed")
    return exact


def check_coverage(lines, heads, found, kind, chapter, quotes, rep):
    span = sub_span(heads, found, "Tier 2", WALK[kind])
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
            layers = parts(lines, (ln, stop - 1))
            missing = [n for n in ("Says", "Means", "Asks") if part(layers, n) is None]
            if missing:
                rep.add("LAYERS", ln, f"the block for John {chapter}:{v1}–{v2} needs "
                                      + ", ".join(f"**{n}:**" for n in missing)
                                      + ": keep what the text says, means, and asks visibly apart")
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


# ---------------------------------------------------------------- the shared sections

def check_at_a_glance(lines, heads, found, kind, rep):
    sub, lo, hi = ("Objectives", 2, 3) if kind == "chapter" else ("Course Outcomes", 3, 5)
    span = sub_span(heads, found, "At a Glance", sub)
    if span is not None:
        items = list_blocks(lines, span[0] + 1, span[1])
        if not lo <= len(items) <= hi:
            rep.add("LIST-COUNT", span[0], f'"{sub}" has {len(items)} list items; it needs {lo}–{hi}')
        if not any(re.match(r"^(?:[-*+]|\d+[.)])\s+\*\*Doing\s*[:.]?\s*\*\*", t, re.I) for _i, t in items):
            rep.add("LIST-COUNT", span[0], f'one item in "{sub}" must start with **Doing:**: something a learner '
                                           "can do this week that brings life or light")
    span = sub_span(heads, found, "At a Glance", "Life & Light At-a-Glance")
    if span is not None:
        tabs = tables(lines, span)
        rows = {key(strip_md(cells[0])): (i, cells) for i, cells in (tabs[0][1] if tabs else [])}
        for name in ("Life", "Light"):
            row = rows.get(key(name))
            if row is None:
                rep.add("AT-A-GLANCE", span[0], f"the Life & Light At-a-Glance table needs a **{name}** row "
                                                "(columns: what is dead or dark · where the source is, with verse · what I do today)")
            elif len(row[1]) < 4 or not valid_refs(row[1][2]):
                rep.add("AT-A-GLANCE", row[0], f"the {name} row needs four cells, the third naming the source with its verse")


VERSES_CELL = re.compile(rf"^(?:John\s+)?(?:(\d+):)?(\d+)(?:\s*{kjvlib.DASH}\s*(?:(\d+):)?(\d+))?$")


def check_map(lines, heads, found, kind, chapter, rep):
    span = sub_span(heads, found, "At a Glance", "Passage Map")
    if span is None:
        return
    tabs = tables(lines, span)
    data = tabs[0][1] if tabs else []
    if len(data) < 2:
        rep.add("TABLE-MAP", span[0], "the Passage Map needs a table (Section | Verses | Theme | One-Line Summary) "
                                      "with at least 2 rows")
        return
    if kind != "chapter":
        return
    size = kjvlib.chapter_sizes()[("John", chapter)]
    covered = set()
    for i, cells in data:
        matches = [(c, VERSES_CELL.match(strip_md(c))) for c in cells[:2]]
        matches = [(c, m) for c, m in matches if m]
        pick = next(((c, m) for c, m in matches if m.group(1)), matches[0] if matches else None)
        if not pick:
            rep.add("TABLE-MAP", i, f'the Verses cell should give verses of John {chapter}, like "{chapter}:1–15"; '
                                    f'found "{" | ".join(cells[:2])[:50]}"')
            continue
        cell, m = pick
        if (m.group(1) and int(m.group(1)) != chapter) or (m.group(3) and int(m.group(3)) != chapter):
            rep.add("TABLE-MAP", i, f'"{cell[:30]}" is not in John {chapter}')
            continue
        v1 = int(m.group(2))
        v2 = int(m.group(4)) if m.group(4) else v1
        if not 1 <= v1 <= v2 <= size:
            rep.add("TABLE-MAP", i, f'"{cell[:30]}" is outside John {chapter}:1–{size}')
            continue
        covered |= set(range(v1, v2 + 1))
    missing = sorted(set(range(1, size + 1)) - covered)
    if missing and len(missing) < size:
        rep.add("TABLE-MAP", span[0], f"the Passage Map leaves out John {chapter}:{_ranges(missing)}; its rows should cover the whole chapter")


def _ranges(nums):
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(f"{nums[i]}" if i == j else f"{nums[i]}–{nums[j]}")
        i = j + 1
    return ", ".join(out)


def check_foundations(lines, heads, found, quotes, rep):
    for sub, names in FOUNDATIONS.items():
        span = sub_span(heads, found, "Core Foundations", sub)
        if span is None:
            continue
        got = need_labels(lines, span, names, f'"{sub}"', rep)
        for name in ("The Truth", "The Source"):
            if name in got and not valid_refs(text_of(lines, got[name])):
                rep.add("LABELS", got[name][0], f'{name} in "{sub}" needs its verse (a reference)')
        if sub == "Christological Root":
            where = got.get("Gospel Foundation", span)
            if not whole_verses(quotes, where, gospel=True):
                rep.add("ROOT", where[0], "the Gospel Foundation must quote at least one Gospel passage in full "
                                          "(whole verses, with the reference)")
            if "Canonical Echoes" in got and len(valid_refs(text_of(lines, got["Canonical Echoes"]))) < 3:
                rep.add("ROOT", got["Canonical Echoes"][0], "Canonical Echoes needs the line Jesus → Promise → "
                                                            "Doctrine → Life, with at least 3 references")


def check_practice_set(items, where, tagged, ln0, rep):
    if len(items) < 3:
        rep.add("PRACTICES", ln0, f"{where} has {len(items)} practices; it needs at least 3, each a list item "
                                  "with a verse")
    for i, t in items:
        if not valid_refs(t):
            rep.add("PRACTICES", i, f"a practice in {where} has no verse: trace every practice to Christ with a "
                                    "reference (source discipline)")
    if tagged and items:
        tags = [TAG.match(t) for _i, t in items]
        if not all(tags):
            rep.add("PRACTICES", ln0, f"every practice in {where} begins with **Inward:** or **Outward:**")
        kinds = {t.group(1).lower() for t in tags if t}
        for kind in ("inward", "outward"):
            if kind not in kinds:
                rep.add("PRACTICES", ln0, f"{where} needs at least one **{kind.title()}:** practice")


def check_tiers(lines, heads, found, quotes, rep):
    span = sub_span(heads, found, "Tier 1", "Key Verses")
    if span is not None:
        n = len(whole_verses(quotes, span))
        if not 3 <= n <= 5:
            rep.add("KEY-VERSES", span[0], f"Tier 1 Key Verses quotes {n} whole verses; it needs 3–5 (a whole-verse "
                                           "quotation is the complete verse text, with its reference)")
    span = sub_span(heads, found, "Tier 1", "Diagnostic Check")
    if span is not None:
        items = [t for _i, t in list_blocks(lines, span[0] + 1, span[1]) if "?" in t]
        if not 4 <= len(items) <= 5:
            rep.add("LIST-COUNT", span[0], f'"Diagnostic Check" has {len(items)} questions (list items ending in ?); it needs 4–5')
    span = sub_span(heads, found, "Tier 2", "Common Errors Quick-Reference")
    if span is not None:
        tabs = tables(lines, span)
        data = tabs[0][1] if tabs else []
        if not 2 <= len(data) <= 4:
            rep.add("TABLE-ERRORS", span[0], f"Common Errors Quick-Reference needs a table (Error | Why it is wrong | "
                                             f"The correction, with verse) with 2–4 rows; found {len(data)}")
        for i, cells in data:
            if len(cells) < 3 or not valid_refs(cells[-1]):
                rep.add("TABLE-ERRORS", i, "each Common Errors row needs 3 cells, the last holding the correction's verse reference")
                break
    span = sub_span(heads, found, "Tier 3", "Debate Corner")
    if span is not None:
        need_labels(lines, span, ["Pastoral Warning"], '"Debate Corner"', rep)
    span = sub_span(heads, found, "Tier 3", "Preaching Mistakes to Avoid")
    if span is not None:
        items = list_blocks(lines, span[0] + 1, span[1])
        if len(items) < 3:
            rep.add("LIST-COUNT", span[0], f'"Preaching Mistakes to Avoid" has {len(items)} list items; it needs at least 3')
        text = strip_md(text_of(lines, span)).lower()
        for phrase in ("information without life", "heat without light"):
            if phrase not in text:
                rep.add("LIST-COUNT", span[0], f'"Preaching Mistakes to Avoid" must name the mistake "{phrase}"')
    span = sub_span(heads, found, "Tier 4", "Every Answer in Jesus")
    if span is not None:
        if not any(r.book == "Colossians" and r.c1 == 2 and r.v1 is not None and r.v1 <= 3 <= r.v2
                   for r in valid_refs(text_of(lines, span))):
            rep.add("LABELS", span[0], '"Every Answer in Jesus" rests on Colossians 2:3; cite it')
    for sub, tagged in (("Humility Practices", False), ("Life Practices", True), ("Light Practices", True)):
        span = sub_span(heads, found, "Tier 4", sub)
        if span is not None:
            check_practice_set(list_blocks(lines, span[0] + 1, span[1]), f'Tier 4 "{sub}"', tagged, span[0], rep)


def category_of(k):
    for i, c in enumerate(CATEGORIES):
        ck = key(c)
        if k == ck or k.startswith(ck + " "):
            return i
    return None


def check_doctrine(lines, heads, found, quotes, rep):
    span = section_span(found, "Doctrine")
    if span is None:
        return 0
    h3 = [(ln, raw, k) for ln, level, raw, k in heads if level == 3 and span[0] < ln <= span[1]]
    blocks, last, covered = 0, -1, set()
    for n, (ln, raw, k) in enumerate(h3):
        stop = h3[n + 1][0] - 1 if n + 1 < len(h3) else span[1]
        if k.startswith("assumed here"):
            for _i, t in list_blocks(lines, ln + 1, stop):
                m = LABEL.match(t)
                cat = category_of(key(m.group(1).rstrip(":."))) if m else None
                if cat is not None:
                    covered.add(cat)
            continue
        cat = category_of(k)
        if cat is None:
            rep.add("DOCTRINE-CATEGORY", ln, f'"### {raw[:50]}" must begin with its category: {", ".join(CATEGORIES)}'
                                             " (or be ### Assumed Here)")
            continue
        if cat < last:
            rep.add("DOCTRINE-ORDER", ln, f"{CATEGORIES[cat]} comes after {CATEGORIES[last]}; keep the blocks in the "
                                          f"category order {', '.join(CATEGORIES)}")
        last = max(last, cat)
        covered.add(cat)
        blocks += 1
        got = need_labels(lines, (ln, stop), DOCTRINE_PARTS, f'the doctrine block "{raw[:40]}"', rep)
        if "Cross-References" in got:
            xr = got["Cross-References"]
            q = len([x for x in quotes if in_span(x[0], xr)])
            if not 2 <= q <= 3:
                rep.add("DOCTRINE-XREF", xr[0], f'Cross-References in "{raw[:40]}" quotes {q} passages; quote 2–3, '
                                                "each exact KJV with its reference (Scripture interprets Scripture)")
    if blocks < 5:
        rep.add("DOCTRINE-FEW", span[0], f"the Doctrine section has {blocks} doctrine blocks; summarize the doctrines "
                                         "in great detail: at least 5 blocks (### Category · doctrine)")
    missing = [c for i, c in enumerate(CATEGORIES) if i not in covered]
    if missing:
        rep.add("DOCTRINE-CATEGORY", span[0], "no category may be skipped: give " + ", ".join(missing)
                + " a block, or a line under ### Assumed Here (- **Category:** how the chapter assumes it, and "
                  "where Scripture teaches it)")
    return blocks


def check_council(lines, heads, found, rep):
    speakers = set()
    asked = 0
    for n in (1, 2, 3):
        span = sub_span(heads, found, "The Council", f"Question {n}")
        if span is None:
            continue
        asked += 1
        pmap = parts(lines, span)
        if part(pmap, "Resolution") is None:
            rep.add("COUNCIL", span[0], f"Question {n} must end with a **Resolution:** from Scripture, or an honest "
                                        "summary of the views faithful readers hold")
        speakers |= set(pmap)
    if asked:
        pseudo = {k: (0, 0) for k in speakers}
        silent = [s for s in SCHOLARS if part(pseudo, s, *(["Curriculum Architect"] if s == "Teacher" else [])) is None]
        if silent:
            rep.add("COUNCIL", section_span(found, "The Council")[0],
                    "every scholar speaks in the three questions (a bold label such as **Historian:**); silent: "
                    + ", ".join(silent))
    span = sub_span(heads, found, "The Council", "The Life & Light Audit")
    if span is not None:
        pmap = parts(lines, span)
        missing = [n for n in ("Pastor", "Theologian") if part(pmap, n) is None]
        if part(pmap, "Teacher", "Curriculum Architect") is None:
            missing.append("Teacher")
        if part(pmap, "Fix") is None:
            missing.append("Fix")
        if missing:
            rep.add("LABELS", span[0], "The Life & Light Audit is missing " + ", ".join(f"**{n}:**" for n in missing))


def check_teaching_angles(lines, heads, found, rep):
    span = sub_span(heads, found, "Leader's Guide", "Teaching Angles")
    if span is not None:
        need_labels(lines, span, ["For a Tier 1 Group", "For a Tier 2 Group", "Tough Question 1", "Tough Question 2",
                                  "Tough Question 3"], '"Teaching Angles"', rep)


# ---------------------------------------------------------------- the lesson (chapter units)

def table_after(lines, ln, end):
    tabs = tables(lines, (ln + 1, end))
    return tabs[0] if tabs else None


def check_lesson(lines, heads, found, chapter, quotes, cites, doctrine_blocks, rep):
    """The participant pages. Returns (verses printed exactly, Mind the Language words)."""
    L = "The Lesson"
    span = sub_span(heads, found, L, "Open")
    if span is not None:
        need_labels(lines, span, ["Prayer focus", "Warm-up"], '"Open"', rep)
        if writeins(lines, span) < 2:
            rep.add("WRITE-IN", span[0], "the warm-up question needs at least two write-in lines (ten or more underscores)")
    span = sub_span(heads, found, L, "Setting the Scene")
    if span is not None:
        n = len(re.findall(r"\S+", text_of(lines, (span[0] + 1, span[1]))))
        lo, hi = SCENE_WORDS
        if not lo <= n <= hi:
            rep.add("LENGTH", span[0], f"Setting the Scene has {n} words; it needs {lo}–{hi}")
    printed = 0
    span = sub_span(heads, found, L, "Read & Mark")
    if span is not None:
        need_labels(lines, span, ["Marking key"], '"Read & Mark"', rep)
        printed = check_text(lines, span, chapter, rep)
    words = []
    span = sub_span(heads, found, L, "Mind the Language")
    if span is not None:
        tabs = tables(lines, span)
        data = tabs[0][1] if tabs else []
        if len(data) < 3:
            rep.add("GLOSSARY", span[0], f"Mind the Language needs a table (KJV word | Verse | What it means today) "
                                         f"with at least 3 rows; found {len(data)}")
        for i, cells in data:
            ref = verse_cell(cells[1], chapter) if len(cells) > 1 else None
            if ref is None:
                rep.add("GLOSSARY", i, "each Mind the Language row gives the word, then its verse (John C:V), then a blank")
                continue
            if not word_in_verse(cells[0], ref):
                rep.add("GLOSSARY", i, f'"{strip_md(cells[0])[:30]}" is not in {ref}; the KJV reads: {ref.text()[:140]}')
            if len(cells) < 3 or not BLANK.search(cells[2]):
                rep.add("WRITE-IN", i, "the third cell of a Mind the Language row is a blank for the participant (__________)")
            words.append((i, strip_md(cells[0])))
    span = sub_span(heads, found, L, "Word Study")
    if span is not None:
        tabs = tables(lines, span)
        data = tabs[0][1] if tabs else []
        if not 3 <= len(data) <= 6:
            rep.add("WORD-STUDY", span[0], f"Word Study needs a table (KJV word | Verse | Original word | Sense | Your lookup) "
                                           f"with 3–6 rows; found {len(data)}")
        for i, cells in data:
            ref = verse_cell(cells[1], chapter) if len(cells) > 1 else None
            if ref is None or len(cells) < 5:
                rep.add("WORD-STUDY", i, "each Word Study row has five cells: the KJV word, its verse (John C:V), the Greek "
                                         "word cited as *translit* (G####, John C:V), its sense, and a blank lookup")
                continue
            if not word_in_verse(cells[0], ref):
                rep.add("WORD-STUDY", i, f'"{strip_md(cells[0])[:30]}" is not in {ref}; the KJV reads: {ref.text()[:140]}')
            here = [c for c in cites if c[0] == i]
            if not here or not any(c[3] is not None and (c[3].book, c[3].c1, c[3].v1) == (ref.book, ref.c1, ref.v1)
                                   for c in here):
                rep.add("WORD-STUDY", i, f"the Original word cell needs a checked citation for {ref}: "
                                         f"*translit* (G####, {ref}); look it up with python3 tools/greek.py \"{ref}\"")
            if not BLANK.search(cells[4]):
                rep.add("WRITE-IN", i, "the last cell of a Word Study row is a blank for the participant's lookup (__________)")
    span = sub_span(heads, found, L, "Search the Scriptures")
    if span is not None:
        items = list_blocks(lines, span[0] + 1, span[1])
        if not 3 <= len(items) <= 6:
            rep.add("LIST-COUNT", span[0], f'"Search the Scriptures" has {len(items)} cross-references (list items); it needs 3–6')
        for i, t in items:
            if not valid_refs(t):
                rep.add("LIST-COUNT", i, "each cross-reference in Search the Scriptures names its verse")
    span = sub_span(heads, found, L, "Interpret")
    if span is not None:
        got = need_labels(lines, span, ["View A", "View B"], '"Interpret" (the View A / View B panel)', rep)
        for name, sp in got.items():
            if not valid_refs(text_of(lines, sp)):
                rep.add("LABELS", sp[0], f"{name} needs its proof text (a reference)")
    span = sub_span(heads, found, L, "Case Study")
    if span is not None and not valid_refs(text_of(lines, span)):
        rep.add("LABELS", span[0], "the Case Study needs the passage where the Bible character is found (a reference)")
    span = sub_span(heads, found, L, "Doctrine in My Own Words")
    if span is not None:
        items = list_blocks(lines, span[0] + 1, span[1])
        if doctrine_blocks and len(items) != doctrine_blocks:
            rep.add("LIST-COUNT", span[0], f'"Doctrine in My Own Words" lists {len(items)} propositions; the Doctrine '
                                           f"section has {doctrine_blocks} doctrine blocks: list one proposition for each")
        if writeins(lines, span) < 2:
            rep.add("WRITE-IN", span[0], "Doctrine in My Own Words ends with at least two write-in lines")
    span = sub_span(heads, found, L, "Apply")
    if span is not None:
        need_labels(lines, span, ["Head", "Heart", "Hands"], '"Apply"', rep)
        if not any(re.match(r"^\s*I will\b.*_{5,}", lines[i - 1]) for i in lines_in(lines, span)):
            rep.add("FIXED-LINE", span[0], 'Apply ends with an "I will ..." commitment line with blanks: I will __________ by __________ (day).')
    span = sub_span(heads, found, L, "Christocentric & Humility")
    if span is not None:
        ln = label_line(lines, span, "Humility Practices")
        if ln is None:
            rep.add("LABELS", span[0], 'Christocentric & Humility needs a **Humility Practices** label with its list')
        else:
            check_practice_set(list_blocks(lines, ln + 1, span[1], contiguous=True), "Level 4 Humility Practices",
                               False, ln, rep)
    check_pathway_page(lines, heads, found, "Bring Life", "Life", rep)
    check_pathway_page(lines, heads, found, "Bring Light", "Light", rep)
    span = sub_span(heads, found, L, "Memory Verse")
    if span is not None:
        n = len(whole_verses(quotes, span))
        if n != 1:
            rep.add("MEMORY-VERSE", span[0], f"the Memory Verse section quotes {n} whole verses; it quotes exactly one, in full")
        if writeins(lines, span) < 2:
            rep.add("WRITE-IN", span[0], "the Memory Verse needs at least two copy-it-out lines (ten or more underscores)")
    span = sub_span(heads, found, L, "Gather")
    if span is not None:
        items = [(i, t) for i, t in list_blocks(lines, span[0] + 1, span[1])
                 if re.match(r"^[-*+]\s+\*\*Group question \d", t, re.I)]
        if len(items) != 4:
            rep.add("LIST-COUNT", span[0], f'"Gather" has {len(items)} group questions; it needs 4, as '
                                           "- **Group question 1 · 10 min.** ...")
        for i, t in items:
            if not re.search(r"\d+\s*min", t):
                rep.add("LIST-COUNT", i, "each group question names its minutes, like **Group question 1 · 10 min.**")
        if not any("naming round" in t.lower() for _i, t in items):
            rep.add("LIST-COUNT", span[0], "one Gather item is the naming round: each member reads the name on their "
                                           "Life Planner and the dark place on their Light Planner")
    span = sub_span(heads, found, L, "Closing & Going Deeper")
    if span is not None:
        need_labels(lines, span, ["Closing prayer focus", "For the week ahead", "Next in John"], '"Closing & Going Deeper"', rep)
        if len(valid_refs(text_of(lines, span))) < 3:
            rep.add("LIST-COUNT", span[0], "Closing & Going Deeper names at least 3 passages (references) for the week ahead")
    return printed, words


GUARDS = {"Life": ("fullness of life in christ", "*Abundant life is fullness of life in Christ — not money, not ease, "
                                                 "not freedom from suffering.*"),
          "Light": ("light without love is glare", "*Light exposes, but light without love is glare; reproof is never "
                                                   "license for contempt or public shaming.*")}
COMMITMENTS = {"Life": (r"I will bring life to\s+_{5,}\s+by\s+_{5,}\s+before\s+_{5,}",
                        "I will bring life to __________ by __________ before __________ (day)."),
               "Light": (r"I will carry light into\s+_{5,}\s+by\s+_{5,}\s+before\s+_{5,}",
                         "I will carry light into __________ by __________ before __________ (day).")}


def check_pathway_page(lines, heads, found, sub, what, rep):
    span = sub_span(heads, found, "The Lesson", sub)
    if span is None:
        return
    planner = label_line(lines, span, f"{what} Planner")
    if planner is None:
        rep.add("PLANNER", span[0], f"{sub} needs the **{what} Planner** label and its table")
    else:
        tab = table_after(lines, planner, span[1])
        if tab is None or len(tab[0]) < 5:
            rep.add("PLANNER", planner, f"the {what} Planner is a five-column table (see TEMPLATE.md) under its label")
        else:
            header, rows = tab
            first = key(header[0])
            if (what == "Life" and "dead" not in first) or (what == "Light" and "dark" not in first):
                rep.add("PLANNER", planner, f"the {what} Planner's columns are KJV82's (see TEMPLATE.md); "
                                            f'its first column asks {"who is dead, dying, or deadened" if what == "Life" else "where it is dark"}')
            if not rows or not any(BLANK.search(c) for _i, cells in rows for c in cells):
                rep.add("PLANNER", planner, f"the {what} Planner needs write-in rows (cells of __________)")
            if what == "Light" and (len(rows) < 2 or not key(strip_md(rows[0][1][0])).startswith("my own heart")):
                rep.add("PLANNER", planner, "the Light Planner has at least two rows, and the first is the participant's "
                                            "own heart: | My own heart: __________ | ...")
    ln = label_line(lines, span, f"{what} Practices")
    if ln is None:
        rep.add("LABELS", span[0], f"{sub} needs the **{what} Practices** label with its list")
    else:
        check_practice_set(list_blocks(lines, ln + 1, span[1], contiguous=True), f"Level 5 {what} Practices", True, ln, rep)
    if what == "Life" and label_line(lines, span, "A Line to Say") is None:
        rep.add("LABELS", span[0], "Bring Life needs **A Line to Say:** a sentence the participant can say this week "
                                   "to a dying, despairing, or deadened person")
    pattern, line = COMMITMENTS[what]
    if not any(re.search(pattern, lines[i - 1]) for i in lines_in(lines, span)):
        rep.add("FIXED-LINE", span[0], f"{sub} needs its commitment line: {line}")
    phrase, guard = GUARDS[what]
    if not any(phrase in lines[i - 1].lower() and re.match(r"^\s*[*_]", lines[i - 1]) for i in lines_in(lines, span)):
        rep.add("FIXED-LINE", span[0], f"{sub} prints its guard in italics on its own line: {guard}")


def check_questions(lines, heads, found, chapter, rep):
    lesson = section_span(found, "The Lesson")
    if lesson is None:
        return 0
    qs = q_lines(lines, lesson)
    expect = 1
    for ln, n in qs:
        if n != expect:
            rep.add("QUESTIONS", ln, f"Q{n} should be Q{expect}: number the questions Q1, Q2, ... through the lesson, "
                                     "with no gaps or repeats")
        expect = n + 1
        if writeins_after(lines, ln, lesson[1]) < 2:
            rep.add("WRITE-IN", ln, f"Q{n} needs at least two write-in lines under it (lines of ten or more underscores)")
    for sub, lo, hi in QUESTION_COUNTS:
        span = sub_span(heads, found, "The Lesson", sub)
        if span is None:
            continue
        n = len(q_lines(lines, span))
        if not lo <= n <= hi:
            rng = f"at least {lo}" if hi == 99 else f"{lo}–{hi}"
            rep.add("QUESTIONS", span[0], f'"{sub}" has {n} numbered questions (**Qn.**); it needs {rng}')
        if sub == "Observe":
            for ln, n in q_lines(lines, span):
                if not any(r.book == "John" and r.c1 == chapter and r.v1 for r in valid_refs(lines[ln - 1])):
                    rep.add("QUESTIONS", ln, f"Observe question Q{n} names the verse it asks about, like (John {chapter}:3)")
    span = sub_span(heads, found, "Leader's Guide", "Answer Key")
    if span is not None:
        answers = q_lines(lines, span)
        got = set()
        for n, (ln, q) in enumerate(answers):
            end = answers[n + 1][0] - 1 if n + 1 < len(answers) else span[1]
            got.add(q)
            if not valid_refs(text_of(lines, (ln, end))):
                rep.add("ANSWER-KEY", ln, f"the answer to Q{q} cites no verse; give verse support for every answer")
        asked = {n for _ln, n in qs}
        missing, extra = sorted(asked - got), sorted(got - asked)
        if missing:
            rep.add("ANSWER-KEY", span[0], "no answer for " + ", ".join(f"Q{n}" for n in missing)
                    + "; the Answer Key answers every question, as **Qn.** answer (verse)")
        if extra:
            rep.add("ANSWER-KEY", span[0], "answers for questions the lesson doesn't ask: " + ", ".join(f"Q{n}" for n in extra))
    return len(qs)


def check_guide(lines, heads, found, words, rep):
    span = sub_span(heads, found, "Leader's Guide", "Session Plan")
    if span is not None:
        tabs = tables(lines, span)
        if not tabs:
            rep.add("SESSION-PLAN", span[0], "the Session Plan is a table: Segment | Minutes | What happens")
        else:
            header, rows = tabs[0]
            col = next((n for n, h in enumerate(header) if "min" in key(h)), None)
            if col is None:
                rep.add("SESSION-PLAN", span[0], "the Session Plan table needs a Minutes column")
            else:
                total, stated = 0, None
                for i, cells in rows:
                    m = re.search(r"\d+", cells[col]) if col < len(cells) else None
                    if key(strip_md(cells[0])).startswith("total"):
                        stated = int(m.group(0)) if m else None
                        continue
                    if not m:
                        rep.add("SESSION-PLAN", i, "every Session Plan row gives its minutes as a number")
                        continue
                    total += int(m.group(0))
                if total != SESSION_MINUTES:
                    rep.add("SESSION-PLAN", span[0], f"the Session Plan's minutes add up to {total}; the session is "
                                                     f"{SESSION_MINUTES} minutes")
                if stated is not None and stated != total:
                    rep.add("SESSION-PLAN", span[0], f"the Total row says {stated}, but the rows add up to {total}")
                if not any("naming round" in " ".join(cells).lower() for _i, cells in rows):
                    rep.add("SESSION-PLAN", span[0], "the Session Plan gives minutes to the naming round")
    span = sub_span(heads, found, "Leader's Guide", "Glossary")
    if span is not None:
        tabs = tables(lines, span)
        data = tabs[0][1] if tabs else []
        if not data:
            rep.add("GLOSSARY", span[0], "the Glossary is a table: KJV word | Verse | Meaning")
        glossed = set()
        for i, cells in data:
            ref = verse_cell(cells[1]) if len(cells) > 2 else None
            if ref is None:
                rep.add("GLOSSARY", i, "each Glossary row gives the word, its verse (John C:V), and its meaning")
                continue
            if not word_in_verse(cells[0], ref):
                rep.add("GLOSSARY", i, f'"{strip_md(cells[0])[:30]}" is not in {ref}; the KJV reads: {ref.text()[:140]}')
            glossed.add(word_key(cells[0]))
        for i, w in words:
            if word_key(w) not in glossed:
                rep.add("GLOSSARY", i, f'"{w}" is flagged in Mind the Language but missing from the Glossary')
    span = sub_span(heads, found, "Leader's Guide", "Life & Light Leader's Map")
    if span is not None:
        need_labels(lines, span, ["Worked Life Planner Row", "Worked Light Planner Row", "When Someone Has No One to Name",
                                  "When Someone Points the Light at Others"], '"Life & Light Leader\'s Map"', rep)


# ---------------------------------------------------------------- the overview (unit 00)

def check_overview(lines, heads, found, rep):
    span = sub_span(heads, found, "Workbook Blueprint", "Lesson Map")
    if span is not None:
        tabs = tables(lines, span)
        if not tabs:
            rep.add("BLUEPRINT", span[0], "the Lesson Map is a table with KJV82's Blueprint columns (see TEMPLATE.md)")
        else:
            header, rows = tabs[0]
            cols = [key(h) for h in header]
            want = ["Lesson", "Title", "Passage", "Big Idea", "Core Doctrines", "Objective", "Memory Verse", "Life → Light"]
            if [c for c in cols] != [key(w) for w in want]:
                rep.add("BLUEPRINT", span[0], "the Lesson Map's columns are: " + " | ".join(want))
            if len(rows) != 21:
                rep.add("BLUEPRINT", span[0], f"the Lesson Map has {len(rows)} rows; it needs 21, one per chapter")
            for n, (i, cells) in enumerate(rows, 1):
                if len(cells) < 8 or any(not strip_md(c) for c in cells[:8]):
                    rep.add("BLUEPRINT", i, f"Lesson {n}'s row needs all eight cells filled")
                    continue
                if strip_md(cells[0]) != str(n):
                    rep.add("BLUEPRINT", i, f'expected lesson {n} here, found "{cells[0][:10]}"; lessons run 1 to 21 in order')
                refs = valid_refs(cells[2])
                if not refs or refs[0].book != "John" or refs[0].c1 != n:
                    rep.add("BLUEPRINT", i, f"lesson {n}'s Passage is John {n}")
                mv = verse_cell(cells[6])
                if mv is None or mv.book != "John" or mv.c1 != n:
                    rep.add("BLUEPRINT", i, f"lesson {n}'s Memory Verse is one verse of John {n} (John {n}:V)")
    span = sub_span(heads, found, "Workbook Blueprint", "Life & Light Ledger")
    if span is not None:
        tabs = tables(lines, span)
        rows = tabs[0][1] if tabs else []
        if len(rows) != 21 or [strip_md(c[0]) for _i, c in rows] != [str(n) for n in range(1, 22)]:
            rep.add("LEDGER", span[0], "the Life & Light Ledger has 21 rows, lessons 1 to 21, with write-in blanks")
        if not any(r.book == "John" and r.c1 == 15 and r.v1 == 5 for r in valid_refs(text_of(lines, span))):
            rep.add("LEDGER", span[0], "the Ledger closes with its line: this page records what Christ did through you, "
                                       "not what you achieved (John 15:5)")
    span = sub_span(heads, found, "Leader's Guide", "Teacher FAQ")
    if span is not None:
        n = len([t for _i, t in list_blocks(lines, span[0] + 1, span[1]) if re.match(r"^[-*+]\s+\*\*[^*]*\?\s*\*\*", t)])
        if n < 6:
            rep.add("LIST-COUNT", span[0], f'"Teacher FAQ" has {n} questions; it needs at least 6, as - **question?** answer')
    span = sub_span(heads, found, "Leader's Guide", "Advanced Teacher Hacks")
    if span is not None:
        n = len(list_blocks(lines, span[0] + 1, span[1]))
        if n < 8:
            rep.add("LIST-COUNT", span[0], f'"Advanced Teacher Hacks" has {n} list items; it needs at least 8')
    span = sub_span(heads, found, "Leader's Guide", "Going Deeper")
    if span is not None and len(valid_refs(text_of(lines, span))) < 3:
        rep.add("LIST-COUNT", span[0], "Going Deeper names at least 3 passages, including one each on life, light, and sound doctrine")


# ---------------------------------------------------------------- Greek, counts, and the rest

# *agapaō* (G25, John 21:15) · *agapas* (G25, John 21:15, V-PAI-2S) · *mishkan* (H4908) — bold is accepted too
CITE = re.compile(r"\*{1,2}([^*\n]{1,40})\*{1,2}\s*\(\s*([GH]\d{1,4}[A-Za-z]?)\s*(?:[,·;]\s*([^,·;()]+?)\s*)?"
                  r"(?:[,·;]\s*([A-Z0-9]+(?:-[A-Z0-9]+)*)\s*)?\)")
GREEK_SCRIPT = re.compile(r"[Ͱ-Ͽἀ-῿]")    # Greek and Coptic U+0370–03FF, Greek Extended U+1F00–1FFF
HEBREW_SCRIPT = re.compile(r"[֐-׿]")        # Hebrew U+0590–05FF


def check_greek(body, heads, found, rep):
    """Returns [(line, strong key, morph, Ref or None)] for every checked citation."""
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
            cites.append((ln, skey, morph, ref))
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
        cites.append((ln, skey, morph, ref))
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
    span = sub_span(heads, found, "Tier 3", "Original Language Deep Dive")
    if span is not None and not [c for c in cites if in_span(c[0], span) and c[1].startswith("G") and c[2]]:
        rep.add("GREEK-MISSING", span[0], '"Original Language Deep Dive" needs at least one checked Greek citation '
                                          "with a parsing code, like *agapas* (G25, John 21:15, V-PAI-2S)")
    return cites


def check_counts(raw, body, rep):
    backed = set()
    for block in re.finditer(r"<!--\s*counts\b(.*?)-->", raw, flags=re.S):
        for off, line in enumerate(block.group(1).split("\n")):
            if not line.strip():
                continue
            ln = line_of(raw, block.start()) + off
            fields = [p.strip() for p in line.split("|")]
            if len(fields) != 3 or not fields[2].isdigit():
                rep.add("COUNT-FORMAT", ln, f'counts lines read "query | scope | number", found "{line.strip()[:60]}"')
                continue
            try:
                total, _hits = kjvlib.count(fields[0], fields[1])
            except (kjvlib.RefError, ValueError) as e:
                rep.add("COUNT-FORMAT", ln, f"can't recount \"{line.strip()}\": {e}")
                continue
            if total != int(fields[2]):
                rep.add("COUNT-WRONG", ln, f'"{fields[0]}" occurs {total} times in {fields[1]}, not {fields[2]} '
                                           f'(python3 tools/concordance.py "{fields[0]}" "{fields[1]}")')
                continue
            backed.add(total)
    for m in re.finditer(r"\b(\d{1,4})\s+times\b", body):
        if int(m.group(1)) not in backed:
            rep.add("COUNT-UNBACKED", line_of(body, m.start()),
                    f'"{m.group(0)}" is a count. Compute it with tools/concordance.py and add its line to the '
                    "<!-- counts --> block, or write the number in words if it's a detail of the story")


# a skeleton line left as it was: "...", a label followed only by "...", or a table cell of "..."
LEFTOVER = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*[^*\n]+\*\*\s*)?(?:\.\.\.|…)\s*\??\s*$|\|\s*(?:\.\.\.|…)\s*\|", re.M)


def check_misc(body, kind, heads, rep):
    words = len(re.findall(r"\S+", body))
    lo, hi = WORDS[kind]
    if not lo <= words <= hi:
        rep.add("LENGTH", 0, f"the unit has {words:,} words; it must have {lo:,}–{hi:,}. "
                             + ("Deepen thin sections rather than padding." if words < lo else
                                "Cut repetition; length earns nothing."))
    for m in re.finditer(r"\{\{|\bTODO\b|\bTBD\b|\[insert|lorem ipsum|\bXXX\b", body, flags=re.I):
        rep.add("PLACEHOLDER", line_of(body, m.start()), f'placeholder text "{m.group(0)}" is still in the unit')
    for m in LEFTOVER.finditer(body):
        rep.add("PLACEHOLDER", line_of(body, m.start()), "a skeleton line was left as ...; write the content")
    for ln, _level, raw, k in heads:
        if "self audit" in k or "flywheel" in k or "verification" in k or "conformity" in k:
            rep.add("SELF-GRADE", ln, f'"{raw[:40]}": the maker never grades its own work here; the checker '
                                      "and the judge do. Remove this section.")
    for m in re.finditer(r"\|\s*\d{1,2}\s*/\s*10\s*\|", body):
        rep.add("SELF-GRADE", line_of(body, m.start()), "a /10 self-score table; remove it (the judge scores the unit)")
    for m in re.finditer(r"\b(PASS|FIX)\b", body):
        rep.add("SELF-GRADE", line_of(body, m.start()), f'"{m.group(0)}": a PASS/FIX self-check; remove it (the checker '
                                                        "and the judge do this)")
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
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if not raw.strip():
        rep.add("EMPTY", 0, "the file is empty. Write the unit following TEMPLATE.md.")
        return rep, {}
    body = blank_comments(raw)
    lines = body.split("\n")
    if not check_header(lines, unit, kind, chapter, rep):
        return rep, {}
    heads = parse_headings(lines)
    found = check_structure(heads, kind, len(lines), rep)
    quotes = check_quotes(body, rep)
    check_single_quotes(body, rep)
    check_refs(body, rep)
    covered = check_coverage(lines, heads, found, kind, chapter, quotes, rep)
    cites = check_greek(body, heads, found, rep)
    check_at_a_glance(lines, heads, found, kind, rep)
    check_map(lines, heads, found, kind, chapter, rep)
    check_foundations(lines, heads, found, quotes, rep)
    check_tiers(lines, heads, found, quotes, rep)
    blocks = check_doctrine(lines, heads, found, quotes, rep)
    check_council(lines, heads, found, rep)
    check_teaching_angles(lines, heads, found, rep)
    printed = questions = 0
    if kind == "chapter":
        printed, words = check_lesson(lines, heads, found, chapter, quotes, cites, blocks, rep)
        questions = check_questions(lines, heads, found, chapter, rep)
        check_guide(lines, heads, found, words, rep)
    else:
        check_overview(lines, heads, found, rep)
    check_counts(raw, body, rep)
    check_misc(body, kind, heads, rep)
    stats = {"quotes": len(quotes), "covered": covered, "greek": len(cites), "printed": printed,
             "questions": questions, "doctrines": blocks, "words": len(re.findall(r"\S+", body))}
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
        if a.unit == "00":
            detail = f"{total}/{total} chapters covered in the breakdown"
        else:
            detail = (f"{stats['printed']}/{total} verses printed exactly · {total}/{total} verses expounded in "
                      f"{blocks} blocks · {stats['questions']} questions answered")
        out.append(f"PASS · john-{a.unit} · deterministic checks · {stats['quotes']} quotations exact · {detail} · "
                   f"{stats['doctrines']} doctrine blocks · {stats['greek']} Greek/Hebrew citations verified · "
                   f"{stats['words']:,} words")
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
