# PROMPTS.md — what was actually asked, and in what order

**B00 and B16 are reconstructions.** Both say so on screen and B00 says it
aloud in its first breath. This file is what was really said.

The work in this repository was done across six days, 2026-11-15 to
2026-11-21, in a conversation of many turns. A single prompt card cannot be a
transcript of that and is not offered as one. What follows is the shape of the
asking, with the author's own words quoted verbatim where they drove a change
— which is most of the time, because **nine of the ten revisions in this
assignment began with the author playing the game.**

The author writes in Chinese; every quotation keeps the original and carries a
translation. `TUNING.md` holds all of them in their dated entries.

---

## Before any code: the brief

`CHANGE-BRIEF.md` was written and **committed before the first agent prompt of
this assignment**, and `CLAUDE.md` imports it with `@CHANGE-BRIEF.md`, so it is
the contract the agent works to rather than a summary written afterwards. It
carries a tag convention the whole assignment depends on:

> **[decided]** — chosen by the author. **[proposal]** — derived by Claude and
> not yet confirmed.

**That convention is why the two-clocks measurement exists.** §8's prediction
was tagged `[proposal]`; a tagged prediction is something to test, so a
measurement got built to test it, and it found the prediction wrong in sign.
An untagged sentence would have been believed.

## The ten revisions, in the author's words

| rev | what was said | what it became |
|---|---|---|
| 7.0.1 | 这个人物模型也太简陋了，不能做到保持之间咱们用gpt做好的人物形象码<br>*[this character model is far too crude — can't we keep the character we already made with GPT?]* | the two clips swapped routes; the sheet is CUT from the existing art |
| 7.0.2 | 刀不太对，他不是挥出去的，而是在身子上面转圈<br>*[the sword isn't right — it isn't swinging out, it's spinning in circles above the body]* | R1 and R2: the arc travels one way, and it finishes below the hand |
| 7.0.3 | 刀没挥出去，以刀把为中心在旋转，而且旋转的中心点在人物背部，我觉得应该在前面<br>*[the sword isn't swinging out, it's rotating about the hilt, and the centre of rotation is at the character's back — I think it should be in front]* | `SwordArm:position` is keyed; R3 |
| 7.0.4 | 刀再长一点，然后把跳跃改成空格键<br>*[make the sword a bit longer, and change jump to the spacebar]* | 16 px → 20 px; jump was **already** on space, and the test that claimed so was strengthened to press the real keys |
| 7.0.5 | 让角色在空中也能挥刀<br>*[let the character swing in the air too]* | the `is_on_floor()` gate on attack is deleted |
| 7.0.6 | 人挥刀的时候也要可以移动<br>*[the character should be able to move while swinging too]* | the movement lock goes; the objection is written down first |
| 7.0.7 | 跑步的时候腿部姿势有点奇怪，不是两个腿交替着跑而是两个腿在各自晃悠<br>*[the legs look odd when running — it isn't two legs alternating, it's two legs each waggling on their own]* | three separate defects found; the cycle is rebuilt |
| 7.0.8 | — | **nobody asked.** The measurement was built because §8 was tagged `[proposal]`, and it disagreed with it |
| 7.0.9 | 角色没有飘逸，但我不是很想让角色边挥刀边滑行<br>*[there's no drift in the cells, but I don't really want the character sliding while it swings]* | the legs get their own `AnimationPlayer`; the rule turns out to be a partition |
| 7.0.10 | 我还希望挥刀的时候也能跳起来，而且不会打断挥刀动作<br>*[I'd also like to be able to jump while swinging, and for it not to interrupt the swing animation]* | the jump leaves the lock; the two halves of the sentence get different evidence |

**Four of those are two sentences long and none of them names a file.** The
shape that worked was: the author plays, says what is wrong in the terms a
player would use, and the agent is responsible for turning that into a
measurement. 转圈 — *spinning in circles* — is not a technical description,
and the technical fact behind it (the tip is never below −3 px in any of the
eighteen frames) was derivable from a table that had been in the repository
for two days.

## The standing instructions

These were given once and held for the whole assignment. They are in
`CLAUDE.md`, which is loaded on every turn.

- **`godot/shaders/` is hand-written by the human and never edited by an
  agent.** `git diff --stat godot/shaders/` must print nothing after every
  agent session, and `scripts/run-test.sh` is diffed too.
- **Clips live as resources, never built in code at runtime.**
- **Every prediction and every `TUNING.md` verdict is the human's.** An agent
  may write the entry; the verdict line stays blank until the author plays it.
- A named list of things out of scope: collision layers, `SPEED`,
  `JUMP_VELOCITY`, `GRAVITY`, the input bindings, the trap's timings, the
  `.glb` files, every A6 effect scene, and the pose PNGs.
- **Never add `--rendering-driver` to a test command.**

**Two of those were crossed, both named in advance.** Revision 7.0.6 changed
two existing tests' expectations, which `CLAUDE.md` forbids — and both
assertions were **inverted rather than deleted**, so the files still state
what the rule is. A test left asserting a superseded rule is the loudest
available way to find out the design moved; a test deleted for failing is the
quietest.

## What the film's two prompt cards say

**B00** is written to show the shape of the opening ask: a looping clip, a
committing action, write the clips and the read-backs, *the verdict on how
they look in play is mine*. That last clause is the only part of the card that
is a quotation of a real standing instruction.

**B16** is the viewer's turn, not a prompt that was sent. It asks for one
bounded thing: find a sentence in your own notes that says something is
impossible or needs a big piece of machinery, and **check it against the
engine rather than against the sentence.**

## What was not prompted for

- No asset library, no 3D generator. `generate_3d`, `search_assets` and
  `import_asset` were never called in this assignment.
- No named living artist's style, no copyrighted character, no brand, no
  existing music in any prompt.
- The film's narration was written by Claude and the figures in it are
  audited in `FACTCHECK.md` — **by the same person who wrote the narration**,
  which is worth knowing while reading it. One figure was wrong and was
  corrected before the film shipped; that correction is recorded rather than
  quietly applied.
