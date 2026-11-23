# PROMPTS.md — what was asked, in order, and in whose words

Assignment 8 allows Claude throughout and asks what it contributed.
`SOURCES.md` §6 is the line-by-line split; this is the sequence.

**The author's words are quoted exactly, in the language they were written
in.** Everything else is a paraphrase of a Claude-side instruction.

---

## 1. The assignment, pasted

The author pasted the full Canvas text of *Assignment 8 — Final Project Pitch
Film* and wrote:

> 现在做这个
> *(do this one now)*

**No project had been chosen at this point and Claude did not choose one
unprompted.** The first response was a question, not a draft.

## 2. The one question that mattered, and the author's answer

Claude offered to skip the questions and asked one:

> 毕业之后你最想干的那份活,具体是什么样子的?
> *(what does the job you most want after graduating actually look like?)*

The author declined the conversation and said:

> 你先来按照咱们之前的设想出一版我来提意见
> *(you do a first version based on what we already designed, and I'll give
> notes)*

**"咱们之前的设想" is `../the-lost-gdd/GDD.md`** — Assignment 4's design
document, written in October. So the project was never invented for this
assignment; the brief is a cut of a document that already existed, and
`PROJECT-BRIEF.md` §1 quotes the GDD's own cut rule as the authority for
which cut.

## 3. The first draft, with four things deliberately left open

Claude read the GDD, the repository at `a7`, `TEST-REPORT.md`,
`CHANGE-BRIEF.md` and `FRICTIONAL.md`, and wrote `pitch/PROJECT-BRIEF.md`
with four items marked **open for the author, not for Claude**:

1. the comparable game — *"the assignment requires one or two real games the
   author has actually played, and Claude must not supply them"*;
2. the target role;
3. desktop or web;
4. the first piece and its first assertion.

Candidates were offered for 1 and 3 and labelled as candidates.

## 4. The author settled all four

> 1.比较像空洞骑士这个类型的 2.岗位对了 3.就做桌面版不做网页版 4.截止日期明天
>
> *(1. it's more the Hollow Knight type. 2. the role is right. 3. desktop
> only, no web build. 4. the deadline is tomorrow)*

**That one line is the source of four of this film's load-bearing facts**:
the comparable named in B03, the target role in B04, the artifact in B02,
and — because desktop-only retires the renderer risk — the fact that B09 is
about the swing rather than about the Compatibility renderer.

The risk changed **because the author changed the scope**, and
`PROJECT-BRIEF.md` §6 keeps the retired risk on the page with what retiring
it costs, rather than deleting it.

## 5. The build instructions, to Claude

Paraphrased; these were Claude-side working decisions, not the author's.

| | |
|---|---|
| Workflow | `godot-gdd` with the `walker` modifier, against `pitch/PROJECT-BRIEF.md`. Not `godot-gamedev`, which A5, A6 and A7 all used: this film explains a proposal's intent, scope, risk and evidence, which is the shape `godot-gdd` is for |
| Narration | first person, as Tiantong Zhang. **Not** the toolkit's default "Liam, in for Bear" — Assignment 8 requires the narration to speak as the author and forbids the instructor's name or persona |
| Length | 2–4 minutes, enforced by the sheet builder, which prints a warning outside that range |
| Footage | re-use A7's played captures rather than re-record; label every held frame |
| Honesty | every body beat carries a `design_status`; nothing unbuilt is drawn as a picture |

## 6. The prompt the film hands back

B12's **Your Turn** card, verbatim as it appears on screen:

> Find the design rule I have the most evidence for. Tell me what conditions
> that evidence was gathered under, and name one condition it has never been
> tested in.

It is the question `PROJECT-BRIEF.md` §6 is the answer to, and it is handed
to the viewer because the answer here was uncomfortable: the most-asserted
rule in this project is *the swing cannot turn*, and every check behind it
ran in a room with no opponent in it.

## 7. What was NOT asked, and did not happen

- No game code was changed. `git diff b33b06c..a8 -- godot/` is empty.
- No paid API call, no key, no account, no upload. Narration cost **$0.00**.
- No asset was downloaded, generated as art, or fetched from a library.
- Claude did not choose the project, the comparable, the role or the scope.
