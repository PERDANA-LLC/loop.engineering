#!/usr/bin/env python3
"""Tests for the deterministic checker: it must pass exact work and catch every kind of slip.

  python3 tests/test_checker.py        (or: python3 -m unittest discover tests)

Three groups:
  * rule tests on small synthetic snippets (quotations, references, Greek, counts);
  * format tests on two minimal units that keep every rule of the KJV72 x KJV82 format with
    brief prose (tests/fixtures/john-02.minimal.md and john-00.minimal.md): each passes every
    check but LENGTH, and each known-bad mutation of it fails with the right code;
  * fixture tests: the good John 2 unit that the loop itself wrote passes, and each known-bad
    mutation of it fails with the right code.
The format and fixture tests are also the known-good / known-bad sample for CALC-1.
"""
import os
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_study as cs  # noqa: E402
import kjvlib  # noqa: E402

GOOD = os.path.join(HERE, "fixtures", "john-02.good.md")
MINIMAL = os.path.join(HERE, "fixtures", "john-02.minimal.md")
MINIMAL_00 = os.path.join(HERE, "fixtures", "john-00.minimal.md")


def codes_for(text):
    """Run the quote, reference, Greek, and count checks on a snippet; return the codes found."""
    rep = cs.Report()
    body = cs.blank_comments(text)
    cs.check_quotes(body, rep)
    cs.check_single_quotes(body, rep)
    cs.check_refs(body, rep)
    cs.check_greek(body, [], {}, rep)
    cs.check_counts(text, body, rep)
    return sorted({code for _ln, code, _m in rep.items})


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_file(unit, text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    try:
        rep, _stats = cs.run(unit, path)
    finally:
        os.unlink(path)
    return sorted({code for _ln, code, _m in rep.items})


class Quotations(unittest.TestCase):
    def test_exact_quotation_passes(self):
        self.assertEqual(codes_for('He said: "Blessed are the poor in spirit: for theirs is the kingdom of heaven." (Matthew 5:3)'), [])

    def test_case_study_comma_error_fails(self):
        # CS-2's v1 slip: a comma where the KJV has a colon.
        self.assertEqual(codes_for('"Blessed are the poor in spirit, for theirs is the kingdom of heaven" (Matthew 5:3)'),
                         ["QUOTE-MISMATCH"])

    def test_fragment_ellipsis_and_first_letter(self):
        self.assertEqual(codes_for('"The Word was made flesh" (John 1:14) and "In the beginning ... the Word was God" (John 1:1)'), [])

    def test_word_changed_fails(self):
        self.assertEqual(codes_for('"For God so loved the world, that he gave his one and only Son" (John 3:16)'), ["QUOTE-MISMATCH"])

    def test_the_source_prompts_ephesians_slip_fails(self):
        # KJV72 and KJV82 both drop "unfruitful" from Ephesians 5:11.
        self.assertEqual(codes_for('"And have no fellowship with the works of darkness, but rather reprove them" (Ephesians 5:11)'),
                         ["QUOTE-MISMATCH"])

    def test_brackets_inside_a_quotation_fail(self):
        self.assertEqual(codes_for('"In the beginning was the Word [Christ]" (John 1:1)'), ["QUOTE-MISMATCH"])

    def test_unreferenced_quotation_fails_but_short_terms_pass(self):
        self.assertEqual(codes_for('Jesus said "I am the bread of life" to them.'), ["QUOTE-UNREFERENCED"])
        self.assertEqual(codes_for('The word "believe" matters, and so does "born again".'), [])

    def test_other_translation_fails(self):
        self.assertEqual(codes_for('"For God so loved the world" (John 3:16 ESV)'), ["QUOTE-VERSION"])

    def test_verse_list_needs_the_words_in_every_verse(self):
        self.assertEqual(codes_for('"Come and see" (John 1:39, 46)'), [])
        self.assertEqual(codes_for('"I am the true vine" (John 15:1, 5)'), ["QUOTE-MISMATCH"])

    def test_range_and_curly_quotes(self):
        self.assertEqual(codes_for('“For God so loved the world, that he gave his only begotten Son, that whosoever '
                                   'believeth in him should not perish, but have everlasting life. For God sent not his Son '
                                   'into the world to condemn the world” (John 3:16–17)'), [])

    def test_unbalanced_marks_fail(self):
        self.assertIn("QUOTE-UNBALANCED", codes_for('He said "In the beginning (John 1:1)'))


class NearMisses(unittest.TestCase):
    """SF-4: Scripture in single quotation marks must still be exact."""

    def test_near_misses_fail(self):
        for phrase in ("Mine hour is not come yet", "I am the resurrection and the life",
                       "the zeal of thy house hath eaten me up"):
            with self.subTest(phrase):
                self.assertEqual(codes_for(f"He said '{phrase}' to them."), ["SCRIPTURE-NEARMISS"])

    def test_exact_phrases_and_own_words_pass(self):
        self.assertEqual(codes_for("Jesus says 'mine hour is not yet come', and the 'good wine until now' is kept."), [])
        self.assertEqual(codes_for("Literally 'was not entrusting himself to them', and 'shall eat me up' in some editions."), [])
        self.assertEqual(codes_for("Two morals, 'Jesus enjoys a party' and 'churches should not sell things'."), [])


class References(unittest.TestCase):
    def test_references_that_do_not_exist_fail(self):
        self.assertEqual(codes_for("See John 22:1."), ["REF-INVALID"])
        self.assertEqual(codes_for("See John 3:37."), ["REF-INVALID"])
        self.assertEqual(codes_for("See Psalm 151."), ["REF-INVALID"])

    def test_real_references_and_lists_pass(self):
        self.assertEqual(codes_for("Compare John 1:1, 14; 3:16, Psalm 23, 1 Jn 4:8, and Rom. 8:28."), [])

    def test_numbered_book_after_a_list(self):
        self.assertEqual(codes_for("John 1:1, 2 Peter 1:21"), [])

    def test_a_number_that_is_not_a_verse(self):
        # SF-5, the maker's own proposal: "John 2:20, 46 years" is not John 2:46.
        self.assertEqual(codes_for("The Jews answer (John 2:20, 46 years in building)."), [])


class Greek(unittest.TestCase):
    def test_valid_citations(self):
        self.assertEqual(codes_for("*agapaō* (G25, John 21:15) and *agapas* (G25, John 21:15, V-PAI-2S)"), [])
        self.assertEqual(codes_for("*phileō* (G5368, John 21:17) and *mishkan* (H4908, Exodus 25:9)"), [])

    def test_spelling_conventions_are_accepted(self):
        self.assertEqual(codes_for("*kyrios* (G2962, John 20:28) and *elenchō* (G1651, John 16:8)"), [])

    def test_traditional_number_for_a_step_form(self):
        # STEP files οἶδα under G6063; traditional Strong's uses G1492. Both are accepted.
        self.assertEqual(codes_for("*oida* (G1492, John 21:15) and *oida* (G6063, John 21:15)"), [])

    def test_word_not_in_the_verse_fails(self):
        self.assertEqual(codes_for("*agapaō* (G25, John 21:17)"), ["GREEK-NOTINVERSE"])

    def test_wrong_number_for_the_word_fails(self):
        self.assertEqual(codes_for("*skotia* (G2842, John 1:5)"), ["GREEK-NOTINVERSE"])

    def test_wrong_transliteration_fails(self):
        self.assertEqual(codes_for("*logos* (G25, John 21:15)"), ["GREEK-TRANSLIT"])

    def test_wrong_parsing_fails(self):
        self.assertEqual(codes_for("*agapas* (G25, John 21:15, V-AAI-2S)"), ["GREEK-MORPH"])

    def test_loose_number_and_uncited_script_fail(self):
        self.assertEqual(codes_for("The word is G25 in Strong's."), ["STRONGS-LOOSE"])
        self.assertEqual(codes_for("The word is λόγος here."), ["GREEK-UNCITED"])
        self.assertEqual(codes_for("*logos* (G3056) without a verse"), ["GREEK-NOREF"])

    def test_a_label_like_g1_is_read_as_strongs(self):
        # Why the Gather items are labeled "Group question 1", not "G1": G1 is a Strong's number.
        self.assertEqual(codes_for("- **G1 · 10 min.** What surprised you?"), ["STRONGS-LOOSE"])

    def test_textus_receptus_reading_at_john_1_18(self):
        self.assertEqual(codes_for("*huios* (G5207, John 1:18)"), [])


class Counts(unittest.TestCase):
    def test_backed_count_passes(self):
        self.assertEqual(codes_for("Believe appears 9 times.\n<!-- counts\nbeliev* | John 3 | 9\n-->"), [])

    def test_wrong_count_fails(self):
        self.assertEqual(codes_for("It appears 98 times.\n<!-- counts\nbeliev* | John | 98\n-->"),
                         ["COUNT-UNBACKED", "COUNT-WRONG"])

    def test_unbacked_count_fails_but_words_pass(self):
        self.assertEqual(codes_for("Verily is said 25 times."), ["COUNT-UNBACKED"])
        self.assertEqual(codes_for("Peter denied him three times."), [])


class NotYetByDefault(unittest.TestCase):
    """BP-2.2: feed the checker an empty file or garbage; it must say NOT YET."""

    def test_empty_file(self):
        self.assertEqual(check_file("02", ""), ["EMPTY"])

    def test_garbage(self):
        codes = check_file("02", "lorem ipsum — not a study at all\n" * 40)
        self.assertIn("TITLE", codes)
        self.assertIn("STRUCTURE", codes)

    def test_the_old_bs3_format_fails(self):
        codes = check_file("02", "# John 2 · The First Sign (KJV)\n> Unit john-02 · John 2:1–25\n\n"
                                 "## 🗂️ Passage Map\n## ✝️ Christological Root\n## 🟢 Tier 1 — Easy (The Foundation)\n")
        self.assertIn("STRUCTURE", codes)


def sub(text, old, new, count=1):
    """Replace old with new; the mutation must actually change the text."""
    assert old in text, f"mutation target not found: {old[:60]!r}"
    return text.replace(old, new, count)


def chapter_mutations(t):
    """Known-bad versions of the minimal John 2 unit, each with the code the checker must report."""
    v7 = kjvlib.kjv()[("John", 2, 7)]
    return [
        ("a verse left out of Read & Mark", "TEXT-MISSING", sub(t, f"**7** {v7}\n", "")),
        ("a word changed in the printed chapter", "TEXT-MISMATCH", sub(t, f"**7** {v7}", f"**7** {v7.replace('brim', 'top')}")),
        ("a question without write-in lines", "WRITE-IN", sub(t, "**Q1.** Who was at the marriage in Cana (John 2:1)?\n\n__________\n__________",
                                                              "**Q1.** Who was at the marriage in Cana (John 2:1)?")),
        ("a question numbered out of order", "QUESTIONS", sub(t, "**Q9.** Which view", "**Q10.** Which view")),
        ("an Observe question without its verse", "QUESTIONS", sub(t, "**Q1.** Who was at the marriage in Cana (John 2:1)?",
                                                                     "**Q1.** Who was at the marriage in Cana?")),
        ("a question with no answer in the key", "ANSWER-KEY", sub(t, "**Q22.** Model answer: a confused friend (Psalm 119:105).\n", "")),
        ("an answer with no verse", "ANSWER-KEY", sub(t, "**Q9.** Either can be held; the text stresses meaning (John 2:13).",
                                                      "**Q9.** Either can be held; the text stresses meaning.")),
        ("a foundation label missing", "LABELS", sub(t, "**The Theft:** ", "")),
        ("a View B without its proof text", "LABELS", sub(t, "early and late (Mark 11:15).", "early and late.")),
        ("a practice with no verse", "PRACTICES", sub(t, "tell them what Jesus did for you (John 10:10).", "tell them what Jesus did for you.")),
        ("Life Practices with no Outward practice", "PRACTICES", sub(sub(t, "- **Outward:** Call one", "- **Inward:** Call one"),
                                                                     "- **Outward:** Share a meal", "- **Inward:** Share a meal")),
        ("the Abundance Guard not printed", "FIXED-LINE", sub(t, "*Abundant life is fullness of life in Christ — not money, not ease, not freedom from suffering.*\n", "")),
        ("the Life commitment line broken", "FIXED-LINE", sub(t, "I will bring life to __________ by __________ before __________ (day).",
                                                              "I will bring life to someone soon.")),
        ("the Light Planner without the participant's own heart first", "PLANNER", sub(t, "| My own heart: __________ |", "| __________ |")),
        ("a Session Plan that doesn't add up to 75", "SESSION-PLAN", sub(t, "| Open and warm-up | 5 |", "| Open and warm-up | 10 |")),
        ("a flagged word missing from the Glossary", "GLOSSARY", sub(t, "| whence | John 2:9 | from where |\n", "")),
        ("a flagged word that isn't in its verse", "GLOSSARY", sub(t, "| firkins | John 2:6 | __________ |", "| firkins | John 2:5 | __________ |")),
        ("a Word Study citation for another verse", "WORD-STUDY", sub(t, "| glory | John 2:11 | *doxa* (G1391, John 2:11) |",
                                                                    "| glory | John 2:11 | *doxa* (G1391, John 1:14) |")),
        ("a walkthrough block without Asks", "LAYERS", sub(t, "**Asks:** Trust the word of Jesus and look for his glory.", "")),
        ("a doctrine block missing a part", "LABELS", sub(t, "**Errors Refuted:** ", "")),
        ("a doctrine with one quoted cross-reference", "DOCTRINE-XREF", sub(t, f'**Cross-References:** {cs_quote("Malachi 3:1")}; ',
                                                                            "**Cross-References:** Malachi 3:1; ")),
        ("a category skipped", "DOCTRINE-CATEGORY", sub(t, "- **Pneumatology:** The chapter assumes the Spirit who later brings the disciples' memory to life (John 14:26).\n", "")),
        ("doctrine blocks out of order", "DOCTRINE-ORDER", sub(t, "### Eschatology · The Temple Raised", "### Christology · The Temple Raised")),
        ("a scholar who never speaks", "COUNCIL", sub(t, "**Historian:** Mothers were honored", "Mothers were honored")),
        ("only three group questions", "LIST-COUNT", sub(t, "- **Group question 3 · 10 min.** What does it mean that Jesus knows what is in man?\n", "")),
        ("no doing objective", "LIST-COUNT", sub(t, "- **Doing:** Name one place", "- Name one place")),
        ("a preaching mistake left out", "LIST-COUNT", sub(t, "- **Heat without light:**", "- **Heat alone:**")),
        ("Every Answer in Jesus without Colossians 2:3", "LABELS", sub(t, "In him are hid all the treasures of wisdom and knowledge (Colossians 2:3).",
                                                                      "In him are hid all the treasures of wisdom and knowledge.")),
        ("two memory verses", "MEMORY-VERSE", sub(t, "**Why this verse:**", f"{cs_quote('John 2:5')}\n\n**Why this verse:**")),
        ("a PASS/FIX self-check", "SELF-GRADE", t + "\n| V1 exact quotations | PASS |\n"),
        ("a skeleton line left as it was", "PLACEHOLDER", sub(t, "**The Lamp:** Scripture remembered, as the disciples remembered it (John 2:22).",
                                                             "**The Lamp:** ...")),
        ("a Life & Light At-a-Glance table without its Light row", "AT-A-GLANCE",
         sub(t, "| **Light** | Faith that is only for show | Jesus, the light of the world (John 8:12) | Ask him to search my motives |\n", "")),
        ("a proposition list that doesn't match the doctrine blocks", "LIST-COUNT",
         sub(t, "- **Eschatology:** The Temple Raised in Three Days (John 2:19)\n", "")),
        ("a whole subsection removed", "STRUCTURE", sub(t, "### 🏙️ Modern Example\n", "")),
    ]


def cs_quote(ref):
    return f'"{kjvlib.parse_ref(ref).text()}" ({ref})'


def overview_mutations(t):
    return [
        ("a Lesson Map with 20 rows", "BLUEPRINT", re.sub(r"^\| 21 \|.*\n", "", t, count=1, flags=re.M)),
        ("a memory verse from the wrong chapter", "BLUEPRINT", sub(t, "| John 3:16 | new birth", "| John 4:16 | new birth")),
        ("a Ledger without John 15:5", "LEDGER", sub(t, '"for without me ye can do nothing" (John 15:5)', "for without me ye can do nothing")),
        ("a Ledger with 20 rows", "LEDGER", re.sub(r"^\| 21 \| _+.*\n", "", t, count=1, flags=re.M)),
        ("five FAQ questions", "LIST-COUNT", sub(t, "- **What if someone has no one to name?** Start with the household.\n", "")),
        ("seven teacher hacks", "LIST-COUNT", sub(t, "- Silent processing: wait seven to ten seconds.\n", "")),
        ("the breakdown skips a chapter", "COVERAGE-GAP", re.sub(r"#### John 12 · .*\n.*\n", "", t, count=1)),
        ("two course outcomes", "LIST-COUNT", sub(t, "- Trace the signs and the sayings of Jesus through the book.\n", "")),
    ]


@unittest.skipUnless(os.path.exists(MINIMAL) and os.path.exists(MINIMAL_00), "needs the minimal fixtures")
class Format(unittest.TestCase):
    """The KJV72 x KJV82 format on two minimal units: every rule kept, prose kept short."""

    def test_minimal_units_pass_all_but_length(self):
        self.assertEqual(check_file("02", read(MINIMAL)), ["LENGTH"])
        self.assertEqual(check_file("00", read(MINIMAL_00)), ["LENGTH"])

    def test_every_chapter_mutation_fails_with_its_code(self):
        text = read(MINIMAL)
        bad = chapter_mutations(text)
        self.assertGreaterEqual(len(bad), 30)
        for name, code, mutated in bad:
            with self.subTest(name):
                self.assertNotEqual(mutated, text)
                self.assertIn(code, check_file("02", mutated))

    def test_every_overview_mutation_fails_with_its_code(self):
        text = read(MINIMAL_00)
        for name, code, mutated in overview_mutations(text):
            with self.subTest(name):
                self.assertNotEqual(mutated, text)
                self.assertIn(code, check_file("00", mutated))


def fixture_mutations(text):
    """Known-bad versions of the real good unit, each with the code the checker must report."""
    out = []
    m = re.search(r'"([^"]*?),([^"]*)" \((John 2:\d+)\)', text)
    if m:
        out.append(("comma dropped from a quotation (the CS-2 slip)", "QUOTE-MISMATCH",
                    text.replace(m.group(0), f'"{m.group(1)}{m.group(2)}" ({m.group(3)})', 1)))
    blocks = list(re.finditer(r"^#### John 2:\d+(?:\s*[-–]\s*\d+)?\s*[·:—–-].*$", text, flags=re.M))
    walk = [b for b in blocks if b.start() > text.find("### 📜 Walkthrough")]
    if len(walk) >= 3:
        a, b = walk[1].start(), walk[2].start()
        out.append(("a walkthrough block deleted", "COVERAGE-GAP", text[:a] + text[b:]))
    out.append(("a required subsection renamed", "STRUCTURE", re.sub(r"^### .*Diagnostic Check.*$", "### Self-check",
                                                                      text, count=1, flags=re.M)))
    out.append(("the maker claims its own success", "SELF-CLAIM", text + "\nAll verses have been verified against the KJV.\n"))
    out.append(("a Strong's number outside a citation", "STRONGS-LOOSE", text + "\nThe verb is G4100 in Strong's.\n"))
    out.append(("a count with no concordance line", "COUNT-UNBACKED", text + "\nJohn uses the word 98 times.\n"))
    out.append(("a reference to a verse that doesn't exist", "REF-INVALID", text + "\nCompare John 2:26.\n"))
    out.append(("an unreferenced quotation", "QUOTE-UNREFERENCED", text + '\nHe said "do whatever he tells you" to them.\n'))
    out.append(("a Greek word cited for the wrong verse", "GREEK-NOTINVERSE", text + "\nSee *agapaō* (G25, John 2:1).\n"))
    out.append(("a self-audit table", "SELF-GRADE", text + "\n| Biblical Accuracy | 9/10 |\n"))
    out.append(("a single-quoted near miss of John 2:4", "SCRIPTURE-NEARMISS",
                text + "\nJesus answers, 'mine hour is not come yet', and waits.\n"))
    v = kjvlib.kjv()[("John", 2, 9)]
    if f"**9** {v}" in text:
        out.append(("a verse of the printed chapter changed", "TEXT-MISMATCH",
                    text.replace(f"**9** {v}", f"**9** {v.replace('governor', 'ruler')}", 1)))
    return out


@unittest.skipUnless(os.path.exists(GOOD), "needs tests/fixtures/john-02.good.md")
class Fixtures(unittest.TestCase):
    def setUp(self):
        self.text = read(GOOD)

    def test_good_unit_passes(self):
        self.assertEqual(check_file("02", self.text), [])

    def test_every_known_bad_mutation_fails_with_its_code(self):
        bad = fixture_mutations(self.text)
        self.assertGreaterEqual(len(bad), 11)
        for name, code, text in bad:
            with self.subTest(name):
                self.assertIn(code, check_file("02", text))

    def test_flawed_fixture_is_not_yet(self):
        flawed = os.path.join(HERE, "fixtures", "john-02.flawed.md")
        self.assertIn("QUOTE-MISMATCH", check_file("02", read(flawed)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
