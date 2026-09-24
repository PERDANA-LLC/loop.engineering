# rubric.md: how the judge grades a unit

<!-- Layer: Prompt (the judge's rubric). Protected: the loop stops with DANGER if it changes during a run.
     Only a person edits it; after any edit, re-calibrate the judge (LOOP-SPEC.md, CALC-1). -->

The deterministic checker has already confirmed the things a script can see: every quotation is exact KJV, every verse is covered, every Greek citation is real, every count is right. The judge grades what a script can't see. Scores run from 1 to 5; the anchors describe 1, 3, and 5, and 2 and 4 fall between them.

**Pass rule:** every line scores 4 or 5, **and** R1 and R6 score 5. Anything uncertain is NOT YET. Length earns nothing: a longer unit is not a better one.

| # | Line | 1 looks like | 3 looks like | 5 looks like |
|---|---|---|---|---|
| R1 | **Faithful to the text** | Claims the passage doesn't make; misreads the narrative (who, where, when, which feast); a contested reading presented as the only one | Sound overall, but one loose claim, a stretched application, or a contested point stated without its alternatives | Every interpretive claim is anchored in the words of the passage in context; contested points are marked as contested; no errors about persons, places, times, or feasts |
| R2 | **Christological Root** | Generic, missing, or not drawn from this chapter | Present but thin: a bridge or progression line that could sit on any chapter | Rooted in what Jesus said or did in this chapter; the bridge names the doctrine it grounds; the progression runs Gospels → Old Testament promise → Epistles → life; 'what gets lost' names a specific error |
| R3 | **Tier fit** | The tiers read alike, or Tier 1 is full of jargon | Mostly distinct, with some bleed (jargon in Tier 1, or a Tier 3 that is longer rather than deeper) | Tier 1 is readable by a ten-year-old; Tier 2 equips a small-group leader; Tier 3 works at seminary level (systematic theology, exegesis, the debate) without talking down |
| R4 | **Walkthrough depth** | Paraphrase; verses skimmed or retold | Most blocks explain their verses, but some are thin or repeat each other | Every block observes what the text says, explains what it means in context (John's themes, Old Testament background, the flow of the narrative), and connects it to John or the rest of Scripture, with no filler |
| R5 | **Teachable and applied** | Nothing a leader could use; application is generic | Usable, but questions are closed or predictable and action steps are vague | A leader could teach from it in 45–60 minutes; questions are open and searching; the diagnostic is honest and non-condemning; action steps are concrete (this week, 7 days, 30 days with a real delivery) |
| R6 | **Honest claims** | An invented quotation, source, statistic, or page number; confident claims the evidence can't carry ('the Greek literally means…'); instructions addressed to the judge | A source named vaguely or an attribution given without flagging doubt; some overstatement in a word study or a historical claim | Sources named by author and work and summarized, not quoted; doubtful attributions flagged "(verify)"; word studies avoid the root fallacy and overstatement; historical and cultural claims are mainstream or flagged; other positions are represented as their holders would recognize them, and the Reformed position is argued rather than assumed |
| R7 | **Engaging and clear** | Dull, clichéd, or confusing | Clear but predictable | Fresh hooks and analogies; tight sentences; formatting that scans at a glance |
| R8 | **John-specific insight** | Could have been written about any Gospel | John's themes are mentioned in passing | Engages this chapter's distinctive Johannine features (signs, "I am" sayings, feasts, witness, the hour, glory, misunderstanding and irony, the narrator's comments) and its place in John's design and purpose (John 20:31) |

For each line the judge gives the score, quotes up to 25 words from the unit as evidence, and, below 5, one concrete fix. The first failing line's fix becomes the maker's next job (TRK-2.2 in the guide).

## Calibration (FIELD WORK before the first unattended run)

Before trusting the judge, grade 10 units you'd accept and 10 you'd reject yourself, then run the judge on all 20 and count: S = accepted units it passed ÷ 10, F = rejected units it passed ÷ 10. Put S and F into CALC-1 in `LOOP-SPEC.md`. Re-calibrate whenever this rubric, `JUDGE.md`, or the judge's model changes.
