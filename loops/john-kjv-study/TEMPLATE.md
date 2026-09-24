# TEMPLATE: one unit of the John KJV study

<!-- Layer: Prompt. The maker follows this file on every run; tools/check_study.py enforces the rules in part 1
     and the "checked" column of parts 4 and 5. It is protected: the loop stops with DANGER if it changes during
     a run. Only a person edits it, with a changelog line in LOOP-SPEC.md. -->

Each unit is one Markdown file: `study/john-NN.md`. Unit `00` is the book overview and the workbook's front matter; units `01` to `21` are John's chapters, one lesson each.

The format combines two of the owner's prompts into one:

- **KJV72**: *KJV2211 v7.2, The Berean Council Flywheel* (`prompt/1.prompt.kjv.72.md` in the owner's `kjv.prompt` repository). A seven-scholar council writes one in-depth study in ten components: the foundations, four tiers of exposition, a systematic doctrine section, application, and the Life (John 10:10) and Light (John 8:12) pathways.
- **KJV82**: *KJV2222 v8.2, The Berean Council Workbook Builder* (`prompt/1.prompt.kjv.82.md`). The same council builds a workbook: a 19-point lesson for participants, climbing a five-level question ladder with write-in lines and two planners, and a Leader's Guide with the answers.

**How they fit together.** Each chapter unit is one workbook lesson (KJV82's participant pages), backed by KJV72's full study for the leader, and closed by KJV82's Leader's Guide for that lesson. Where the two prompts ask for the same thing (the Scripture text, the setting, the doctrine, the practices, the memory verse, the timing), the unit has it **once**, in the place that serves both. In Part 4, a **From** column names the source of every section: `72` for KJV72 (C = a component of its Step 5, GR = a ground rule, S = a step), `82` for KJV82 (P = a point of its 19-point lesson, BM = its back matter, S = a step), and ◆ for the loop's own additions.

---

## Part 1 · The rules the checker enforces

A unit passes the checker only when every rule holds. The checker's report names the rule, the line, and what it expected.

1. **Scripture is exact KJV, copied, never recalled.** Get the text from `python3 tools/verse.py "John 3:16"`. Write every quotation in double quotation marks, **on one line**, followed at once by **one** reference in parentheses. Put your own punctuation after the parenthesis:
   - ✅ `Martha hears the claim: "I am the resurrection, and the life" (John 11:25).`
   - ❌ `"I am the resurrection and the life" (John 11:25)` — the KJV has a comma after "resurrection", so the quotation isn't exact.
   - A fragment is fine, and `...` marks a gap. Only the first letter may change case. No [brackets] inside a quotation, and no other translation.
   - ❌ `"And have no fellowship with the works of darkness, but rather reprove them" (Ephesians 5:11)` fails: the KJV reads "the unfruitful works of darkness". (Both source prompts quote it this way; the loop quotes the KJV.)
2. **Double quotation marks are for Scripture only.** A term, a sermon title, or words in an example take single quotation marks or *italics*. Double-quoted text of three or more words without a reference fails. A short Scripture phrase may sit in single quotation marks inside a sentence ('mine hour is not yet come'), but it must still be the exact KJV wording: a single-quoted phrase of five or more words that is close to a verse without matching it fails as a near miss. Never quote a creed, confession, hymn, commentator, or sermon: name the work and summarize it.
3. **Every reference must exist.** Use full book names (`Numbers 21:9`) or standard abbreviations with chapter and verse. A quotation found in several verses of one chapter may list them: `"Come and see" (John 1:39, 46)`.
   - ❌ `John 22:1` fails: John has 21 chapters.
   - A number right after a reference and a comma reads as another verse: write 'John 2:20, where forty and six years are named', not a numeral after the comma.
4. **Greek and Hebrew words are cited, and the citation is checked.** Look the word up first with `tools/greek.py` (the words of a verse) and `tools/lexicon.py` (a Strong's entry). Cite it as *transliteration* (Strong's number, a verse where it occurs):
   - `*anōthen* (G509, John 3:3)` means 'this Greek word is in the Textus Receptus of John 3:3', and the checker confirms it. Common spelling variants are accepted (*kyrios* or *kurios*, *elenchō* or *elegchō*); the number and the verse must be right.
   - Add the parsing code when you discuss the form: `*agapas* (G25, John 21:15, V-PAI-2S)`.
   - Hebrew: `*mishkan* (H4908)` or `*mishkan* (H4908, Exodus 25:9)`.
   - A Strong's number anywhere else fails. Greek or Hebrew script needs a citation on the same line. The tools make every number certain, so the prompts' "(verify)" escape is not used for Strong's numbers.
5. **Counts come from the concordance.** A numeral before "times" is a claim about the text. Compute it with `python3 tools/concordance.py "believ*" John` and paste the line it prints into the counts block at the end of the file. The checker recounts every line. Story details are written in words ('Peter denied him three times').
6. **The maker never grades itself.** No self-audit, no /10 scores, no PASS/FIX list, no claim that 'all verses are verified'. The prompts' own checks (KJV72's V1–V14 and self-audit, KJV82's V1–V18 and conformity check) are the checker's and the judge's job here (Part 6).
7. **Nothing left unfinished:** no `TODO`, `TBD`, `{{`, or `[insert`. A write-in line is not a placeholder: it is a line holding only underscores, at least ten (`__________`), and blanks inside a sentence or a table cell are written the same way.
8. **Length:** a chapter unit has 8,000–20,000 words; the overview has 8,000–18,000. Length earns nothing with the judge. Depth does.
9. **Headings follow the skeleton, in order,** at the levels shown. You may add a `####` heading inside a section, except inside the Walkthrough and the Chapter-by-Chapter Breakdown, where every `####` is a block. No quotation marks in headings.
10. **The whole chapter is printed, exactly.** Read & Mark prints every verse of the chapter, in order, each as its own paragraph in the form `**N** text`. `python3 tools/verse.py "John 2" --read-mark` prints it ready to paste. The checker compares every verse with the KJV file.
11. **Labels are bold, at the start of a line,** spelled as the skeleton shows (`**The Theft:**`, `**Says:**`, `**View A:**`). The checker finds the parts of a section by their labels.
12. **Questions are numbered and answered.** Every participant question starts a line with `**Qn.**`, numbered Q1, Q2, … through the lesson with no gaps, and is followed by at least two write-in lines. The Leader's Guide answers every one under the same number, and each answer cites at least one verse.
13. **Practices are traced to Christ with a verse** (KJV72's source discipline). Every practice is a list item that includes a reference. Each set has at least 3 practices. Life and Light practices begin with `**Inward:**` or `**Outward:**`, and each set has at least one of each.
14. **Some lines are fixed.** The two commitment lines, the two guards, and the Light Planner's first row read as the skeleton shows (the blanks are yours to size).
15. **Tables have the shapes in Part 4.** Among them: the Session Plan's minutes add up to 75; every word in Mind the Language is also in the Glossary; every Mind the Language, Word Study, and Glossary word appears in the verse its row names.

## Part 2 · How to write it (what the judge looks for)

- **Work as the Berean Council.** Before writing, think through the chapter as KJV72's seven scholars would: the Philologist (the Greek beneath the KJV, archaic words, thee and thou against ye and you), the Historian, the Literary Scholar (structure, hinge words, contrasts of life and death, light and darkness), the Theologian (the doctrines, Scripture interpreting Scripture, Christ the source of life and light), the Church Historian, the Pastor (sin exposed, grace offered, the warfare, the pathways), and the Teacher, whom KJV82 calls the Curriculum Architect (objectives, the question ladder, teaching angles). Their briefs stay in your head; their findings go into the sections, and their debate goes into the Council's Hard Questions.
- **Text first, and three layers kept apart** (72 GR3). What the text SAYS, what it MEANS, and what it ASKS of us stay visibly separate: in every Walkthrough block, and in the ladder (Observe, then Interpret, then Apply).
- **Gloss every archaic word** a modern reader could misread (72 GR5): in the Glossary, and at its first use in the Walkthrough. The KJV's italic words (supplied by the translators) are not marked in `kjv/kjv.tsv`, so make no claims about italics.
- **Fair views** (72 GR4, 82 V9). Where faithful readers disagree (the water of John 3:5, the bread of John 6, one cleansing of the temple or two, the textual questions at John 5:4 and 7:53–8:11), say so, state each view at its strongest, and say why they differ: in a View A / View B panel for participants, and in the Debate Corner, where Tier 3 argues for the position most consistent with Reformed hermeneutics and adds a Pastoral Warning.
- **Never invent** (72 GR2, 82 Gotchas). Name the author and the work (for example J. C. Ryle, *Expository Thoughts on the Gospels*) and summarize the view in your own words. Never quote a non-Scripture source, never invent a page number, and write '(verify)' beside any attribution you aren't sure of. No root fallacy, and no 'the Greek literally means' unless the lexicon supports it.
- **Humility and Christ's glory** (72 GR7). Show how this chapter humbles the believer and makes Christ more glorious. Every problem the chapter exposes finds its answer in Jesus, and every truth in it is found in him, "In whom are hid all the treasures of wisdom and knowledge" (Colossians 2:3).
- **Life** (72 GR8, 82). "I am come that they might have life, and that they might have it more abundantly" (John 10:10). Name the Theft in this chapter's own terms, not in generalities; show the Source (Christ, with the verse, and the means he uses); show the Channel (how that life passes through a believer to another). The Abundance Guard is printed in every lesson: abundant life is fullness of life in Christ, not prosperity, ease, or freedom from suffering.
- **Light** (72 GR9, 82). "I am the light of the world: he that followeth me shall not walk in darkness, but shall have the light of life" (John 8:12). Name the Darkness this chapter addresses; show the Source ("For God, who commanded the light to shine out of darkness, hath shined in our hearts" (2 Corinthians 4:6)); show the Lamp (Scripture opened, truth told, hidden sin confessed, a reproof of "the unfruitful works of darkness" (Ephesians 5:11), good works that glorify the Father (Matthew 5:16)). The Love Guard is printed in every lesson: light without love is glare.
- **Source discipline** (72 GR10, 82). The believer is a channel and a reflector, never the origin of life or light: "for without me ye can do nothing" (John 15:5). No practice may work by the believer's own energy, sincerity, or technique. Humility is the posture in which both life and light are received.
- **Practices you can do today.** Each is concrete and doable within one day. An Outward Life practice names the kind of person to reach and leaves a blank for the name.
- **Doctrine in great detail** (72 GR11 and C6, 82 P13). Each doctrine the chapter teaches, implies, defends, or assumes gets a precise proposition, the words of the chapter that establish it, Scripture interpreting Scripture, the errors it refutes (stated as their holders would recognize them), and its fruit in humility, worship, and holiness. Don't force a category onto a chapter that doesn't teach it: list it under Assumed Here, with where Scripture teaches it plainly.
- **Tiers that differ, and a ladder that climbs.** Tier 1 is readable by a ten-year-old. Tier 2 equips a small-group leader. Tier 3 works at seminary level: deeper, not just longer. Tier 4 turns everything toward Christ and practice. On the participant pages, questions climb from Observe to Life & Light; they are open and searching, and none can be answered yes or no.
- **Participant pages are question-dominant** (82 V7). Exposition and answers belong in the Study and the Leader's Guide, not on the pages a participant writes in.
- **Tone:** reverent, precise, warm: scholarship in service of devotion (72 GR6).
- **John's own design.** Engage what this chapter contributes to John: signs, "I am" sayings, feasts, witnesses, the hour, glory, misunderstanding and irony, the narrator's comments, and John's purpose in John 20:31.
- **The session is 75 minutes** for the TONA small group, adults of mixed Bible familiarity, with a balanced emphasis (the prompts' defaults; `plan.md` D7).

## Part 3 · The skeleton (chapter units 01–21)

Copy this shape. Replace every `...` with your content; keep the headings, labels, fixed lines, and table headers.

```markdown
# John 2 · The First Sign and the Cleansed Temple (KJV)
> Unit john-02 · John 2:1–25 · loop john-kjv-study v2.0 · DRAFT for human doctrine review

## 🧭 At a Glance
### 🧵 Golden Thread
...
### 🌗 Life & Light Line
...
### 🎯 Objectives
- ...
- **Doing:** ...
### 📋 Life & Light At-a-Glance
| | What is dead or dark | Where the source is, with verse | What I do about it today |
|---|---|---|---|
| **Life** | ... | ... (John 10:10) | ... |
| **Light** | ... | ... (John 8:12) | ... |
### 🗂️ Passage Map
| Section | Verses | Theme | One-Line Summary |
|---|---|---|---|
| ... | 2:1–11 | ... | ... |
| ... | 2:12–25 | ... | ... |

## 🏛️ Core Foundations
### ✝️ Christological Root
**Gospel Foundation:** ...
**The Bridge:** ...
**Canonical Echoes:** Jesus (John 2:19) → Promise (...) → Doctrine (...) → Life (...)
**What Gets Lost:** ...
### ⚔️ Spiritual Warfare
**The Lie:** ...
**The Truth:** ...
**The Battleground:** ...
**The Weapon:** ...
### 🌱 Life Pathway
**The Theft:** ...
**The Source:** ...
**The Channel:** ...
**The Abundance Guard:** ...
### 💡 Light Pathway
**The Darkness:** ...
**The Source:** ...
**The Lamp:** ...
**The Love Guard:** ...

## 📖 The Lesson · Participant Pages
### 🙏 Open
**Prayer focus:** ...
**Warm-up:** ...?

__________
__________
### 🏺 Setting the Scene
...
### 🖍️ Read & Mark
**Marking key:** circle repeated words · underline commands · box names of God · double-underline promises
#### John 2:1–11 · ...
**1** And the third day there was a marriage in Cana of Galilee; and the mother of Jesus was there:

**2** ...
#### John 2:12–25 · ...
**12** ...
### 👁️ Observe · Level 1 (Easy)
**Q1.** ... (John 2:1)?

__________
__________
### 🔤 Mind the Language
| KJV word | Verse | What it means today (write it, then check the Glossary) |
|---|---|---|
| firkins | John 2:6 | __________ |
### 🔍 Word Study
| KJV word | Verse | Original word | Sense | Your lookup: another verse, and what it adds |
|---|---|---|---|---|
| miracles | John 2:11 | *sēmeion* (G4592, John 2:11) | ... | __________ |
### 🔗 Search the Scriptures
- ... (Psalm 69:9) · ...
**Q7.** What do these passages teach together?

__________
__________
### 🧩 Interpret · Level 2 (Medium)
**Q8.** ...?

__________
__________
**View A:** ... (proof text)
**View B:** ... (proof text)
**Q11.** Which view does the text best support, and why?

__________
__________
### 👣 Case Study · Scripture in Action
...
**Q12.** ...?

__________
__________
### 🏙️ Modern Example
...
### 📜 Voices from Church History
...
### ⛪ Doctrine in My Own Words
- **Christology:** ... (John 2:11)
State each core doctrine in your own words, and how it anchors your faith:

__________
__________
### ✋ Apply · Level 3 (Difficult)
**Head (believe)**
**Q15.** ...?
...
**Heart (love)**
...
**Hands (do)**
...
I will __________ by __________ (day).
### 👑 Christocentric & Humility · Level 4
...
**Humility Practices**
- ... (verse)
**Q19.** ...?
...
### 🌱 Bring Life · Level 5a
**Q20.** ...?
...
**Life Planner**
| Who around me is dead, dying, or deadened? (name) | What has the thief stolen there? | What does Christ give instead (verse) | What I will do about it this week | Done? |
|---|---|---|---|---|
| __________ | __________ | __________ | __________ | ____ |
**Life Practices**
- **Inward:** ... (verse)
- **Outward:** ... (verse)
**A Line to Say:** ...
I will bring life to __________ by __________ before __________ (day).
*Abundant life is fullness of life in Christ — not money, not ease, not freedom from suffering.*
### 💡 Bring Light · Level 5b
**Q24.** ...?
...
**Light Planner**
| Where is it dark? (mine first, then around me) | What is hidden there? | What light does Christ shine (verse) | How I carry it there this week, in love, not accusation | Done? |
|---|---|---|---|---|
| My own heart: __________ | __________ | __________ | __________ | ____ |
| __________ | __________ | __________ | __________ | ____ |
**Light Practices**
- **Inward:** ... (verse)
- **Outward:** ... (verse)
I will carry light into __________ by __________ before __________ (day).
*Light exposes, but light without love is glare; reproof is never license for contempt or public shaming.*
### 💎 Memory Verse
"This beginning of miracles did Jesus in Cana of Galilee, and manifested forth his glory; and his disciples believed on him." (John 2:11)
**Why this verse:** ...

__________
__________
### 🤝 Gather
- **Group question 1 · 10 min.** ...? *Cue:* ...
- **Group question 2 · 10 min.** ...
- **Group question 3 · 10 min.** ...
- **Group question 4 · 10 min · Naming round.** ...
### 🌀 Closing & Going Deeper
**Closing prayer focus:** ...
**For the week ahead:** ...
**Next in John:** ...

## 🟢 Tier 1 — Easy
### 📌 Core Concept
### 📖 Key Verses
### 🪞 Analogy
### 🔎 Diagnostic Check
### ✅ Action Step
### 🌗 Life and Light, Simply

## 🟡 Tier 2 — Medium
### 📜 Walkthrough
#### John 2:1–5 · ...
**Says:** ...
**Means:** ...
**Asks:** ...
#### John 2:6–10 · ...
(... blocks until the last verse of the chapter ...)
### 🚫 Common Errors Quick-Reference
| Error | Why it is wrong | The correction, with verse |
|---|---|---|
| ... | ... | ... (John 10:10) |
### 🧨 Cultural Landmines and Misconceptions

## 🔴 Tier 3 — Expert
### 🏗️ Theological Framework
### 📚 Scholarly Insights
### ⚔️ Debate Corner
**Pastoral Warning:** ...
### 🔤 Original Language Deep Dive
### 🚷 Preaching Mistakes to Avoid
- **Information without life:** ...
- **Heat without light:** ...
- ...

## 🟣 Tier 4 — Christocentric, Humility, Life & Light
### 👑 Every Answer in Jesus
### 🙇 Humility Practices
### 🌱 Life Practices
### 💡 Light Practices

## 📚 Doctrine
### Christology · ...
**Proposition:** ...
**Textual Anchor:** ...
**Cross-References:** "..." (...); "..." (...)
**Errors Refuted:** ...
**Pastoral Fruit:** ...
### Soteriology & Grace · ...
(... one block per doctrine, categories in order ...)
### Assumed Here
- **Pneumatology:** ...

## ⚖️ The Council's Hard Questions
### ❓ Question 1 · ...
**Moderator:** ...
**Historian:** ...
**Theologian:** ...
**Resolution:** ...
### ❓ Question 2 · ...
### ❓ Question 3 · ...
### 🔦 The Life & Light Audit
**Pastor:** ...
**Theologian:** ...
**Teacher:** ...
**Fix:** ...

## 🗝️ Leader's Guide
### ⏱️ Session Plan
| Segment | Minutes | What happens |
|---|---|---|
| ... | 5 | ... |
| Naming round | 10 | ... |
### ✅ Answer Key
**Q1.** ... (John 2:1)
### 📖 Glossary
| KJV word | Verse | Meaning |
|---|---|---|
| firkins | John 2:6 | ... |
### 🗺️ Life & Light Leader's Map
**Worked Life Planner Row:** ...
**Worked Light Planner Row:** ...
**When Someone Has No One to Name:** ...
**When Someone Points the Light at Others:** ...
### 🐑 Shepherding Notes
### 🎯 Teaching Angles
**For a Tier 1 Group:** ...
**For a Tier 2 Group:** ...
**Tough Question 1:** ...
**Tough Question 2:** ...
**Tough Question 3:** ...

<!-- counts
believ* | John 2 | 3
-->
```

The counts block holds one line per count you state (`query | scope | number`, exactly as `tools/concordance.py` prints it). Leave it out if you state no counts.

## Part 4 · What goes in each section (chapter units)

| Section | What goes in it | From | Checked by script |
|---|---|---|---|
| **Title and unit line** | `# John N · title (KJV)`, then the unit line as in the skeleton. If `study/john-00.md` exists, use its Lesson Map title for this chapter. | 82 P1 | present |
| 🧵 **Golden Thread** | The Big Idea: one sentence the whole unit serves | 72 C1, 82 P1 | — |
| 🌗 **Life & Light Line** | Two sentences: the death this chapter answers and the life Christ gives instead; the darkness it exposes and the light he gives instead | 72 S4 | — |
| 🎯 **Objectives** | 2–3 measurable learning objectives; at least one a *doing* objective, something a learner can do this week that brings life or light | 72 C7 (Teacher), 82 P1 | 2–3 list items, one starting `**Doing:**` |
| 📋 **Life & Light At-a-Glance** | Two rows, Life and Light; three columns: what is dead or dark, where the source is (with verse), what I do about it today | 72 C1 | rows **Life** and **Light**; a reference in each source cell |
| 🗂️ **Passage Map** | The chapter's sections: one row each, with verses, theme, and a one-line summary | 72 S1 | the Verses cells cover the whole chapter |
| ✝️ **Christological Root** | What Jesus said or did that grounds this chapter, **quoted in full**; the bridge to the doctrine; the canonical echoes as a line, Jesus → Promise → Doctrine → Life; what is lost if this is taught without Christ at the center | 72 C3, S4 | four labels; ≥ 1 whole-verse Gospel quotation; ≥ 3 references in Canonical Echoes |
| ⚔️ **Spiritual Warfare** | The specific Lie; the Truth that answers it, with its verse; the battleground (the mind, the home, the tongue…); the weapon | 72 C3 | four labels; a reference in The Truth |
| 🌱 **Life Pathway** | The Theft (this chapter's own terms), the Source (Christ, with the verse, and his means), the Channel, and the Abundance Guard | 72 GR8, C3 | four labels; a reference in The Source |
| 💡 **Light Pathway** | The Darkness, the Source (with the verse), the Lamp, and the Love Guard | 72 GR9, C3 | four labels; a reference in The Source |
| 🙏 **Open** | A prayer focus (Psalm 119:18 suits most lessons) and one warm-up question, the icebreaker tied to the Golden Thread | 82 P2, 72 C1 | both labels; ≥ 2 write-in lines |
| 🏺 **Setting the Scene** | The Historian's context: facts that change how the text reads | 82 P3, 72 C2 | 150–300 words |
| 🖍️ **Read & Mark** | The marking key, then the whole chapter as `**N** text`, one verse per paragraph, in marked sections that follow the Passage Map | 82 P4, 72 C4 | every verse, in order, exact |
| 👁️ **Observe** (Level 1) | 5–8 'what does it say?' questions, each naming its verse | 82 P5 | 5–8 questions, each citing a verse of the chapter |
| 🔤 **Mind the Language** | 3 or more archaic or misreadable words, with their verse, and a blank for the modern sense | 82 P6, 72 GR5 | 3+ rows; each word is in its verse, and in the Glossary |
| 🔍 **Word Study** | 3–6 words: the KJV word, its verse, the Greek word cited as in rule 4, its sense, and a lookup for the participant (another KJV occurrence; the Law of First Mention) | 82 P7, 72 S2 | 3–6 rows; each word is in its verse; each Greek citation is checked and names the row's verse |
| 🔗 **Search the Scriptures** | A chain of 3–6 cross-references, a summary line each, then one question: what do they teach together? | 82 P8 | 3–6 list items with references; a question |
| 🧩 **Interpret** (Level 2) | 3–5 'what does it mean?' questions, including a View A / View B panel on a disputed point, each view with its proof text, and the question which view the text best supports, and why | 82 P9, 72 GR4 | 3–5 questions; both views, each with a reference |
| 👣 **Case Study** | A Bible character applying or misapplying this chapter's core truth; a reflection question | 82 P10 | a reference; a question |
| 🏙️ **Modern Example** | A believer today meets a real challenge and resolves it by this text; a reflection question | 82 P11 | a question |
| 📜 **Voices from Church History** | One creed, confession, hymn, or sermon: named and summarized, never quoted; a reflection question | 82 P12, 72 GR2 | a question |
| ⛪ **Doctrine in My Own Words** | One proposition per doctrine block in the Doctrine section, each with its anchor verse; then the synthesis prompt | 82 P13 | one list item per doctrine block; ≥ 2 write-in lines |
| ✋ **Apply** (Level 3) | Head (believe), Heart (love), and Hands (do) questions tied to the gospel of grace, including how to humble oneself before God and glorify Christ; then the "I will" line | 82 P14, 72 C7 | the three labels; ≥ 3 questions; an `I will` line with blanks |
| 👑 **Christocentric & Humility** (Level 4) | Every problem in this chapter answered in Jesus, every truth found in him; how it calls us to humble ourselves and make Christ glorious; 3+ Humility Practices; a reflection question | 82 P15, 72 C7 | `**Humility Practices**` with ≥ 3 items, each with a reference; a question |
| 🌱 **Bring Life** (Level 5a) | 3–4 questions (what has the thief stolen where I live? what does Christ give instead, and in whose life am I withholding it?); the Life Planner; 3+ Life Practices; a line the participant can actually say to a dying, despairing, or deadened person this week; the commitment line; the Abundance Guard in italics | 82 P16, 72 C7 | 3–4 questions; the planner; practices (rule 13); `**A Line to Say:**`; the fixed lines |
| 💡 **Bring Light** (Level 5b) | 3–4 questions, the first turned inward (what am I keeping in the dark?); the Light Planner, its first row the participant's own heart; 3+ Light Practices; the commitment line; the Love Guard in italics | 82 P17, 72 C7 | 3–4 questions; the planner with its first row; practices (rule 13); the fixed lines |
| 💎 **Memory Verse** | One verse, **quoted in full**; why it was chosen; copy-it-out lines. If `study/john-00.md` exists, use its Lesson Map memory verse. | 82 P18, 72 C9 | exactly 1 whole-verse quotation; ≥ 2 write-in lines |
| 🤝 **Gather** | The group session: 4 discussion questions with minutes and facilitation cues (seven to ten seconds of silence; comparing Big Ideas); the fourth is the naming round, where each member reads the name on their Life Planner and the dark place on their Light Planner (KJV72's Life & Light Commission). Label them Group question 1 to 4: a G with a number is read as a Strong's number. | 82 P19, 72 C8, C10 | 4 group questions, each with minutes; one the naming round |
| 🌀 **Closing & Going Deeper** | A closing prayer focus; passages for the week ahead; a bridge to the next chapter | 72 C10 | the three labels; ≥ 3 references |
| 🟢 **Tier 1** | Core Concept for a ten-year-old; Key Verses: 3–5 verses **quoted in full**, one sentence each; one Analogy; Diagnostic Check: 4–5 honest, non-condemning yes/no questions; one Action Step for this week; Life and Light, Simply: one sentence each, in a child's words, on how Jesus gives life here and how he gives light here | 72 C5 | 3–5 whole verses; 4–5 questions |
| 📜 **Walkthrough** (Tier 2) | The expository spine, paragraph by paragraph: `#### John N:V–W · short title` blocks, **in order, covering every verse**, **no more than 6 verses each**, each with **Says**, **Means**, and **Asks**, weaving in the word studies, history, and structure. Quote the block's own verses. | 72 C5, GR3 | every verse once, in order, ≤ 6 per block; each block quotes its verses and has the three labels |
| 🚫 **Common Errors Quick-Reference** | Table `Error · Why it is wrong · The correction, with verse`: 2–4 errors a teacher must be able to answer; include 'abundant life means prosperity' and 'being light means exposing other people' when the chapter touches them | 72 C5 | 2–4 rows; a reference in each last cell |
| 🧨 **Cultural Landmines and Misconceptions** | What a modern reader gets wrong about this chapter's world, and the common myths, answered from Scripture | 72 C5 | — |
| 🏗️ **Theological Framework** | Where the chapter sits in systematic theology | 72 C5 | — |
| 📚 **Scholarly Insights** | Commentators, church fathers, creeds, confessions, sermons: author and work named, summarized, never quoted | 72 C5 | (judge) |
| ⚔️ **Debate Corner** | 2–3 positions on a contested point; which is most consistent with Reformed hermeneutics, and why; the Pastoral Warning about its real effect on a church | 72 C5 | `**Pastoral Warning:**` |
| 🔤 **Original Language Deep Dive** | A full word study: parsing, cognates, semantic range, Septuagint use where it helps | 72 C5 | ≥ 1 Greek citation **with a parsing code** |
| 🚷 **Preaching Mistakes to Avoid** | At least 3, including the two that void a study: information without life, and heat without light | 72 C5 | ≥ 3 list items, including those two |
| 👑 **Every Answer in Jesus** (Tier 4) | How this chapter demolishes self-glory and makes Christ supreme; Colossians 2:3 | 72 C5 | cites Colossians 2:3 |
| 🙇 🌱 💡 **Tier 4 practice sets** | 3+ Humility, 3+ Life, and 3+ Light Practices for the leader, different from the lesson's (KJV72 asks for six of each per study: three here and three in the application) | 72 C5 | rule 13, for each set |
| 📚 **Doctrine** | One `### Category · doctrine` block per doctrine, in the category order Theology Proper, Christology, Pneumatology, Anthropology & Sin, Soteriology & Grace, Ecclesiology, Eschatology, Christian Walk (a category may have several blocks). Each block has five labeled parts: Proposition, Textual Anchor, Cross-References (2–3 verses **quoted**), Errors Refuted, Pastoral Fruit. End with `### Assumed Here`, one line for each category the chapter assumes rather than teaches, with where Scripture teaches it | 72 C6, GR11, 82 P13 | ≥ 5 blocks, categories in order; the five labels; 2–3 exact quotations in Cross-References; every category in a block or in Assumed Here |
| ❓ **The Council's Hard Questions** | The three hardest questions this chapter raises (cruxes, tensions, misreadings, controversies), answered in dialogue: the Moderator asks, the scholars answer and challenge one another by name, and each question ends with a Resolution from Scripture or an honest summary of the views | 72 S3, 82 S3 | 3 question blocks, each with `**Resolution:**`; all seven scholars speak |
| 🔦 **The Life & Light Audit** | *If a hearer obeyed this lesson exactly, what in him would come alive, and what dark place would be lit?* The Pastor answers; the Theologian checks it against source discipline; the Teacher says whether a Level 1 participant could do it; the Fix names any change (and the unit has made it), or says none was needed | 72 S3, 82 S3 | the four labels |
| ⏱️ **Session Plan** | The 75 minutes, segment by segment, including the naming round | 72 C1, 82 BM | minutes add up to 75; a naming round row |
| ✅ **Answer Key** | For every question Q1 onward: a suggested answer with verse support; for Levels 4 and 5, model answers, not the only answers | 82 BM | every question answered, each with a reference |
| 📖 **Glossary** | Every archaic word flagged in the lesson, and any other the chapter needs, with its modern sense | 82 BM, 72 GR5 | holds every Mind the Language word; each word is in its verse |
| 🗺️ **Life & Light Leader's Map** | A worked Life Planner row and a worked Light Planner row; how to coach the member who says there is no one to bring life to, and the member who wants to use the light on someone else's sin | 82 BM | the four labels |
| 🐑 **Shepherding Notes** | The tender places this chapter touches, including the Light Planner's first row | 82 BM | — |
| 🎯 **Teaching Angles** | How to teach this chapter to a Tier 1 group and to a Tier 2 group; the three toughest questions it provokes, answered | 72 C5, 72 S2 | the five labels |

## Part 5 · The overview unit (00)

Unit 00 is the book overview and the workbook's front matter: KJV82's Frame and Blueprint (its steps 1 and 4) and its course-long back matter, with KJV72's study of the book as a whole. It has no participant pages. Its skeleton:

```markdown
# The Gospel of John · Book Overview (KJV)
> Unit john-00 · John 1–21 · loop john-kjv-study v2.0 · DRAFT for human doctrine review

## 🧭 At a Glance
### 🧵 Golden Thread
### 🌗 Life & Light Frame
### 🎯 Course Outcomes
### 📋 Life & Light At-a-Glance
### 🗂️ Passage Map

## 🏛️ Core Foundations
(the four foundations, as in a chapter unit, for the whole book)

## 🗺️ Workbook Blueprint
### 📅 Lesson Map
| Lesson | Title | Passage | Big Idea | Core Doctrines | Objective | Memory Verse | Life → Light |
|---|---|---|---|---|---|---|---|
| 1 | ... | John 1 | ... | ... | ... | John 1:14 | ... |
(... 21 rows ...)
### 📘 How to Use This Workbook
### 🧾 Life & Light Ledger
| Lesson | The name I carried life to | What I did | The dark place I carried light into | What I did | Answered prayer or result |
|---|---|---|---|---|---|
| 1 | __________ | __________ | __________ | __________ | __________ |
(... 21 rows, then the closing line with John 15:5 ...)

## 🟢 Tier 1 — Easy
(the six subsections of a chapter unit)
## 🟡 Tier 2 — Medium
### 🏺 Setting the Scene
### 📚 Chapter-by-Chapter Breakdown
#### John 1 · ...
(... John 1 to John 21 ...)
### 🚫 Common Errors Quick-Reference
### 🧨 Cultural Landmines and Misconceptions
## 🔴 Tier 3 — Expert
(the five subsections)
## 🟣 Tier 4 — Christocentric, Humility, Life & Light
(the four subsections)
## 📚 Doctrine
(the course's doctrinal pillars, in the same form)
## ⚖️ The Council's Hard Questions
(three questions about the book, and the audit)
## 🗝️ Leader's Guide
### ❓ Teacher FAQ
### 🛠️ Advanced Teacher Hacks
### 🐑 Shepherding Notes
### 🎯 Teaching Angles
### 🌀 Going Deeper
```

| Section | What goes in it | From | Checked by script |
|---|---|---|---|
| 🌗 **Life & Light Frame** | Two sentences for the whole course: the death John speaks into and the life Christ gives; the darkness he exposes and the light Christ gives | 82 S1 | — |
| 🎯 **Course Outcomes** | 3–5 outcomes a participant should reach by the last lesson; at least one a doing outcome | 82 S1 | 3–5 list items, one starting `**Doing:**` |
| 🗂️ **Passage Map** | The book's movements (Prologue, the Book of Signs, the Farewell, the Passion and Resurrection, the Epilogue) | 72 S1 | ≥ 2 rows |
| 📅 **Lesson Map** | One row per chapter-lesson, in KJV82's Blueprint columns. The chapter units follow it for their title, Big Idea, and memory verse. | 82 S4 | 21 rows, lessons 1–21 in order; each Passage is its chapter; each Memory Verse a verse of that chapter |
| 📘 **How to Use This Workbook** | The individual track (the Law of First Mention, Webster's 1828 dictionary for archaic words) and the group track; the marking key; how the participant pages, the Study, and the Leader's Guide fit together | 82 BM | — |
| 🧾 **Life & Light Ledger** | The course-long tracker, one row per lesson, then the line: this page records what Christ did through you, not what you achieved, with John 15:5 | 82 BM | 21 rows; John 15:5 |
| 🏺 **Setting the Scene** (Tier 2) | Authorship and date as the church has received them (the beloved disciple, traditionally John the son of Zebedee; mark tradition as tradition), audience, and purpose (John 20:30–31) | 72 C2 | — |
| 📚 **Chapter-by-Chapter Breakdown** | `#### John N · short title` for John 1 to John 21 in order, a paragraph each, each quoting at least one verse of its own chapter | ◆ | every chapter, in order, each quoting its chapter |
| ❓ **Teacher FAQ** | KJV82's six questions (a participant who uses another version; a doctrinal misunderstanding; not finishing all five levels; abundant life read as money; light used on others; no one to name on the Life Planner) and John's own (the Jews in John; how John differs from Matthew, Mark, and Luke), each as `- **question?** answer` | 82 BM | ≥ 6 questions |
| 🛠️ **Advanced Teacher Hacks** | KJV82's eight: silent processing, group engagement, the cross-reference hack, the application trick, the doctrinal anchor, humbling and exalting, bring life, bring light | 82 BM | ≥ 8 list items |
| 🌀 **Going Deeper** | Passages for the weeks beyond the course, including one each on life, light, and sound doctrine | 82 BM | ≥ 3 references |

Everything else (the foundations, the tiers, the doctrine, the council) follows the chapter rules in Part 4, applied to the whole book. The overview introduces authorship and date as the church has received them, marking tradition as tradition.

## Part 6 · What happened to the prompts' own process ◆

Both prompts are written for one person in one chat. A loop runs them differently.

| In the prompts | In this loop |
|---|---|
| Steps 1–4: frame, the seven experts' briefs, the council's deliberation, the synthesis (KJV72); frame, briefs, deliberation, blueprint (KJV82) | The maker's method on every unit (Part 2). The briefs aren't printed; the deliberation is, as the Council's Hard Questions and the Life & Light Audit. |
| KJV82's Blueprint checkpoint (`PACING = checkpoint`: halt for `APPROVE`) | Unit 00 carries the Blueprint. Chapter units don't start until a person approves unit 00 (`BLUEPRINT_CHECKPOINT` in `loop.env`); `./run.sh --real --unit NN` runs one anyway. |
| KJV72's Step 6 verification (V1–V14), KJV82's VerifyWorkbook (V1–V18), and the per-lesson PASS/FIX conformity check | **Replaced.** A maker checking itself is the first thing loop engineering removes. Whatever a script can see became a checker rule (Part 1 and the checked column of Part 4); the rest became the judge's rubric (`rubric.md`); a person approves the doctrine. The table in `LOOP-SPEC.md` (CHECKER) maps each V-item to its check. |
| KJV72's self-audit (1–10 on 12 dimensions) and rewrite of the lowest | **Replaced** by the judge's anchored scores and the loop's next iteration, which fixes the judge's first failing line. |
| KJV72's Spiral (three prompt upgrades, and the next command) | **Proposals only:** the maker may add ideas to `proposals/prompt-upgrades.md` and never edits the prompts. The next unit comes from `units.tsv`. |
| KJV82's follow-up commands (`EXPAND`, `ADAPT`, `ANSWERS`, `ADD LESSON`) and KJV72's plain-words rewrite requests | `./review.sh revise NN "notes"`: a person's notes go to the maker on the next run. |
| KJV82's Glossary and Leader's Guide for the whole workbook | Per lesson, in each chapter unit's Leader's Guide; the course-long parts (the FAQ, the teacher hacks, the Ledger) are in unit 00. |
| Voice notifications, `CONTINUE` after a pause, the output file names | Dropped: the maker has no network and writes one file; the loop's logs and escalation notes report progress; the unit is `study/john-NN.md`. |
