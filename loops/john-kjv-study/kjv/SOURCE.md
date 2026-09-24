# Source texts: where every word the checker trusts comes from

The loop never quotes Scripture or cites a Greek word from memory. It looks them up in the files in this folder, and the checker compares every quotation and citation against the same files. This page says where the files came from, how to rebuild them, and how to prove they haven't changed.

**Layer:** these files are the loop's CHECKER data. They're protected: the loop stops with DANGER if any of them changes during a run.

## The files

| File | What it is | Rows | sha256 |
|---|---|---|---|
| `kjv.tsv` | The King James Version, 66 books, one verse per line: `book · chapter · verse · text` | 31,102 verses | `c94fff0d950845cfdc75c6e4b8a54b7443685306bab550a5e9bcbf07b0c505c2` |
| `variants.tsv` | Every verse where the three strongest sources didn't agree, with each reading and the one chosen | 591 verses | `0e793c31070d9c24f1444a16a06ebba06c387353b7ebb195df70d6d42d0961df` |
| `errata.tsv` | Corrections a person has approved after checking a printed KJV. Starts empty. | 0 | (edit by hand only) |
| `greek-nt.tsv.gz` | Every word of the Textus Receptus New Testament that underlies the KJV, with Strong's number, parsing, lemma, and gloss | 139,120 words | `105a69cdad0319e0c1245f77c4ff0ce9d809bb63b5e14e704d4c6ab2c8af72b9` |
| `lexicon.tsv.gz` | Brief Greek and Hebrew lexicon keyed by Strong's number: lemma, transliteration, gloss, short definition, and, where STEP numbers a form separately, the traditional number it belongs to, so that *oida* (G1492, John 21:15) and *oida* (G6063, John 21:15) both check | 21,232 entries | `83e7530ee78ded653a43dc795ac88fe16c74122880099d467864fae8c9582fb0` |

John is complete in both: all 21 chapters and 879 verses, including John 5:4 and John 7:53–8:11, which the KJV prints.

## How `kjv.tsv` was made

No single free digital KJV was clean enough to be the only authority. Compared verse by verse, each transcription of the 1769 standard text had its own slips. In John alone:

| Verse | What one source had (outvoted) | What the KJV reads (checked) |
|---|---|---|
| John 21:11 | ❌ 'full of great fishes, **and** hundred and fifty and three' | "full of great fishes, an hundred and fifty and three" (John 21:11) |
| John 20:27 | ❌ 'Then saith he to Thomas, **reach** hither thy finger' | "Then saith he to Thomas, Reach hither thy finger" (John 20:27) |
| John 19:18 | ❌ 'and two **others** with him' | "and two other with him" (John 19:18) |
| John 15:20 | ❌ 'they will keep **your's** also' (the 1769 spelling) | "they will keep yours also" (John 15:20), as modern printings read |

So `build_kjv.py` reads four public-domain sources, each pinned to a commit and a checksum, and each verse takes the reading that the most sources share. Ties go to the source with the fewest outliers. All four readings of John's four disputed verses went 3 to 1, and the table above shows the winners.

| Source | Pinned file | sha256 of the download |
|---|---|---|
| farskipper/kjv (1769 text) | [`json/verses-1769.json` @ `8f06584`](https://github.com/farskipper/kjv) | `43fbd2fd6a7aebaf62c0c828a85072336143c1fe8233a4856a12db1d5e5df470` |
| thiagobodruk/bible | [`json/en_kjv.json` @ `093b472`](https://github.com/thiagobodruk/bible) | `fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b` |
| seven1m/open-bibles (eBible.org's 1769 text, 2013) | [`eng-kjv.osis.xml` @ `f257a35`](https://github.com/seven1m/open-bibles) | `eeeae647fc28360ce47f9c0d5cc3b397b7fdd9913fe53dc9f44eb6deee50e253` |
| scrollmapper/bible_databases | [`formats/csv/KJV.csv` @ `e1b254c`](https://github.com/scrollmapper/bible_databases) | `a1051b4395bee78d01e239984425f3919563db5caee6fc162d4ddc7faff7eaa8` |

Before the vote, every source gets the same light normalization: italics markers and paragraph marks are removed (the words stay), curly apostrophes become straight ones, the æ ligature is written "ae" (so "Judaea", "Caesar"), and spacing is tidied. Nothing else about the wording, spelling, capitals, or punctuation changes.

**What this text is:** the 1769 Oxford standard text as modern KJV Bibles print it (for example "yours" rather than the 1769 "your's"). A particular printed edition (Cambridge, Oxford, a Thomas Nelson reprint) may differ from it in a handful of places, almost all outside John. If your own Bible differs at a verse the loop quotes, check the other readings in `variants.tsv`, then add a line to `errata.tsv` and rebuild. That's a decision for a person, never for the loop.

## How the Greek files were made

`build_greek.py` reads the STEPBible.org data from Tyndale House, Cambridge ([github.com/STEPBible/STEPBible-Data](https://github.com/STEPBible/STEPBible-Data) @ `b99716b`), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/):

| Source file | sha256 |
|---|---|
| TAGNT Mat–Jhn (Translators Amalgamated Greek NT) | `ab8eaaeb68e17a1dcfa34e1e9350358f22f03bc2a97244d848750ad81044bc8e` |
| TAGNT Act–Rev | `524e32375361e6d3fa2f7ef00b87605fdc4317a762f395651a05fdc31ad031b7` |
| TBESG (brief lexicon, Greek) | `312f723d7b8ef263bbdfb0451c9b8057125804dfff390b6f8544cff2a84b57f4` |
| TBESH (brief lexicon, Hebrew) | `464dccadd95fd8620dd05fa0d7a4caba58ec3c4d5db3ebf38e43d046ca25b591` |

The KJV New Testament was translated from the Textus Receptus (TR), so only words TAGNT marks as present in the TR are kept. Where the TR reads a different word from the modern critical text, TAGNT lists the TR word as a variant, and the index takes that variant. At John 1:18, for example, the index has the TR's word for 'Son', *huios* (G5207, John 1:18), as the KJV reads "the only begotten Son" (John 1:18), where modern critical texts print the word for 'God'. Verse numbers follow the KJV.

**Attribution (CC BY 4.0):** Greek and Hebrew data from STEPBible.org, Tyndale House Cambridge. Changes: filtered to Textus Receptus words, columns reduced, lexicon definitions shortened and stripped of markup.

## Rebuild or verify

```bash
python3 kjv/build_kjv.py --check     # downloads the 4 pinned KJV sources; exit 0 = kjv.tsv is exactly reproducible
python3 kjv/build_greek.py --check   # downloads the 4 pinned STEPBible files; exit 0 = the Greek files are reproducible
sha256sum kjv/kjv.tsv kjv/greek-nt.tsv.gz kjv/lexicon.tsv.gz   # compare with the table at the top
```

Drop `--check` to rebuild in place (for example after adding a line to `errata.tsv`). The downloads come from raw.githubusercontent.com. Every one is checked against its sha256 before it's used, so a changed upstream file stops the build instead of quietly changing the text.
