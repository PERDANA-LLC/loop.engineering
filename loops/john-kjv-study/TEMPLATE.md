# TEMPLATE: one unit of the John KJV study

<!-- Layer: Prompt. The maker follows this file on every run; tools/check_study.py enforces the rules in part 1.
     It is protected: the loop stops with DANGER if it changes during a run. Only a person edits it, with a
     changelog line in LOOP-SPEC.md. -->

Each unit is one Markdown file: `study/john-NN.md`. Unit `00` is the book overview; units `01`–`21` are John's chapters. The shape follows **bs3 v3.1, the TONA Bible Study Flywheel** (Map → Christological Root → three tiers → connectors), so a unit serves personal study and group teaching at once. Loop changes to bs3 are marked ◆.

---

## Part 1 · The rules the checker enforces

A unit passes the checker only when every rule holds. The checker's report names the rule, the line, and what it expected.

1. **Scripture is exact KJV, copied, never recalled.** Get the text from `python3 tools/verse.py "John 3:16"`. Write every quotation in double quotation marks, **on one line**, followed at once by **one** reference in parentheses. Put your own punctuation after the parenthesis:
   - ✅ `Martha hears the claim: "I am the resurrection, and the life" (John 11:25).`
   - ❌ `"I am the resurrection and the life" (John 11:25)` — the KJV has a comma after "resurrection", so the quotation isn't exact.
   - A fragment is fine, and `...` marks a gap. Only the first letter may change case. No [brackets] inside a quotation, and no other translation.
2. **Double quotation marks are for Scripture only.** A term, a sermon title, or dialogue in an analogy takes single quotation marks or *italics*. Double-quoted text of three or more words without a reference fails. A short Scripture phrase may sit in single quotation marks inside a sentence ('mine hour is not yet come'), but it must still be the exact KJV wording: a single-quoted phrase of five or more words that is close to a verse without matching it fails as a near miss.
3. **Every reference must exist.** Use full book names (`Numbers 21:9`) or standard abbreviations with chapter and verse. A quotation found in several verses of one chapter may list them: `"Come and see" (John 1:39, 46)`.
   - ❌ `John 22:1` fails: John has 21 chapters.
   - A number right after a reference and a comma reads as another verse: write 'John 2:20, where forty and six years are named', not a numeral after the comma.
4. **Greek and Hebrew words are cited, and the citation is checked.** Look the word up first with `tools/greek.py` (the words of a verse) and `tools/lexicon.py` (a Strong's entry). Cite it as *transliteration* (Strong's number, a verse where it occurs):
   - `*anōthen* (G509, John 3:3)` means 'this Greek word is in the Textus Receptus of John 3:3', and the checker confirms it. Common spelling variants are accepted (*kyrios* or *kurios*, *elenchō* or *elegchō*); the number and the verse must be right.
   - Add the parsing code when you discuss the form: `*agapas* (G25, John 21:15, V-PAI-2S)`.
   - Hebrew: `*mishkan* (H4908)` or `*mishkan* (H4908, Exodus 25:9)`.
   - A Strong's number anywhere else fails. Greek or Hebrew script needs a citation on the same line.
5. **Counts come from the concordance.** A numeral before "times" is a claim about the text. Compute it with `python3 tools/concordance.py "believ*" John` and paste the line it prints into the counts block at the end of the file. The checker recounts every line. Story details are written in words ('Peter denied him three times').
6. **The maker never grades itself.** No self-audit section, no /10 scores, no claim that 'all verses are verified'. The checker and the judge grade; a person approves.
7. **Nothing left unfinished:** no `TODO`, `TBD`, `{{`, or `[insert`.
8. **Length:** a chapter unit has 4,500–12,000 words; the overview has 3,000–10,000. Length earns nothing with the judge. Depth does.
9. **Headings follow the skeleton below, in order.** Extra `####` headings inside a section are fine. No quotation marks in headings.

## Part 2 · How to write it (what the judge looks for)

- **Text first.** Observe what the passage says, then explain what it means in context, then connect it to the rest of John and Scripture. Every interpretive claim should be traceable to words in the passage.
- **Mark what is contested.** When Christians disagree (the water of John 3:5, the bread of John 6, the textual questions at John 5:4 and 7:53–8:11), say so and state each view fairly. At Tier 3, argue for the position most consistent with Reformed hermeneutics (bs3's lens), with reasons, and add the Pastoral Warning.
- **Sources honestly.** Name the author and the work (for example J. C. Ryle, *Expository Thoughts on the Gospels*) and summarize the view in your own words. Never quote a non-Scripture source, and never invent a page number. If you aren't sure a writer held a view, write '(verify)'.
- **Word studies without overreach.** No root fallacy, no 'the Greek literally means' unless the lexicon supports it, no claims about tense beyond what the grammar carries.
- **Tiers that really differ.** Tier 1 is readable by a ten-year-old. Tier 2 equips a small-group leader. Tier 3 is seminary level: deeper, not just longer.
- **John's own design.** Engage what this chapter contributes to John: signs, "I am" sayings, feasts, witnesses, the hour, glory, misunderstanding and irony, the narrator's comments, and John's purpose in John 20:31.

## Part 3 · The skeleton (chapter units 01–21)

```markdown
# John 3 · Ye Must Be Born Again (KJV)
> Unit john-03 · John 3:1–36 · loop john-kjv-study v1.0 · DRAFT for human doctrine review

## 🗂️ Passage Map
| Section/Verses | Theme | One-Line Summary |
|---|---|---|
| 3:1–15 | The new birth | ... |
| 3:16–21 | ... | ... |
| 3:22–36 | ... | ... |

## ✝️ Christological Root
### 🔎 What Jesus Said/Did
### 🔗 The Bridge
### 📊 The Progression Line
### ⚠️ What Gets Lost Without This Root

## 🟢 Tier 1 — Easy (The Foundation)
### 📌 Core Concept
### 📖 Key Verses
### 🪞 Analogy
### 💡 Tip
### 🔧 Hack
### 🔎 Personal Diagnostic
### 🙏 Prayer/Response
### ✅ Action Step

## 🟡 Tier 2 — Medium (The Builder)
### 📌 Deeper Dive
### 📜 Verse-by-Verse Walkthrough
#### John 3:1–3 · A Ruler Comes by Night
#### John 3:4–8 · Born of Water and of the Spirit
(... blocks until the last verse of the chapter ...)
### 📖 Key Verses
### 🔤 Original Language Insight
### ⚠️ Common Misconception
### 🚫 Common Errors Quick-Reference
### 💡 Tip
### 🔧 Hack
### 🎯 Teaching Angle
### ❓ Discussion Questions
### ✅ Action Step

## 🔴 Tier 3 — Expert (The Masterclass)
### 📌 Theological Framework
### 📖 Key Verses
### 📚 Scholarly Insight
### ⚔️ Debate Corner
### 🔤 Original Language Deep Dive
### 💡 Tip
### 🔧 Hack
### 🎯 Teaching Angle
### 🎤 Preaching Titles
### ✅ Action Step

## 🔗 Cross-Tier Connectors
### 🔗 Golden Thread
### 📊 Progress Map
### 🧩 Unlock Moments

## 🌀 Spiral
### 🔑 Follow-Up Topics
### ➡️ Next in John

<!-- counts
believ* | John 3 | 9
-->
```

The counts block holds one line per count you state (`query | scope | number`, exactly as `tools/concordance.py` prints it). Leave it out if you state no counts.

## Part 4 · What goes in each section

| Section | bs3 asks for | Checked by script ◆ |
|---|---|---|
| **Unit line** | `> Unit john-NN · John N:1–last · loop john-kjv-study v1.0 · DRAFT for human doctrine review` | present |
| 🗂️ **Passage Map** | Section-by-section table; one line each. Orients all three tiers. | rows start with `N:V–W`, cover the whole chapter |
| 🔎 **What Jesus Said/Did** | 1–2 Gospel passages where Jesus grounds this chapter's teaching, **quoted in full** | ≥ 1 whole-verse Gospel quotation |
| 🔗 **The Bridge** | 2–3 sentences: how what Jesus said or did becomes the root of the doctrine | — |
| 📊 **The Progression Line** | Text diagram: Jesus (Gospels) → Promise/Prophecy (OT) → Doctrine (Epistles) → Application | references valid |
| ⚠️ **What Gets Lost** | One sentence naming the error or imbalance of teaching this without Jesus | — |
| 📌 **Core Concept** (T1) | The chapter's heart, as if to a ten-year-old; one paragraph | — |
| 📖 **Key Verses** (T1) | 3–5 verses **quoted in full**, a one-sentence explanation each | 3–5 whole verses |
| 🪞 **Analogy** | One real-world picture that makes it click | — |
| 💡 **Tip** / 🔧 **Hack** (T1) | A "start here" habit; a memory trick (acronym, mnemonic, picture) | — |
| 🔎 **Personal Diagnostic** | 4–5 yes/no self-check questions, honest and non-condemning, as a list | 4–5 list items with `?` |
| 🙏 **Prayer/Response** | A short written prayer or response prompt | — |
| ✅ **Action Step** (T1) | One concrete thing to do this week | — |
| 📌 **Deeper Dive** (T2) | A vivid 1–2 sentence hook, then historical and cultural background and John's intent (2–3 paragraphs) | — |
| 📜 **Verse-by-Verse Walkthrough** ◆ | The expository spine. `#### John N:V–W · short title` blocks, **in order, covering every verse**, **no more than 6 verses each**. In each block: observe, explain, connect. Quote the block's own verses. | every verse once, in order, ≤ 6 per block, each block quotes its verses |
| 📖 **Key Verses** (T2) | 5–8 verses **quoted in full**, each with cross-references showing the thematic links. Give the cross-references as bare references or short fragments: every whole-verse quotation in a Key Verses section counts toward its limit. | 5–8 whole verses |
| 🔤 **Original Language Insight** | One Greek word study: transliteration, definition, use across Scripture | ≥ 1 checked Greek citation |
| ⚠️ **Common Misconception** | One myth, answered from Scripture | — |
| 🚫 **Common Errors Quick-Reference** | Table `Error · Definition · Corrective Verse`, 2–3 theological errors a teacher must be able to answer | 2–3 rows, last cell a valid reference |
| 💡 **Tip** / 🔧 **Hack** (T2) | A study method (S.O.A.P., inductive, COMA); a tool or resource for going deeper | — |
| 🎯 **Teaching Angle** (T2) | How to teach this chapter to a Tier 1 group: a simple outline | — |
| ❓ **Discussion Questions** | 3–5 searching questions, as a list | 3–5 list items with `?` |
| ✅ **Action Step** (T2) | A 7-day study plan or challenge | — |
| 📌 **Theological Framework** | Where the chapter sits in systematic theology (Christology, soteriology, pneumatology, eschatology…) | — |
| 📖 **Key Verses** (T3) | 8 or more verses **quoted in full**, with exegetical notes (context, grammar, theological weight) | ≥ 8 whole verses |
| 📚 **Scholarly Insight** | Commentators, church fathers, or scholars: author and work named, views summarized, never quoted | (judge) |
| ⚔️ **Debate Corner** | 2–3 positions on a contested point; which is most consistent with Reformed hermeneutics and why; a Pastoral Warning about the real effect on a church | (judge) |
| 🔤 **Original Language Deep Dive** | A full word study: parsing, cognates, semantic range, Septuagint use where it helps | ≥ 1 Greek citation **with a parsing code** |
| 💡 **Tip** / 🔧 **Hack** (T3) | A hermeneutical or homiletical technique; a sermon-prep or research workflow | — |
| 🎯 **Teaching Angle** (T3) | How to teach this to a Tier 2 group, plus answers to the 3 toughest questions | — |
| 🎤 **Preaching Titles** | 3 sermon or lesson titles for TONA, as a list (no double quotation marks) | exactly 3 list items |
| ✅ **Action Step** (T3) | A 30-day deep-study plan that ends in a real delivery: teach it, record it, get feedback | — |
| 🔗 **Golden Thread** | The one theme uniting the tiers, in one sentence | — |
| 📊 **Progress Map** | Root → Tier 1 → Tier 2 → Tier 3 with the key milestones | — |
| 🧩 **Unlock Moments** | The insight that lifts a learner from Root→T1, T1→T2, T2→T3 | — |
| 🔑 **Follow-Up Topics** ◆ | 3 topics that grow out of this chapter, as a list | exactly 3 list items |
| ➡️ **Next in John** ◆ | One paragraph bridging to the next chapter | — |

## Part 5 · The overview unit (00)

Unit 00 has the same sections with three changes:

- Title: `# The Gospel of John · Book Overview (KJV)`; unit line: `> Unit john-00 · John 1–21 · loop john-kjv-study v1.0 · DRAFT for human doctrine review`.
- 🗂️ **Passage Map** maps the whole book (Prologue, the Book of Signs, the Farewell, the Passion and Resurrection, the Epilogue), at least 2 rows.
- In Tier 2, **📚 Chapter-by-Chapter Breakdown** ◆ replaces the walkthrough: `#### John N · short title` for John 1 to John 21 in order, a paragraph each, each quoting at least one verse of its own chapter.

Everything else, including the verse counts per Key Verses section, is the same. The overview introduces authorship and date as the church has received them, marking tradition as tradition.

## Part 6 · What happened to bs3's Flywheel Engine ◆

| bs3 step | In this loop |
|---|---|
| A · Self-Audit (the maker scores itself /10) | **Replaced.** A maker grading itself is the first thing loop engineering removes. `tools/check_study.py` checks what a script can; a separate judge (`JUDGE.md`, `rubric.md`) scores the rest; a person approves the doctrine. |
| B · Rewrite the lowest-scoring section | **Automatic.** The checker's or the judge's first failing line becomes the next iteration's job. |
| C · Prompt Upgrade | **Proposals only.** The maker may add suggestions to `proposals/prompt-upgrades.md`; it never edits `PROMPT.md`, `TEMPLATE.md`, or `rubric.md`. A person decides. |
| D · Spiral | **In the unit** as 🌀 Spiral, and in the loop as `units.tsv`, which picks the next unit. |
| Iteration tracker | `progress.md` (decisions and attempts) and `loop-log.csv` (every iteration). |
