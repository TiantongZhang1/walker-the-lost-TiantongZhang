<!-- GENERATED COPY. The original is
     youtube/claude-liam-walker-the-lost-pitch-gdd/GDD-COVERAGE.md
     Rebuild with: python -X utf8 scripts/assemble_pitch_folder.py
     Do not edit this copy; edit the original. -->

# GDD-COVERAGE.md — every section of the document, and the beat that carries it

The document is **`pitch/PROJECT-BRIEF.md`**. It has **nine `## ` sections**
and **all nine are covered**; there are no exclusions in `gdd-evidence.json`,
which is unusual for this workflow and is only possible because the document
was written to be filmed in under four minutes.

`./art godot-gdd --check` compares this mapping with the document's actual
headings as a **set**. A heading reworded in the brief and not here fails the
check — it does not quietly drop out of the film.

---

| § | Section | Beats | Status | What the beat actually does |
|---|---|---|---|---|
| 1 | What is it? | **B02** | `proposed` | One sentence, then the artifact and its form: one `.exe`, title to end screen, under ten minutes. Names the GDD's own cut rule as the reason it is one floor |
| 2 | Why would anyone care? | **B03** | `comparison` | The two progress bars, then **Hollow Knight** — a game the author has played — and the structural difference: there, rescue and bosses are two systems; here they are one |
| 3 | Who opens it, and the first sixty seconds | **B04** | `implemented` | Names the target role, over **real captured play**. What a player is actually moving in minute one |
| 4 | What does it prove about me? | **B05** | `observed` | Four course skills against the tags that hold their evidence, and a fourth card for what the evidence does **not** prove |
| 5 | In, out, first | **B08** | `proposed` | In and out separated; the first piece is one thing, and its first assertion is an **existing** measurement rather than a new one |
| 6 | What could sink it? | **B09** | `pending` | The one concrete risk, derived from this repository's own revisions, and the mitigation that is also §5's "first" |
| 7 | Why this project? | **B10** | `proposed` | New learning separated from existing skill, and one row that is genuinely unknown |
| §A | Exists today | **B06**, **B07** | `implemented`, `proposed` | B06 plays the one mechanism §B is built on and shows it connecting with nothing; B07 puts the list beside §B's |
| §B | Will exist | **B07** | `proposed` | The unstarted list, shown **beside** §A so neither can be read without the other |

**Zero exclusions.** Every section is narrated.

## Beats that are not sections

| Beat | Act | Why it is in the film |
|---|---|---|
| B00 | ASK | Walker's reconstructed Claude composer. Establishes in the first ten seconds that this is a pitch and that most of it does not exist |
| B01 | BLUF | The misconception the film has to kill immediately — that any of the final project is built. Working correction: *finished* → *proposed* |
| B11 | VERDICT | Recapitulation only. **No claim appears here that has not already been made and labelled.** Names what Claude did and what stayed the author's |
| B12 | YOUR TURN | A bounded prompt that revises one design hypothesis and names its test — which is what §6 of this brief is |
| B13 | OUTRO | The locked `ClaudeTitleOutro`. No narration |

## What the coverage check cannot tell you

It is a set comparison and a hash. It does **not** know whether a beat
explains its section well, whether a status label is honest, or whether a
number in the narration is right. `FACTCHECK.md` is where each narrated claim
is traced to the file it came from, including the two that are reasoning
rather than measurement.

## The two documents, and why this is not a GDD film

`../the-lost-gdd/GDD.md` is the four-floor game and is Assignment 4's
deliverable. A film walking **it** would be a film about a game nobody is
being asked to fund. The brief is the project being pitched, and the GDD is
cited inside it twice — once for the cut rule it supplies, once for the
renderer row that contradicts `project.godot`. `SOURCES.md` §1 records the
choice where a reviewer will look for it.
