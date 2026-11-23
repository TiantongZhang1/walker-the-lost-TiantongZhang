# FRICTIONAL.md — Assignment 8, dated, as it happened

Assignment 8 asks for a `FRICTIONAL.md` inside `pitch/`, so **this file is
the authoritative log for Assignment 8** and the repository's running log,
`../FRICTIONAL.md`, points at it rather than carrying a second copy. Eleven
sentences in this repository have outlived the facts they stated and every
one of them was a second copy of something.

---

## 2026-11-23 — the whole assignment had one day, not five

The assignment says *five days from release*. Canvas said **tomorrow**. So
the five-day shape in the brief — choose, beat sheet, build, gates, assemble
— happened in one sitting, in that order, and the order is the only part of
it that survived.

**What that cost, concretely:** the author did not play anything. Every HUMAN
check in this repository has been answered by them playing the game and
writing down what they said; this assignment has none, because there was
nothing new to play. That is fine for a pitch and it would not be fine for a
build, and it is written here so the difference is on the record.

**What it did not cost:** the fact-check. See the third entry.

## 2026-11-23 — I asked for the due date instead of inferring it, and it mattered

The assignment text says five days. The repository's own standing rule is to
**ask for the due date and not infer it**. Asking produced "tomorrow", which
is four days off what the text implied. An inferred deadline here would have
produced a comfortable plan for a film that was never going to be rendered in
time.

The rule exists because of Assignment 7, where a whole day went into the
wrong assignment from a plausible-looking document. Same shape, caught
earlier: **the document and the reality disagreed, and the person was the
instrument that noticed.**

## 2026-11-23 — the fact-check caught three wrong numbers, all the same wrong

`FACTCHECK.md` traces every narrated claim to a file. Writing it changed
three sentences, none of which any script would have caught:

1. **"four assignments"** on one character in one room → **three**. Four
   assignments have been about The Lost; the GDD was one of them and it built
   nothing in the room.
2. **"eleven things can be cloned at a tag"** → **ten, and the eleventh is in
   no repository at all.** §A has eleven rows and the first is the design
   document, which the same table flags as having no tag. The narration was
   counting a gap as evidence.
3. **"sixty checks are written around cannot turn"** → **"the sixty-check
   suite … has that rule written through it."** `test_swing_edges.gd` is 60
   checks; several of its sections depend on the no-turn rule and the rest
   cover the lock, the air swing, movement, the jump and the two clocks.

**All three are a true number attached to the wrong quantity** — the failure
`CHANGE-BRIEF.md` revision 7.0.3 §2 named in Assignment 7, arriving for the
fourth time, and this time inside the film about honesty. The checker passed
on all three. It compares hashes and coverage; it does not know what a
sentence means.

## 2026-11-23 — the toolkit's own component failed the toolkit's own gate

`./art final` refused the master: **14 BLOCKER `edge-bleed` defects, every one
of them on a `GodotDesignBoard` beat**, all on the bottom title-safe edge.

It is the component, not the content. `GodotDesignBoard.tsx` positions its
source line at `bottom: height*.045` and the `@NikBearBrown` handle at
`bottom: height*.04`; the gate's title-safe inset is 5% and its tolerance is
0.4% of the width, so at 3840 × 2160 the handle's ink lands about seven
pixels outside. **Every frame that component has ever drawn is over the line.**

There was a declarative escape hatch — `qc.full_bleed: true` per beat, which
drops the edge-bleed check. **It was not used.** It is documented for
compositions that fill the frame *on purpose*, and this one does not; setting
it would have been writing down something false to make a gate go quiet.
Assignment 8 says to fix a film that fails its render-integrity check and not
to submit over it.

**What was done instead:** both footer elements moved to `bottom: height*.075`
in the local toolkit checkout, and all seven board beats re-rendered. The
patch is two numbers; `../youtube/claude-liam-walker-the-lost-pitch-gdd/BUILD-PROMPT.md`
carries it, because **this film cannot be rebuilt from a clean clone of the
toolkit without it** and a rebuild recipe that omits that is a recipe that
does not work.

Two MAJOR defects were fixed in this repository rather than in the toolkit:
B01 under-filled the safe area at 43% against a 55% floor (type size raised),
and B07's `zones` layout measured 0.23 ink/background separation against a
0.30 floor (switched to `cards`).

## 2026-11-23 — ffmpeg's drawtext crashed instead of failing, twice over

The held final frames had to be labelled on screen. The first implementation
used `drawtext`; this ffmpeg build has no fontconfig and the filter **exited
with an access violation** rather than an error message. A label that
disappears silently is worse than no label, so the label is a PIL-drawn PNG
overlaid for exactly the held seconds.

Then the replacement ran forever: the label is an endlessly looped still and
only the *first* overlay carried `shortest=1`, so ffmpeg wrote 37 MB of a
ten-second clip before it was stopped. Both overlays carry it now and the
output carries `-t` as well. **A filter graph that can run forever should be
stopped in two places.**

## 2026-11-23 — the toolkit has no show-tell skill, so the pitch used godot-gdd

The assignment says *"if your checkout includes the show-tell skill, it is the
right format for the pitch beats."* This checkout of `brutalist.art` has 22
skills under `skills/make/` and **show-tell is not one of them**.

The workflow used instead is **`godot-gdd` with the `walker` modifier**, which
is the closest thing in the toolkit to what a pitch is: a walk through a
design document's intent, scope, risk and evidence, with proposed,
implemented, observed and pending kept apart by a machine-checked label.
Assignment 7 and the two before it used `godot-gamedev`, which pairs code
with its visible result — the wrong shape for a document that is mostly
proposal.

The document it walks is **`pitch/PROJECT-BRIEF.md`, not
`../the-lost-gdd/GDD.md`**, and `SOURCES.md` §1 says why.

## 2026-11-23 — the outro handle, which I could not change and am not claiming

`ClaudeTitleOutro` is locked by `OUTRO-LOCK.md` with a hardcoded
`@NikBearBrown` handle. Assignment 8 says AI narration *"speaks as you. Do not
use the instructor's name, persona or credit line."*

**The narration complies in full**: it is first person as Tiantong Zhang, the
toolkit's default "Liam, in for Bear" framing is not used, and the
instructor's name and persona appear nowhere in any spoken line. The rendered
outro card still carries the handle, because the toolkit locks that card and
the previous three films in this repository shipped it the same way.

It is a toolkit lock on a card, not a credit this submission is claiming. It
is written here rather than left for a reviewer to wonder about.

## 2026-11-23 — the renderer contradiction, found by writing the risk section

Writing §6 of the brief turned up something that had been sitting in two
committed files since October: **`GDD.md:369` says the renderer is GL
Compatibility and `godot/project.godot:15` says Forward Plus.** Everything in
`TEST-REPORT.md` was measured on Forward+.

Nothing caught this. `tools/check_claude_refs.py` checks `CLAUDE.md`'s facts
against the repository; the GDD lives outside the repository entirely, so no
check in this project has ever been able to see it. **That is the same gap as
the design document having no tag** — it is the one deliverable of this course
that is not under version control here, and §A of the brief lists it as a gap
rather than quietly omitting it.

The contradiction stopped being a live risk when the author chose desktop-only
— a web export is the only thing that forces Compatibility — but the GDD row
is still wrong and §B carries "the corrected GDD renderer row" as work to do.
