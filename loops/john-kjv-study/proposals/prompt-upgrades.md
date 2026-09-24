# Prompt upgrade proposals

KJV72's Spiral (bs3's Step C before it), made safe (EX-6.1 in the guide): the maker may add ideas here for improving `PROMPT.md`, `TEMPLATE.md`, `plan.md`, or `rubric.md`. It never edits those files itself. A person reads these, tries any change on a fixed set of units first, and records the decision in `LOOP-SPEC.md`'s changelog.

Format: `- <date> · john-NN · <file>: <the change, and why>`

- 2026-09-24 · john-02 · TEMPLATE.md: in Part 1 rule 3 or Part 4, say that a whole-verse quotation of a cross-reference inside a Key Verses section counts toward that section's whole-verse limit (the checker counts every full quote in the span), so cross-references there are best given as bare references or fragments. Also warn that a number after a reference and a comma is read as a follow-on verse ('John 2:20, 46 years' is checked as John 2:46 and fails). Both are easy to trip over and neither is stated.
  - **Decision (2026-09-24, the builder, before v1.0 shipped):** adopted both. TEMPLATE.md Part 4 now says whole-verse cross-references count toward a Key Verses limit; TEMPLATE.md rule 3 warns against a numeral after a reference and a comma; and the checker no longer reads a number followed by an ordinary word ('46 years') as a verse. See LOOP-SPEC.md, changelog v1.0 (SF-5).
