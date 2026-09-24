#!/usr/bin/env python3
"""Tests for the deterministic checker: it must pass exact work and catch every kind of slip.

  python3 tests/test_checker.py        (or: python3 -m unittest discover tests)

Two groups:
  * rule tests on small synthetic snippets (quotations, references, Greek, counts);
  * fixture tests: the good John 2 unit passes, and each known-bad mutation of it fails
    with the right code. These double as the known-good / known-bad sample for CALC-1.
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


def mutations(text):
    """Known-bad versions of a good unit, each with the code the checker must report."""
    out = []
    m = re.search(r'"([^"]*?),([^"]*)" \((John 2:\d+)\)', text)
    if m:
        out.append(("comma dropped from a quotation (the CS-2 slip)", "QUOTE-MISMATCH",
                    text.replace(m.group(0), f'"{m.group(1)}{m.group(2)}" ({m.group(3)})', 1)))
    blocks = list(re.finditer(r"^#### John 2:.*$", text, flags=re.M))
    if len(blocks) >= 3:
        a, b = blocks[1].start(), blocks[2].start()
        out.append(("a walkthrough block deleted", "COVERAGE-GAP", text[:a] + text[b:]))
    out.append(("a required subsection renamed", "STRUCTURE", re.sub(r"^### .*Personal Diagnostic.*$", "### Self-check",
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
    return out


@unittest.skipUnless(os.path.exists(GOOD), "needs tests/fixtures/john-02.good.md")
class Fixtures(unittest.TestCase):
    def setUp(self):
        self.text = open(GOOD, encoding="utf-8").read()

    def test_good_unit_passes(self):
        self.assertEqual(check_file("02", self.text), [])

    def test_every_known_bad_mutation_fails_with_its_code(self):
        bad = mutations(self.text)
        self.assertGreaterEqual(len(bad), 9)
        for name, code, text in bad:
            with self.subTest(name):
                self.assertIn(code, check_file("02", text))

    def test_flawed_fixture_is_not_yet(self):
        flawed = os.path.join(HERE, "fixtures", "john-02.flawed.md")
        self.assertIn("QUOTE-MISMATCH", check_file("02", open(flawed, encoding="utf-8").read()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
