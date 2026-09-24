"""Shared helpers for the John KJV study loop.

Everything that decides "is this quotation exact?" or "is this Greek word really
in that verse?" lives here, so the maker's lookup tools and the checker can never
disagree. Data comes only from the files in kjv/ (see kjv/SOURCE.md).
"""
import functools
import gzip
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KJV_TSV = os.path.join(ROOT, "kjv", "kjv.tsv")
GREEK_TSV = os.path.join(ROOT, "kjv", "greek-nt.tsv.gz")
LEXICON_TSV = os.path.join(ROOT, "kjv", "lexicon.tsv.gz")

BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians",
    "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation",
]
NT_BOOKS = BOOKS[BOOKS.index("Matthew"):]
GOSPELS = ["Matthew", "Mark", "Luke", "John"]

# Other spellings a writer might use. Abbreviations count only in chapter:verse form.
_FULL_ALIASES = {"Psalm": "Psalms", "Song of Songs": "Song of Solomon", "Revelations": "Revelation"}
_ABBREVIATIONS = {
    "Gen": "Genesis", "Ex": "Exodus", "Exod": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "1 Sam": "1 Samuel",
    "2 Sam": "2 Samuel", "1 Kgs": "1 Kings", "2 Kgs": "2 Kings", "1 Chr": "1 Chronicles",
    "2 Chr": "2 Chronicles", "Neh": "Nehemiah", "Esth": "Esther", "Ps": "Psalms", "Psa": "Psalms",
    "Prov": "Proverbs", "Eccl": "Ecclesiastes", "Eccles": "Ecclesiastes", "Isa": "Isaiah",
    "Jer": "Jeremiah", "Lam": "Lamentations", "Ezek": "Ezekiel", "Dan": "Daniel", "Hos": "Hosea",
    "Obad": "Obadiah", "Mic": "Micah", "Nah": "Nahum", "Hab": "Habakkuk", "Zeph": "Zephaniah",
    "Hag": "Haggai", "Zech": "Zechariah", "Mal": "Malachi", "Matt": "Matthew", "Mt": "Matthew",
    "Mk": "Mark", "Lk": "Luke", "Jn": "John", "Rom": "Romans", "1 Cor": "1 Corinthians",
    "2 Cor": "2 Corinthians", "Gal": "Galatians", "Eph": "Ephesians", "Phil": "Philippians",
    "Col": "Colossians", "1 Thess": "1 Thessalonians", "2 Thess": "2 Thessalonians",
    "1 Tim": "1 Timothy", "2 Tim": "2 Timothy", "Tit": "Titus", "Phlm": "Philemon",
    "Heb": "Hebrews", "Jas": "James", "1 Pet": "1 Peter", "2 Pet": "2 Peter", "1 Jn": "1 John",
    "2 Jn": "2 John", "3 Jn": "3 John", "Rev": "Revelation",
}


def _variants(name):
    """'1 John' may also be written '1John'."""
    out = {name}
    if re.match(r"^[1-3] ", name):
        out.add(name.replace(" ", "", 1))
    return out


FULL_NAMES = {}
for _b in BOOKS:
    for _v in _variants(_b):
        FULL_NAMES[_v] = _b
for _a, _b in _FULL_ALIASES.items():
    FULL_NAMES[_a] = _b
ABBREVS = {}
for _a, _b in _ABBREVIATIONS.items():
    for _v in _variants(_a):
        ABBREVS[_v] = _b


def _alternation(names):
    return "|".join(re.escape(n).replace(r"\ ", r"\s") for n in sorted(names, key=len, reverse=True))


DASH = r"[-‐‑‒–—]"
# "John 3:16", "John 3:16-18", "John 7:53-8:11", "John 3" (chapter only, full names only)
FULL_REF = re.compile(
    rf"(?<![\w.])({_alternation(FULL_NAMES)})\s+(\d+)(?::(\d+)(?:\s*{DASH}\s*(\d+)(?::(\d+))?)?)?(?![\w:])")
ABBR_REF = re.compile(
    rf"(?<![\w.])({_alternation(ABBREVS)})\.?\s+(\d+):(\d+)(?:\s*{DASH}\s*(\d+)(?::(\d+))?)?(?![\w:])")


def canonical_book(name):
    name = re.sub(r"\s+", " ", name.strip().rstrip("."))
    return FULL_NAMES.get(name) or ABBREVS.get(name)


@functools.lru_cache(maxsize=None)
def kjv():
    """(book, chapter, verse) -> text, in canonical order."""
    out = {}
    with open(KJV_TSV, encoding="utf-8") as f:
        next(f)
        for line in f:
            book, ch, vs, text = line.rstrip("\n").split("\t")
            out[(book, int(ch), int(vs))] = text
    return out


@functools.lru_cache(maxsize=None)
def chapter_sizes():
    sizes = {}
    for book, ch, vs in kjv():
        sizes[(book, ch)] = max(vs, sizes.get((book, ch), 0))
    return sizes


class RefError(ValueError):
    pass


class Ref:
    """A verse, a range of verses, or a whole chapter, already validated."""

    def __init__(self, book, c1, v1=None, c2=None, v2=None):
        self.book, self.c1, self.v1 = book, c1, v1
        self.c2 = c2 if c2 is not None else c1
        self.v2 = v2 if v2 is not None else v1
        sizes = chapter_sizes()
        for c in (self.c1, self.c2):
            if (book, c) not in sizes:
                raise RefError(f"{book} has no chapter {c}")
        if v1 is not None:
            for c, v in ((self.c1, self.v1), (self.c2, self.v2)):
                if not 1 <= v <= sizes[(book, c)]:
                    raise RefError(f"{book} {c} has {sizes[(book, c)]} verses, so {book} {c}:{v} doesn't exist")
            if (self.c2, self.v2) < (self.c1, self.v1):
                raise RefError(f"the range {self} runs backwards")

    def verses(self):
        sizes = chapter_sizes()
        out = []
        for c in range(self.c1, self.c2 + 1):
            first = self.v1 if (self.v1 is not None and c == self.c1) else 1
            last = self.v2 if (self.v2 is not None and c == self.c2) else sizes[(self.book, c)]
            out += [(self.book, c, v) for v in range(first, last + 1)]
        return out

    def text(self):
        return " ".join(kjv()[k] for k in self.verses())

    def __str__(self):
        if self.v1 is None:
            return f"{self.book} {self.c1}"
        s = f"{self.book} {self.c1}:{self.v1}"
        if (self.c2, self.v2) != (self.c1, self.v1):
            s += f"–{self.v2}" if self.c2 == self.c1 else f"–{self.c2}:{self.v2}"
        return s


def _ref_from_match(m):
    book = canonical_book(m.group(1))
    c1 = int(m.group(2))
    v1 = int(m.group(3)) if m.group(3) else None
    if m.group(4) is None:
        return Ref(book, c1, v1)
    if m.group(5):       # John 7:53-8:11
        return Ref(book, c1, v1, int(m.group(4)), int(m.group(5)))
    return Ref(book, c1, v1, c1, int(m.group(4)))


def parse_ref(s):
    """Parse one whole reference such as 'John 3:16' or 'John 3:16-18'. Raises RefError."""
    s = s.strip()
    for rx in (FULL_REF, ABBR_REF):
        m = rx.fullmatch(s)
        if m:
            return _ref_from_match(m)
    raise RefError(f"'{s}' isn't a reference in the form Book C:V or Book C:V–W")


def parse_ref_list(s):
    """'John 1:39, 46' or 'John 10:11, 14' or 'John 7:37; 8:12' -> [Ref, ...] in one book.
    A single reference gives a one-item list. Raises RefError."""
    s = s.strip()
    m = re.match(rf"^(.*?\d+:\d+(?:\s*{DASH}\s*\d+(?::\d+)?)?)((?:\s*[,;]\s*(?:\d+:)?\d+(?:\s*{DASH}\s*\d+)?)*)$", s)
    if not m:
        return [parse_ref(s)]
    first = parse_ref(m.group(1))
    refs = [first]
    chapter = first.c2
    for part in re.finditer(rf"[,;]\s*(?:(\d+):)?(\d+)(?:\s*{DASH}\s*(\d+))?", m.group(2)):
        chapter = int(part.group(1)) if part.group(1) else chapter
        v1 = int(part.group(2))
        refs.append(Ref(first.book, chapter, v1, chapter, int(part.group(3)) if part.group(3) else v1))
    return refs


def find_refs(text):
    """Every reference written in running text: [(start, end, raw, Ref or RefError)].

    Follow-on verses in the same chapter ('John 1:1, 14') and chapters in the same
    book ('John 1:1; 3:16') are checked too.
    """
    found = []
    taken = []
    for rx in (FULL_REF, ABBR_REF):
        for m in rx.finditer(text):
            if any(a <= m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            try:
                ref = _ref_from_match(m)
            except RefError as e:
                ref = e
            found.append((m.start(), m.end(), m.group(0), ref))
            if isinstance(ref, RefError) or ref.v1 is None:
                continue
            book, chapter, pos = ref.book, ref.c2, m.end()
            follow = re.compile(rf"\s*([,;])\s*(?:(\d+):)?(\d+)(?:\s*{DASH}\s*(\d+))?(?![\w:])(?!\s+[A-Z][a-z])(?!\s+(?!and\b|to\b|f\b|ff\b)[a-z])")
            while True:
                f = follow.match(text, pos)
                if not f or (f.group(1) == ";" and not f.group(2)):
                    break
                chapter = int(f.group(2)) if f.group(2) else chapter
                try:
                    extra = Ref(book, chapter, int(f.group(3)), chapter,
                                int(f.group(4)) if f.group(4) else int(f.group(3)))
                except RefError as e:
                    extra = e
                found.append((f.start(), f.end(), f.group(0).strip(" ,;"), extra))
                taken.append((f.start(), f.end()))
                pos = f.end()
    return sorted(found, key=lambda x: x[0])


# ---------- comparing a quotation with the KJV ----------

ELLIPSIS = re.compile(r"\s*(?:\.\s?\.\s?\.|…)\s*")


def norm_text(s):
    """Differences that aren't differences in wording: quote style, the ae ligature,
    markdown emphasis markers, and spacing."""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("Æ", "Ae").replace("æ", "ae").replace("--", "—")
    s = s.replace("*", "").replace("_", "")
    s = re.sub(r"\s*\n\s*>?\s*", " ", s)       # a quote wrapped across blockquote lines
    return re.sub(r"\s+", " ", s).strip()


def _find(segment, text, start):
    i = text.find(segment, start)
    if i < 0 and segment:   # the first letter of a quotation may change case
        alt = segment[0].swapcase() + segment[1:]
        i = text.find(alt, start)
    return i


def match_quote(quote, ref):
    """(True, '') when the quotation is exact KJV text of ref, else (False, why)."""
    source = norm_text(ref.text())
    q = norm_text(quote)
    if "[" in q or "]" in q:
        return False, "square brackets inside a quotation add words the KJV doesn't have; quote the text as printed"
    segments = [s for s in ELLIPSIS.split(q) if s]
    if not segments:
        return False, "the quotation is empty"
    pos = 0
    for seg in segments:
        i = _find(seg, source, pos)
        if i < 0:
            return False, _explain(seg, source)
        pos = i + len(seg)
    return True, ""


def is_full_quote(quote, ref):
    q = norm_text(quote)
    source = norm_text(ref.text())
    return not ELLIPSIS.search(q) and (q == source or (q[:1].swapcase() + q[1:]) == source)


def _explain(segment, source):
    """Point at the first place the quotation departs from the verse text."""
    best_i, best_len = 0, -1
    for i in range(len(source)):
        n = 0
        while n < len(segment) and i + n < len(source) and source[i + n] == segment[n]:
            n += 1
        if n > best_len:
            best_i, best_len = i, n
    if best_len < 8:
        return f'not found in the verse text. The KJV reads: "{source}"'
    got = segment[best_len:best_len + 25]
    want = source[best_i + best_len:best_i + best_len + 25]
    return (f'departs from the KJV after "{segment[max(0, best_len - 30):best_len]}": '
            f'the quotation has "{got}", the KJV has "{want}". The KJV reads: "{source}"')


# ---------- near misses: Scripture words that aren't quite Scripture ----------

def words_of(s):
    return re.findall(r"[a-z0-9]+", norm_text(s).lower())


@functools.lru_cache(maxsize=None)
def word_index():
    """word -> set of verse keys, and word -> frequency, for finding candidate verses fast."""
    index, freq = {}, {}
    for key, text in kjv().items():
        for w in words_of(text):
            freq[w] = freq.get(w, 0) + 1
            index.setdefault(w, set()).add(key)
    return index, freq


@functools.lru_cache(maxsize=None)
def _normalized_bible():
    return " ".join(norm_text(t) for t in kjv().values())


def is_exact_somewhere(phrase):
    p = norm_text(phrase)
    bible = _normalized_bible()
    return p in bible or (p[:1].swapcase() + p[1:]) in bible


def near_miss(phrase, threshold=0.8):
    """If the phrase closely resembles KJV wording without matching it exactly, return
    (key, kjv_words, ratio) for the closest verse; else None."""
    import difflib
    if is_exact_somewhere(phrase):
        return None
    pw = words_of(phrase)
    if len(pw) < 5:
        return None   # four common words ('shall eat me up') resemble too many verses to call a misquote
    index, freq = word_index()
    known = sorted((w for w in set(pw) if w in freq), key=lambda w: freq[w])
    if not known:
        return None
    candidates = index[known[0]]
    if len(known) > 1:
        both = candidates & index[known[1]]
        candidates = both or candidates
    if len(candidates) > 400:
        return None   # only common words: too weak a signal to call it a misquote
    best = None
    for key in candidates:
        vw = words_of(kjv()[key])
        for size in (len(pw) - 1, len(pw), len(pw) + 1):
            for i in range(0, max(1, len(vw) - size + 1)):
                window = vw[i:i + size]
                ratio = difflib.SequenceMatcher(None, pw, window).ratio()
                if best is None or ratio > best[2]:
                    best = (key, " ".join(window), ratio)
    return best if best and best[2] >= threshold else None


# ---------- Greek and Hebrew ----------

@functools.lru_cache(maxsize=None)
def greek_index():
    """'John 1:1' -> list of word dicts (TR words only)."""
    out = {}
    with gzip.open(GREEK_TSV, "rt", encoding="utf-8") as f:
        cols = next(f).rstrip("\n").split("\t")
        for line in f:
            row = dict(zip(cols, line.rstrip("\n").split("\t")))
            out.setdefault(row["ref"], []).append(row)
    return out


@functools.lru_cache(maxsize=None)
def lexicon():
    """'G25' -> list of lexicon entries (a number can have several senses)."""
    out = {}
    with gzip.open(LEXICON_TSV, "rt", encoding="utf-8") as f:
        cols = next(f).rstrip("\n").split("\t")
        for line in f:
            row = dict(zip(cols, line.rstrip("\n").split("\t")))
            out.setdefault(strong_key(row["strong"]), []).append(row)
    return out


def strong_key(s):
    """G0025 -> G25; G3004G -> G3004 (STEPBible's sense letters are ignored)."""
    m = re.match(r"^([GH])0*(\d+)", s.strip().upper())
    return f"{m.group(1)}{m.group(2)}" if m else s.strip().upper()


@functools.lru_cache(maxsize=None)
def form_of():
    """STEP gives some forms their own numbers ('G6063 = a Form of G1492'); traditional
    Strong's files them under the parent number. Either number is accepted."""
    out = {}
    for key, entries in lexicon().items():
        for e in entries:
            if e.get("form_of"):
                out.setdefault(key, set()).add(strong_key(e["form_of"]))
    return out


def word_strongs(word):
    keys = {strong_key(s) for s in word["strongs"].split()}
    keys |= {strong_key(s) for s in word["alt"].split()}
    for k in list(keys):
        keys |= form_of().get(k, set())
    return keys


def translit_key(s):
    """Spelling conventions differ, the word doesn't: agapaō = agapao, kyrios = kurios,
    elenchō = elegchō, angelos = aggelos, hodos = odos, ha.yah = hayah."""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z]", "", s)
    s = s.replace("kh", "ch").replace("y", "u")                  # chi; upsilon
    s = s.replace("nch", "gch").replace("ng", "gg").replace("nk", "gk").replace("nx", "gx")  # nasal gamma
    s = re.sub(r"^h", "", s).replace("rh", "r")                  # rough breathing
    return s


def words_in(ref_str, strong=None):
    words = greek_index().get(ref_str, [])
    if strong:
        words = [w for w in words if strong_key(strong) in word_strongs(w)]
    return words


# Robinson-style morphology codes, as used by STEPBible's TAGNT.
_POS = {"N": "noun", "A": "adjective", "T": "article", "V": "verb", "P": "personal pronoun",
        "R": "relative pronoun", "C": "reciprocal pronoun", "D": "demonstrative pronoun",
        "K": "correlative pronoun", "I": "interrogative pronoun", "X": "indefinite pronoun",
        "Q": "correlative or interrogative pronoun", "F": "reflexive pronoun", "S": "possessive pronoun"}
_WORDS = {"ADV": "adverb", "CONJ": "conjunction", "COND": "conditional particle", "PRT": "particle",
          "PREP": "preposition", "INJ": "interjection", "ARAM": "Aramaic word", "HEB": "Hebrew word"}
_CASE = {"N": "nominative", "V": "vocative", "G": "genitive", "D": "dative", "A": "accusative"}
_NUM = {"S": "singular", "P": "plural"}
_GEN = {"M": "masculine", "F": "feminine", "N": "neuter"}
_TENSE = {"P": "present", "I": "imperfect", "F": "future", "2F": "second future", "A": "aorist",
          "2A": "second aorist", "R": "perfect", "2R": "second perfect", "L": "pluperfect",
          "2L": "second pluperfect", "X": "no stated tense"}
_VOICE = {"A": "active", "M": "middle", "P": "passive", "E": "middle or passive",
          "D": "middle deponent", "O": "passive deponent", "N": "middle or passive deponent",
          "Q": "impersonal active", "X": "no stated voice"}
_MOOD = {"I": "indicative", "S": "subjunctive", "O": "optative", "M": "imperative",
         "N": "infinitive", "P": "participle", "R": "imperative participle"}
# Suffixes whose meaning is certain. Anything else is shown as the raw code, never guessed.
_SUFFIX = {"N": "negative", "I": "interrogative", "C": "comparative", "S": "superlative",
           "P": "personal name", "L": "place name", "T": "title", "ATT": "Attic form",
           "HEB": "Hebrew word", "ARAM": "Aramaic word", "LI": "letter", "NUI": "indeclinable number",
           "PRI": "indeclinable name", "OI": "indeclinable"}
_WORD_SUFFIX = {"N": "negative", "I": "interrogative", "C": "comparative", "S": "superlative",
                "HEB": "Hebrew word", "ARAM": "Aramaic word"}


def _cng(code):
    if len(code) == 3 and code[0] in _CASE and code[1] in _NUM and code[2] in _GEN:
        return f"{_CASE[code[0]]} {_NUM[code[1]]} {_GEN[code[2]]}"
    return None


def expand_morph(code):
    """'V-PAI-2S' -> 'verb, present active indicative, second person singular'.
    Returns the code itself for anything it doesn't recognise, never a guess."""
    parts = code.split("-")
    head = parts[0]
    if head in _WORDS:
        extra = [_WORD_SUFFIX.get(p, f"({p})") for p in parts[1:]]
        return ", ".join([_WORDS[head]] + extra)
    if head not in _POS:
        return code
    out = [_POS[head]]
    rest = parts[1:]
    if head == "V" and rest:
        m = re.match(r"^(2?[PIFARLX])([AMPEDONQX])([ISOMNPR])$", rest[0])
        if not m:
            return code
        out.append(f"{_TENSE[m.group(1)]} {_VOICE[m.group(2)]} {_MOOD[m.group(3)]}")
        rest = rest[1:]
        if rest:
            pn = re.match(r"^([123])([SP])$", rest[0])
            cng = _cng(rest[0])
            if pn:
                out.append(f"{['first', 'second', 'third'][int(pn.group(1)) - 1]} person {_NUM[pn.group(2)]}")
            elif cng:
                out.append(cng)
            else:
                return code
            rest = rest[1:]
    elif rest:
        first = rest[0]
        pm = re.match(r"^([123])([NVGDA])([SP])([MFN]?)$", first)   # P-1NS, F-3ASM
        sm = re.match(r"^([123])([SP])([NVGDA])([SP])([MFN])$", first)  # S-1SNSM
        if pm:
            person = ["first", "second", "third"][int(pm.group(1)) - 1]
            desc = f"{person} person {_CASE[pm.group(2)]} {_NUM[pm.group(3)]}"
            if pm.group(4):
                desc += f" {_GEN[pm.group(4)]}"
            out.append(desc)
        elif sm:
            person = ["first", "second", "third"][int(sm.group(1)) - 1]
            out.append(f"{person} person, {_NUM[sm.group(2)]} possessor, "
                       f"{_CASE[sm.group(3)]} {_NUM[sm.group(4)]} {_GEN[sm.group(5)]}")
        elif _cng(first):
            out.append(_cng(first))
        elif first in _SUFFIX:
            out.append(_SUFFIX[first])
        else:
            return code
        rest = rest[1:]
    for p in rest:
        out.append(_SUFFIX.get(p, f"({p})"))
    return ", ".join(out)


# ---------- counting (the only allowed source of "N times" claims) ----------

def scope_keys(scope):
    """'John' (a book), 'John 3' (a chapter), 'NT', 'OT', or 'Bible' -> verse keys."""
    scope = scope.strip()
    keys = list(kjv())
    if scope in ("Bible", "KJV"):
        return keys
    if scope == "NT":
        return [k for k in keys if k[0] in NT_BOOKS]
    if scope == "OT":
        return [k for k in keys if k[0] not in NT_BOOKS]
    m = re.fullmatch(r"(.+?)(?:\s+(\d+))?", scope)
    book = canonical_book(m.group(1)) if m else None
    if not book:
        raise RefError(f"'{scope}' isn't a scope: use a book (John), a chapter (John 3), NT, OT, or Bible")
    if m.group(2):
        ch = int(m.group(2))
        if (book, ch) not in chapter_sizes():
            raise RefError(f"{book} has no chapter {ch}")
        return [k for k in keys if k[0] == book and k[1] == ch]
    return [k for k in keys if k[0] == book]


def english_pattern(query):
    """Whole words, case-insensitive; a trailing * matches any ending (believ* -> believe,
    believed, believeth, believing...). Spaces match any spacing."""
    q = query.strip().strip('"').strip()
    if not q:
        raise ValueError("empty query")
    parts = []
    for token in re.split(r"(\s+)", q):
        if token.isspace():
            parts.append(r"\s+")
        else:
            parts.append(re.escape(token).replace(r"\*", r"\w*"))
    body = "".join(parts)
    start = r"\b" if re.match(r"\w", q) else ""
    end = r"\b" if re.search(r"\w$", q) else ""
    return re.compile(start + body + end, re.IGNORECASE)


def count_english(query, scope):
    rx = english_pattern(query)
    hits = [(k, len(rx.findall(kjv()[k]))) for k in scope_keys(scope)]
    hits = [(k, n) for k, n in hits if n]
    return sum(n for _, n in hits), hits


def count_strong(strong, scope):
    key = strong_key(strong)
    wanted = {f"{b} {c}:{v}" for b, c, v in scope_keys(scope)}
    if not any(k[0] in NT_BOOKS for k in scope_keys(scope)):
        raise RefError("Greek counts need a New Testament scope (a NT book or chapter, or NT)")
    hits = []
    for ref, words in greek_index().items():
        if ref in wanted:
            n = sum(1 for w in words if key in word_strongs(w))
            if n:
                hits.append((ref, n))
    return sum(n for _, n in hits), hits


def count(query, scope):
    q = query.strip()
    if re.fullmatch(r"[GH]\d{1,4}[A-Za-z]?", q):
        if q.upper().startswith("H"):
            raise RefError("Hebrew counts aren't supported: the loop has no tagged Hebrew text")
        return count_strong(q, scope)
    return count_english(q, scope)
