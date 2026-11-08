# PROMPTS.md — what was actually asked for, and by whom

Two kinds of prompt appear in this project and they must not be confused.

**The prompts on screen are reconstructions.** B00 and B13 render a Claude
composer card. Neither was ever sent. B00's card says so in its own running
text — `RECONSTRUCTION — this prompt was never sent` — and the narration says
it out loud in the first ten seconds. They are there because the Walker
bookend asks for a prompt that describes *this* game, and they do.

**The prompts below are the real ones.** They are the author's instructions to
Claude Code across this assignment, recorded in the author's own words where
they were given in Chinese, with a plain-English gloss. The full transcript
discipline is `../../PROMPTS.md`'s; this file records the ones that shaped the
film.

---

## The reconstructed cards, verbatim

**B00, the opening.**

> Please use Walker to add particle effects to my game design document about
> The Lost — a side-view dungeon crawler where every hazard announces itself
> before it can hurt you. The spike trap needs grit when it strikes and the
> room needs air. Write the scenes and the tests; the verdict on how they look
> in play is mine.

**B13, Your Turn.**

> Please use Walker to capture the same six frames of my particle effect
> before and after one setting change, and count the pixels that differ on
> each frame. I will write the prediction into the brief first. Tell me
> plainly which frames disagree with what I wrote.

Neither was sent. The second is the exercise the beat asks the viewer to do,
and it is bounded on purpose: one setting, a prediction written first, and a
count rather than an opinion.

## The real instructions that shaped this film

| When | The author said | What it meant |
|---|---|---|
| 2026-11-08 | 开影片吧 | *start the film.* The whole build below follows from this one line |
| mid-build | 你在跑的时候必须一直占用我的屏幕吗，我的屏幕总是显示游戏画面，我能切屏吗 | *do you have to hold my screen the whole time — can I switch windows?* This is why the capture driver re-presses its held keys every frame: it could not, and the take that was running at the time came back wrong |
| 2026-11-08, earlier | 你扒吧 | *go ahead and extract it.* The one dated exception to the rule that no agent touches a `.gdshader`, recorded in `CLAUDE.md` |
| 2026-11-07 | 留下 | *keep it.* Effect A's r1 verdict, the one tuning revision this film shows closing |
| 2026-11-07 | 看起来像是天上有浮灰往下掉，但没看出地板灰尘 | *it looks like dust falling from the sky, but I don't see any dust at the floor.* Effect B's r0 verdict, and the reason Effect C exists |

The second row is worth keeping because it changed a file. A question about
screen real estate turned out to be a correctness problem: Godot releases
every pressed key when its window loses focus, so a take written as "hold D
for four seconds" silently becomes "hold D until the user clicks something
else". The driver's `_leg()` now re-presses the key every frame and carries
the whole story in its docstring.

## What was not prompted

No prompt in this project asked for a game change to make the film look
better, and none was made. The one game-source file this film added is
`godot/tests/capture_particles.gd`, which reads state and writes none.

No paid model was called for any part of this film. Narration is local Kokoro
`am_onyx`; cost $0.00.

No prompt was used to generate art, music or texture. There is none to
generate: every particle in this film is Godot's default point.
