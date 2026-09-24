# plan.md: the study plan for John

<!-- Layer: Loop design, owned by a person. Protected: the loop stops with DANGER if it changes during a run.
     The maker reads the "For every unit" section and its own unit's entry. Only a person edits this file,
     and each change gets a changelog line in LOOP-SPEC.md. -->

Twenty-two units: a book overview, then one unit per chapter of John. Each unit follows the owner's combined format, KJV72 × KJV82 (`TEMPLATE.md`): KJV82's workbook lesson for the participants, KJV72's Berean Council study for the leader, with a verse-by-verse walkthrough, and KJV82's Leader's Guide. The overview is the workbook's front matter and course plan. The finished set is an in-depth commentary, a 21-lesson workbook, and a leader's guide for the TONA group at the same time.

## For every unit

**John's purpose, in his own words:** "But these are written, that ye might believe that Jesus is the Christ, the Son of God; and that believing ye might have life through his name" (John 20:31). Every unit should show how its chapter serves that purpose.

**The shape of the book** (a common outline, taught as an outline and not as John's own headings):

| Section | Passage | Movement |
|---|---|---|
| Prologue | John 1:1–18 | The Word who was God becomes flesh |
| The Book of Signs | John 1:19–12:50 | Jesus reveals himself to Israel in signs, sayings, and feasts; belief and unbelief divide the hearers |
| The Farewell | John 13:1–17:26 | Jesus washes his disciples' feet, teaches them, and prays for them |
| The Passion and Resurrection | John 18:1–20:31 | The hour of glory: arrest, trial, cross, empty tomb, and the risen Lord |
| Epilogue | John 21:1–25 | Peter restored and the disciples sent; the beloved disciple's testimony |

**Threads to follow through the whole book:**
- **The signs** John narrates in the ministry: water made wine (John 2:1–11), the nobleman's son healed (John 4:46–54), the impotent man healed at Bethesda (John 5:1–15), the five thousand fed (John 6:1–14), Jesus walking on the sea (John 6:16–21), the man born blind healed (John 9:1–7), and Lazarus raised (John 11:1–44). John himself numbers only the first two (John 2:11; 4:54), so present the count of seven as the church's reading, and note that some add the great catch of fish (John 21:1–14).
- **The "I am" sayings** with an image: the bread of life (John 6:35), the light of the world (John 8:12), the door (John 10:7, 9), the good shepherd (John 10:11, 14), the resurrection and the life (John 11:25), the way, the truth, and the life (John 14:6), the true vine (John 15:1, 5). And the "I am" with no image (John 8:24, 28, 58; 13:19; 18:5–8), which echoes Exodus 3:14.
- **The feasts:** Passover (John 2:13; 6:4; 11:55), an unnamed feast (John 5:1), Tabernacles (John 7:2), Dedication (John 10:22).
- **The hour:** not yet come (John 2:4; 7:30; 8:20), then come (John 12:23; 13:1; 17:1).
- **Witness:** John the Baptist, the works, the Father, the scriptures, and Moses (John 5:31–47), then the Spirit and the disciples (John 15:26–27), and the beloved disciple (John 19:35; 21:24).
- **The disciple whom Jesus loved** (John 13:23; 19:26; 20:2; 21:7, 20).
- **Key words**, counted with `tools/concordance.py` rather than from memory: believe, life, light, witness and record, glory, truth, love, abide, world, sent, hour.

## Decisions for all units (made by a person; the loop follows them)

| # | Decision |
|---|---|
| D1 | KJV only. Every quotation is copied from `kjv/kjv.tsv` through `tools/verse.py`. |
| D2 | Tier 3 reads through Reformed hermeneutics, as KJV72 and KJV82 specify: Scripture interprets Scripture. Other positions are stated fairly and at their strongest before the Reformed position is argued. The Debate Corner ends with a Pastoral Warning. |
| D3 | Textual questions: the KJV prints John 5:3–4 and John 7:53–8:11 in full and reads "the only begotten Son" (John 1:18) there. Teach the text the KJV prints. At Tier 3, explain calmly and fairly that many modern editions differ here and why, without scorn for either side. |
| D4 | Peter's restoration: the change between *agapaō* (G25, John 21:15) and *phileō* (G5368, John 21:17) is debated. Present both readings (a meaningful distinction, or stylistic variation) and don't overclaim. |
| D5 | Sources: name the author and work, summarize, never quote a non-Scripture source; write "(verify)" if unsure. The lexicon the tools use is named too: the STEPBible.org brief lexicon, whose Greek entries draw on Abbott-Smith. |
| D6 | Audience: the TONA small group, from new believers to teachers. |
| D7 | The prompts' session defaults: an adult small group of mixed Bible familiarity, one 75-minute session per lesson, a balanced emphasis (doctrinal, devotional, and evangelistic together). |
| D8 | The format is KJV72 × KJV82 (`TEMPLATE.md`), replacing bs3 v3.1. Life (John 10:10), Light (John 8:12), humility and Christ's glory, source discipline, and the detailed doctrines are not options: they are in every unit. |
| D9 | KJV82's Blueprint checkpoint: unit 00 carries the Lesson Map, and chapter units don't start until a person approves unit 00 (`BLUEPRINT_CHECKPOINT` in `loop.env`). |
| D10 | No word limit: a unit is as long as its chapter needs. Length earns nothing with the judge. |

## The units

Working titles may be improved by the maker. The focus notes say what the unit must engage; they are not a script.

### 00 · Book Overview · That Ye Might Believe
Passage: John 1–21. The workbook's front matter and course plan (KJV82's Frame and Blueprint) and KJV72's study of the book as a whole. The Lesson Map sets each chapter-lesson's title, Big Idea, core doctrines, objective, memory verse, and Life → Light line; the chapter units follow it, so choose them with care (the working titles below are a starting point). How to Use This Workbook, the course-long Life & Light Ledger, the Teacher FAQ, and the Advanced Teacher Hacks live here. The author as the church has received him (the beloved disciple, traditionally John the son of Zebedee, writing late in the first century; mark tradition as tradition). John's purpose (John 20:30–31). The outline above, the signs, the "I am" sayings, the feasts, and the key words with concordance counts. How John differs from Matthew, Mark, and Luke (long discourses, the Judean ministry, several Passovers) without setting the Gospels against each other. The chapter-by-chapter breakdown replaces the walkthrough.

### 01 · John 1 · The Word Made Flesh
Passage: John 1:1–51. The Prologue: the Word, *logos* (G3056, John 1:1), with God and God; creation (John 1:3); life and light shining in darkness (John 1:4–5); John sent as a witness (John 1:6–8); the Word received and rejected (John 1:10–13); the Word made flesh who "dwelt among us" (John 1:14), *skēnoō* (G4637, John 1:14), with Exodus 25:8–9 and Exodus 40:34 behind it; grace and truth (John 1:14, 17). The Baptist's witness and the Lamb of God (John 1:29, 36) with Isaiah 40:3. The first disciples and "Come and see" (John 1:39, 46); the titles given to Jesus in this chapter; Jacob's ladder (John 1:51 with Genesis 28:12). D3 applies to John 1:18.

### 02 · John 2 · The First Sign and the Cleansed Temple
Passage: John 2:1–25. The wedding at Cana: "mine hour is not yet come" (John 2:4); the six waterpots "after the manner of the purifying of the Jews" (John 2:6); the first sign that "manifested forth his glory" (John 2:11), *sēmeion* (G4592, John 2:11). The temple cleansed at Passover (John 2:13–17) with Psalm 69:9; "Destroy this temple, and in three days I will raise it up" (John 2:19) and the misunderstanding that follows (John 2:20–22). Jesus "knew what was in man" (John 2:23–25).

### 03 · John 3 · Ye Must Be Born Again
Passage: John 3:1–36. Nicodemus by night; born again or from above, *anōthen* (G509, John 3:3); water and the Spirit (John 3:5, with Ezekiel 36:25–27); the wind and the Spirit (John 3:8); the serpent lifted up (John 3:14–15 with Numbers 21:8–9); John 3:16–21, love, judgment, light and darkness. The Baptist's last witness: "He must increase, but I must decrease" (John 3:30); John 3:31–36.

### 04 · John 4 · Living Water and the Saviour of the World
Passage: John 4:1–54. Jacob's well and the woman of Samaria; living water (John 4:10–14); worship "in spirit and in truth" (John 4:23–24); "I that speak unto thee am he" (John 4:26); the fields white to harvest (John 4:35–38); the Samaritans' confession (John 4:42). The second sign: the nobleman's son healed by a word (John 4:46–54).

### 05 · John 5 · The Son Who Gives Life
Passage: John 5:1–47. The impotent man at Bethesda and the sabbath (John 5:1–16); D3 applies to John 5:3–4. "My Father worketh hitherto, and I work" (John 5:17) and the charge of "making himself equal with God" (John 5:18); the Son's works, judgment, and honour (John 5:19–30); passing from death unto life (John 5:24). The witnesses (John 5:31–47): John, the works, the Father, the scriptures, Moses.

### 06 · John 6 · The Bread of Life
Passage: John 6:1–71. The five thousand fed near the Passover (John 6:1–14); the crowd that would make him king (John 6:15); walking on the sea, "It is I; be not afraid" (John 6:20). The discourse at Capernaum: manna and the true bread from heaven (John 6:31–33 with Exodus 16); "I am the bread of life" (John 6:35); the Father giving, drawing, and raising up (John 6:37–40, 44); eating his flesh and drinking his blood (John 6:51–58). Many disciples turn back; Peter's confession (John 6:66–69); Judas (John 6:70–71). Tier 3 Debate Corner candidates: the drawing of John 6:44 (effectual calling and other readings), and whether John 6:51–58 speaks of the Lord's Supper.

### 07 · John 7 · Rivers of Living Water
Passage: John 7:1–53. The feast of tabernacles (John 7:2); his brethren's unbelief (John 7:5); "My time is not yet come" (John 7:6); teaching in the temple and the crowd's division (John 7:14–36); the last great day of the feast (John 7:37–39) and the Spirit not yet given; officers who report "Never man spake like this man" (John 7:46); Nicodemus asks for a fair hearing (John 7:50–51). John 7:53 opens the passage about the woman taken in adultery (D3); cover the verse here and the story in unit 08.

### 08 · John 8 · The Light of the World
Passage: John 8:1–59. The woman taken in adultery (John 8:1–11; D3). "I am the light of the world" (John 8:12); the Father's witness; "if ye believe not that I am he, ye shall die in your sins" (John 8:24); "the truth shall make you free" (John 8:32); children of Abraham or of the devil (John 8:33–47); "Before Abraham was, I am" (John 8:58) with Exodus 3:14, and the stones (John 8:59).

### 09 · John 9 · Once Blind, Now Seeing
Passage: John 9:1–41. The disciples' question and Jesus' answer about the man born blind (John 9:2–3); "I am the light of the world" (John 9:5); the pool of Siloam, "which is by interpretation, Sent" (John 9:7); the neighbours, the parents, and the Pharisees; "whereas I was blind, now I see" (John 9:25); cast out (John 9:34); belief and worship (John 9:35–38); the blindness of those who say "We see" (John 9:39–41).

### 10 · John 10 · The Good Shepherd
Passage: John 10:1–42. The shepherd, the thief, and the door (John 10:1–10); "I am the good shepherd" (John 10:11, 14), *poimēn* (G4166, John 10:11), with Ezekiel 34 and Psalm 23; laying down his life and taking it again (John 10:17–18); the feast of the dedication (John 10:22); "My sheep hear my voice" (John 10:27) and "they shall never perish" (John 10:28); "I and my Father are one" (John 10:30); "Ye are gods" (John 10:34), quoting Psalm 82:6. Tier 3 Debate Corner candidate: the security of the sheep (John 10:28–29).

### 11 · John 11 · The Resurrection and the Life
Passage: John 11:1–57. Lazarus sick, the delay, and the reason given (John 11:4–6); Martha's faith and "I am the resurrection, and the life" (John 11:25–27); "Jesus wept" (John 11:35); "Lazarus, come forth" (John 11:43); the council's fear and Caiaphas's unwitting prophecy (John 11:47–52); the Passover near (John 11:55).

### 12 · John 12 · The Hour Is Come
Passage: John 12:1–50. Mary anoints Jesus at Bethany (John 12:1–8); the entry into Jerusalem with Zechariah 9:9 (John 12:12–16); the Greeks who would see Jesus (John 12:20–22) and "The hour is come" (John 12:23); the corn of wheat (John 12:24); the troubled soul and the Father's voice (John 12:27–30); "if I be lifted up from the earth" (John 12:32); unbelief foretold by Isaiah (John 12:37–41 with Isaiah 53:1 and 6:10); the last public appeal (John 12:44–50).

### 13 · John 13 · Having Loved His Own
Passage: John 13:1–38. The hour and the love "unto the end" (John 13:1); the foot washing and its meaning (John 13:2–17); the betrayer (John 13:18–30) and "ye may believe that I am he" (John 13:19); the new commandment, *entolē* (G1785, John 13:34) and *kainos* (G2537, John 13:34); Peter's denial foretold (John 13:36–38).

### 14 · John 14 · The Way, the Truth, and the Life
Passage: John 14:1–31. "Let not your heart be troubled" (John 14:1); the Father's house (John 14:2–3); "I am the way, the truth, and the life" (John 14:6); seeing the Father in the Son (John 14:8–11); greater works and prayer in his name (John 14:12–14); another Comforter, *paraklētos* (G3875, John 14:16), and the Spirit of truth (John 14:16–17, 26); love and obedience (John 14:15, 21–24); "Peace I leave with you" (John 14:27).

### 15 · John 15 · Abide in Me
Passage: John 15:1–27. "I am the true vine" (John 15:1) and "I am the vine, ye are the branches" (John 15:5) with Isaiah 5:1–7 and Psalm 80:8; abiding, *menō* (G3306, John 15:4), and bearing fruit (John 15:1–8); love and friendship (John 15:9–17), "Greater love hath no man than this" (John 15:13) and "Ye have not chosen me, but I have chosen you" (John 15:16); the world's hatred (John 15:18–25); the Comforter's witness and the disciples' witness (John 15:26–27). Tier 3 Debate Corner candidate: the branches that are taken away and burned (John 15:2, 6).

### 16 · John 16 · Sorrow Turned into Joy
Passage: John 16:1–33. Persecution foretold (John 16:1–4); "It is expedient for you that I go away" (John 16:7); the Spirit who will reprove the world, *elenchō* (G1651, John 16:8), of sin, righteousness, and judgment (John 16:8–11) and guide into all truth (John 16:13–15); the little while, and sorrow turned to joy (John 16:16–24); asking the Father (John 16:23–27); "I have overcome the world" (John 16:33).

### 17 · John 17 · The High Priestly Prayer
Passage: John 17:1–26. "Father, the hour is come; glorify thy Son" (John 17:1); eternal life as knowing the Father and the Son he sent (John 17:3); prayer for the disciples: kept, sanctified, sent (John 17:6–19), "thy word is truth" (John 17:17); prayer for all who will believe: "that they all may be one" (John 17:20–23); the glory given and the love that remains (John 17:24–26).

### 18 · John 18 · Whom Seek Ye?
Passage: John 18:1–40. The garden and the arrest; "I am he" (John 18:5) and the band that "went backward, and fell to the ground" (John 18:4–8); Peter's sword and the cup (John 18:10–11); before Annas and Caiaphas; Peter's three denials (John 18:15–18, 25–27); before Pilate: "My kingdom is not of this world" (John 18:36) and "What is truth?" (John 18:38); Barabbas (John 18:39–40).

### 19 · John 19 · It Is Finished
Passage: John 19:1–42. The scourging and the crown of thorns; "Behold the man!" (John 19:5); "We have no king but Caesar" (John 19:15); the title in Hebrew, Greek, and Latin (John 19:19–22); the garments and Psalm 22:18 (John 19:23–24); "Woman, behold thy son!" (John 19:26–27); "I thirst" (John 19:28); "It is finished" (John 19:30), *tetelestai* (G5055, John 19:30, V-RPI-3S); no bone broken and the pierced side (John 19:31–37, with Exodus 12:46 and Zechariah 12:10); the burial by Joseph and Nicodemus (John 19:38–42).

### 20 · John 20 · That Ye Might Believe
Passage: John 20:1–31. The empty tomb and the grave clothes (John 20:1–10); Mary Magdalene and "Rabboni" (John 20:11–18); peace, sending, and the breath of the Spirit (John 20:19–23); Thomas: "My Lord and my God" (John 20:28) and the blessing on those who have not seen (John 20:29); the purpose of the book (John 20:30–31).

### 21 · John 21 · Lovest Thou Me?
Passage: John 21:1–25. The night of fishing and the great catch (John 21:1–14); breakfast by the fire of coals (John 21:9); Peter restored with three questions (John 21:15–17; D4); "Feed my sheep" (John 21:16, 17); Peter's death foretold and "Follow me" (John 21:18–19); "what is that to thee? follow thou me" (John 21:22); the beloved disciple's testimony and the books the world could not contain (John 21:24–25).
