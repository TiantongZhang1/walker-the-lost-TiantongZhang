#!/usr/bin/env python3
"""Generate beat_sheet.json and gamedev-evidence.json for the gamedev film.

The code shown on screen is READ FROM THE SOURCE here, never typed, so
`excerpts[].text` and `shot.remotion.props.code` cannot drift from the file or
from each other. The evidence checker compares all three.
"""
import hashlib, io, json, os, subprocess

ROOT = r"D:\Graduate\2026Fall\7270\walker-ninja-TiantongZhang"
os.chdir(ROOT)
GAME = "godot"
REEL = "youtube/claude-liam-walker-ninja-gamedev"
TITLE = "NewWalkerArtVideo_TiantongZhang"
SLUG = "claude-liam-walker-ninja-gamedev"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def excerpt(rel, a, b):
    """One-based inclusive line range, newline joined, no trailing newline."""
    lines = io.open(os.path.join(GAME, rel), encoding="utf-8", newline="").read().split("\n")
    return "\n".join(lines[a - 1:b])


EX = {
    "B02": ("features/player/player.gd", 118, 134),
    "B04": ("features/player/player.gd", 313, 326),
    "B06": ("game/session.gd", 276, 288),
    "B08": ("game/session.gd", 601, 611),
    "B10": ("features/player/player.gd", 674, 690),
}

PROJECT = "walker-ninja-TiantongZhang"


def code_beat(bid, path, a, b, title, notes, cues, secs, narration, role, show, font=23):
    text = excerpt(path, a, b)
    return {
        "beat_id": bid, "act": "BUILD", "role_note": role,
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": secs,
        "shot": {
            "type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "motion": "code-highlight", "show": show,
            "remotion": {
                "pattern": "GodotDevWorkbench",
                "props": {
                    "mode": "code", "title": title, "project": PROJECT,
                    "path": "godot/%s  lines %d-%d" % (path, a, b),
                    "source": "godot/%s" % path, "code": text, "startLine": a,
                    "codeFontSize": font,
                    "inspectorLabel": "Source notes - not Inspector values",
                    "notes": notes, "cues": cues, "durationSeconds": secs,
                },
            },
        },
    }


def footage_beat(bid, capture, window, secs, narration, role, show):
    return {
        "beat_id": bid, "act": "RESULT", "role_note": role,
        "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
        "estimated_duration_s": secs,
        "shot": {
            "type": "FOOTAGE", "class": "SHOW", "source": "capture",
            # "capture", not "own": beat_plan.fill_plan reads this field and
            # falls through to "ai-video-prompt" for anything it does not
            # recognise, which put "ai-video-prompt / human" against three real
            # Godot captures in the generated STATUS.md. "capture" is the
            # toolkit's own word for footage the CLI cannot fake.
            "motion": "gameplay", "capture": capture,
            "window_s": window, "show": show,
            "evidence_media": "capture/%s.mp4" % capture,
        },
    }


beats = []

# ---------------------------------------------------------------- bookend 1
beats.append({
    "beat_id": "B00", "act": "ASK",
    "role_note": "WALKER BOOKEND 1/4 - ClaudeComposerAsk. The prompt begins "
                 "'Please use Walker to convert my game design document about ...' "
                 "and describes THIS game. It is an illustrative RECONSTRUCTION and "
                 "the narration says so out loud; no fabricated build receipts. "
                 "IN-FOR-BEAR LAW: Liam is named in the first breath.",
    "narration_text":
        "Sawubona - this is Liam, in for Bear. This one is a teardown, not a "
        "playthrough. The prompt on screen is a reconstruction, written to be "
        "illustrative, and it is not a transcript of anything. The game under it is "
        "real. It is a dungeon slice running in Godot four, and this time the "
        "character you are looking at was generated.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 21,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "type-on",
             "show": [{"at": "0.03", "event": "composer card fades in"},
                      {"at": "0.12", "event": "greeting 'Sawubona, Liam' lands"},
                      {"at": "0.28", "event": "the Walker prompt types on"},
                      {"at": "0.78", "event": "RECONSTRUCTION label stays visible"}],
             "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                 "greeting": "Sawubona, Liam",
                 "prompt": "Please use Walker to convert my game design document "
                           "about a cyber-ninja in a torchlit dungeon - double jump, "
                           "one air dash, a sword, pop-up spike traps and patrolling "
                           "enemies - into a playable Godot project, and then let me "
                           "replace the code-drawn character with generated art "
                           "without letting the blade and its hitbox come apart.",
                 "label": "RECONSTRUCTION - illustrative, not a transcript",
                 "brandLabel": "@NikBearBrown"}}}})

# ---------------------------------------------------------------- bookend 2
beats.append({
    "beat_id": "B01", "act": "RESULT",
    "role_note": "WALKER BOOKEND 2/4 - hesitant-writer overview of what actually "
                 "exists, with a MEANINGFUL single-word correction: the writer first "
                 "types 'a generated game', strikes 'game' and writes 'character'. "
                 "States the slice's limits rather than the assignment's ambitions.",
    "narration_text":
        "Here is what actually changed. The level is the same three thousand and "
        "seventy-two pixels it was, and the eight movement values are the same eight. "
        "What is new is the art, the sound and the music. The character is nine "
        "generated images - one reference and eight poses, one per state the engine "
        "can already tell apart. The music is one generated loop. The four sound "
        "effects are not generated at all; they are synthesised by arithmetic, and I "
        "will say that again when you hear one. The dungeon is not generated either. "
        "Neither is his sword, and that is the most interesting decision in the "
        "project.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 38,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "hesitant-write",
             "show": [{"at": "0.02", "event": "heading framed, cards below"},
                      {"at": "0.22", "event": "'a generated game' is written"},
                      {"at": "0.34", "event": "'game' is struck through"},
                      {"at": "0.40", "event": "'character' is written in its place"},
                      {"at": "0.66", "event": "the placeholder line lands, greyed"}],
             "remotion": {"pattern": "ClaudeHesitantWriter", "props": {
                 "heading": "What Assignment 2 changed",
                 "draft": "a generated game",
                 "strike": "game",
                 "correction": "character",
                 "lines": [
                     "Level: unchanged. 3072 px, same eight movement values.",
                     "Character: 9 generated images - 1 reference, 8 poses.",
                     "Music: 1 generated loop, 16 bars, on its own bus.",
                     "Sound effects: NOT generated. Synthesised placeholders.",
                     "Dungeon, HUD, enemies, traps: original vector drawing.",
                     "The blade: still drawn in code, on purpose."],
                 "brandLabel": "@NikBearBrown"}}}})

# ------------------------------------------------- C1 pose_key -> take p
beats.append(code_beat(
    "B02", *EX["B02"][:1], EX["B02"][1], EX["B02"][2],
    title="One sprite per state the engine can already name",
    notes=[
        {"label": "Why a string and not a texture",
         "value": "A string can be asserted without a renderer. The check drives the game through all eight states and reads the key back."},
        {"label": "Why death is tested first",
         "value": "On death the body is disabled and is_on_floor() keeps whatever it last returned, so a pose derived from movement would differ by cause of death."},
        {"label": "Cost",
         "value": "One dictionary lookup per frame, and the names live in two places. A mismatch is a missing texture, not a wrong one."}],
    cues=[{"at": 2.0, "line": 119, "label": "death first"},
          {"at": 7.0, "line": 128, "label": "dash outranks the air"},
          {"at": 11.0, "line": 130, "label": "rise or fall by velocity sign"},
          {"at": 15.0, "line": 134, "label": "idle is the fallthrough"}],
    secs=23,
    narration=
        "Eight generated sprites, one per state. The function that picks one returns a "
        "string, not a texture - and that is the whole reason the mapping can be "
        "tested. Death is checked first, because on death the body is disabled and "
        "is on floor keeps whatever it last returned; a pose read off movement would "
        "depend on how you died. Then the swing, then the dash, then the sign of "
        "vertical velocity for rising or falling, and idle is what is left.",
    role="C1 CODE. pose_key() verbatim from player.gd. Paired with B03.",
    show=[{"at": "0.05", "event": "the excerpt is already readable"},
          {"at": "0.09", "event": "line 119 highlights - death_pose"},
          {"at": "0.30", "event": "line 128 highlights - dash_ticks_left"},
          {"at": "0.48", "event": "line 130 highlights - not is_on_floor()"},
          {"at": "0.65", "event": "line 134 highlights - idle"}]))

beats.append(footage_beat(
    "B03", "take-p", [0.20, 3.30], 17,
    narration=
        "And here is that table in motion. Idle, run, rise, fall, back to run, idle "
        "again, then the air dash at the top of the second jump. Those transitions "
        "are not read off the picture: the capture driver logs pose key every time it "
        "changes, with the tick it changed on.",
    role="C1 RESULT. take-p, native 3840x2160, the pose sequence the input log "
         "records: idle, run, rise, fall, run, idle, rise, dash, fall, idle.",
    show=[{"at": "0.04", "event": "idle on the opening platform"},
          {"at": "0.20", "event": "run - the scarf streams back"},
          {"at": "0.36", "event": "rise, then fall, over the 16 px step"},
          {"at": "0.58", "event": "idle again, facing right"},
          {"at": "0.74", "event": "jump, then the air dash - body level, scarf straight"}]))

# ------------------------------------------------- C2 the rim -> the strip
beats.append(code_beat(
    "B04", *EX["B04"][:1], EX["B04"][1], EX["B04"][2],
    title="The rim is a light, not an outline",
    notes=[
        {"label": "The arithmetic",
         "value": "A rim grown on four sides costs a part 2 px of width. A 3 px arm keeps 1 px of armour. Rendered, the limbs came out as grey pipes."},
        {"label": "Measured on the generated sprite",
         "value": "Figure reading at 3:1 or better against the wall: 6.3% without the rim, 24.2% with it. The code-drawn character measures 9.1%."},
        {"label": "The same rule, twice",
         "value": "player.gd applies it to the fallback body; scripts/import_pose.py applies it to every generated pose. An edit to a generated asset, declared in ASSET-LOG."},
        {"label": "Also restored",
         "value": "The visor. At a 28 px figure height the slit averages into the helm and snaps to plate: 0 visor pixels in seven of the first eight imports. 6-9 px restored per pose."}],
    cues=[{"at": 3.0, "line": 318, "label": "grown one way only"},
          {"at": 12.0, "line": 313, "label": "x is forward, so it mirrors"},
          {"at": 19.0, "line": 322, "label": "polygons translate, not expand"}],
    secs=27,
    narration=
        "The character is navy armour on a dark wall - one point six to one. Something "
        "has to break the silhouette. The first attempt grew a one pixel rim on all "
        "four sides, and that costs a part two pixels of width, so a three pixel arm "
        "keeps one pixel of armour. Rendered, the limbs were grey pipes. So the rim "
        "stopped being an outline: one pixel toward the back and one up, which costs "
        "nothing, and because x is measured forward it mirrors with the body - a light "
        "source behaves that way and an outline does not.",
    role="C2 CODE. The directional rim verbatim from player.gd. Paired with B05.",
    show=[{"at": "0.04", "event": "the excerpt and the four notes are framed"},
          {"at": "0.12", "event": "line 318 highlights - the one-way growth"},
          {"at": "0.45", "event": "line 313 highlights - x is forward"},
          {"at": "0.70", "event": "line 322 highlights - the polygon case"}]))

beats.append({
    "beat_id": "B05", "act": "RESULT",
    "role_note": "C2 RESULT. The importer's own acceptance strip for p1-idle: on the "
                 "dungeon wall, as a silhouette, on the lit platform edge, and its "
                 "silhouette. Written by scripts/import_pose.py, not redrawn.",
    "narration_text":
        "This is what the importer writes for every pose: the sprite on the dungeon "
        "wall, the same sprite as a solid silhouette, then both again on the torchlit "
        "platform edge. Six point three per cent of the figure read against that wall "
        "before the rim. Twenty four point two after. The code-drawn character it "
        "replaced measures nine point one on the same test.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 21,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "asset-preview",
             "show": [{"at": "0.05", "event": "the four-panel strip is framed"},
                      {"at": "0.30", "event": "the two contrast numbers land"},
                      {"at": "0.72", "event": "the 9.1% comparison lands"}],
             "evidence_media": "media/B05-poses.png",
             "remotion": {"pattern": "GodotDevWorkbench", "props": {
                 "mode": "asset", "title": "Acceptance strip, written by the importer",
                 "project": PROJECT,
                 "path": "build/poses/p1-idle-checks.png",
                 "source": "scripts/import_pose.py",
                 "code": "", "startLine": 1,
                 "image": "B05-poses.png",
                 "imageLabel": "on wall | silhouette | on lit edge | silhouette",
                 "notes": [], "cues": [], "durationSeconds": 21}}}})

# ------------------------------------------------- C3 the trap -> take t
beats.append(code_beat(
    "B06", *EX["B06"][:1], EX["B06"][1], EX["B06"][2],
    title="The warning fires on the arming tick",
    notes=[
        {"label": "Why not on the damage",
         "value": "Hung off the contact it is a death sound arriving after the information is useless - and it would still pass a test that only asked whether a sound played when the trap killed you."},
        {"label": "Recorded",
         "value": "Warning at tick 24 with the player at x 1064.6 against a trigger at 1064. Death at tick 59. Lead 35 ticks, about 0.58 s, against a 15-tick rise."},
        {"label": "The sound was specified first",
         "value": "CONCEPT revision 1.1 predicted on 2026-10-01 that a 124 bpm bed would mask it, and called for a moving pitch - which percussion does not have. 420 to 2100 Hz, inharmonic partials, amplitude rising."},
        {"label": "Declared",
         "value": "That effect is synthesised, not generated. A placeholder."}],
    cues=[{"at": 3.0, "line": 276, "label": "the trigger gate"},
          {"at": 10.0, "line": 284, "label": "the tick trap_risen leaves 0"},
          {"at": 18.0, "line": 288, "label": "the spike moves by its rise offset"}],
    secs=25,
    narration=
        "A trap arms when the player crosses its trigger, and the spike rises over "
        "fifteen ticks. The sound fires on the tick that counter leaves zero - the "
        "arming, not the contact. That distinction is the whole fairness argument, "
        "because a sound hung off the damage is a death sound, arriving after the "
        "information is useless, and it would still pass a check that only asked "
        "whether something played when the trap killed you.",
    role="C3 CODE. advance_traps() verbatim from session.gd. Paired with B07.",
    show=[{"at": "0.05", "event": "the excerpt is framed with four notes"},
          {"at": "0.12", "event": "line 276 highlights - the trigger comparison"},
          {"at": "0.40", "event": "line 284 highlights - trap_risen[i] == 0"},
          {"at": "0.72", "event": "line 288 highlights - the rise offset"}]))

beats.append(footage_beat(
    "B07", "take-t", [6.20, 8.88], 20,
    narration=
        "Watch the floor. The trigger is at one thousand and sixty four, the spike "
        "starts at one thousand one hundred and sixty, and the warning you just heard "
        "fired thirty five ticks before the hit - a little over half a second. The "
        "capture driver read that number out of the sound log on its own, and the test "
        "suite reports the same thirty five from a different path. The pose on the "
        "floor afterwards is the one the storyboard asked for.",
    role="C3 RESULT. take-t, the arming at t=6.800 x=1064.9, the death at t=7.383, "
         "and the prone pose held through the 0.55 s retry. The 35-tick lead is in "
         "the input log and in test_game.gd independently.",
    show=[{"at": "0.08", "event": "crossing the trigger - the spike begins to rise"},
          {"at": "0.30", "event": "the spike is fully up, still ahead of him"},
          {"at": "0.46", "event": "contact - the prone pose, wider than it is tall"},
          {"at": "0.70", "event": "the reason panel and the reaction"},
          {"at": "0.90", "event": "respawn at the start"}]))

# ------------------------------------------------- C4 the music guard
beats.append(code_beat(
    "B08", *EX["B08"][:1], EX["B08"][1], EX["B08"][2],
    title="One if, because this runs on every death",
    notes=[
        {"label": "The failure it prevents",
         "value": "restart_attempt() runs on every death. A naive play() restarts a 16-bar loop at bar 1 every 0.55 s, which is worse than silence."},
        {"label": "The bug inside the fix",
         "value": "AudioStreamPlayer.playing reports FALSE while stream_paused is true. So 'if not playing' was right for an ordinary death and wrong for pause-then-R: the track jumped to bar 1."},
        {"label": "How it was found",
         "value": "By printing what the engine reports in each state before writing the assertions. The code reads correctly; only the engine's own answer showed it."},
        {"label": "Recorded",
         "value": "a-retry-does-not-restart-the-track: position 0.467 s before, 0.557 s after. It went forward."}],
    cues=[{"at": 4.0, "line": 604, "label": "guarded, not unconditional"},
          {"at": 11.0, "line": 605, "label": "playing OR stream_paused"},
          {"at": 18.0, "line": 611, "label": "play() only on a cold start"}],
    secs=25,
    narration=
        "This function runs on every single death. Call play here and a sixteen bar "
        "loop restarts at bar one every half second, which is worse than silence - so "
        "it resumes instead. And the guard was still wrong. Playing reports false "
        "while a stream is paused, so testing playing alone was correct for an "
        "ordinary death and wrong for pause then retry, where the track jumped back to "
        "the top. I found that by printing what the engine actually reports in each "
        "state, before writing the assertion. The code reads correctly.",
    role="C4 CODE. The music guard verbatim from session.gd. Paired with B09.",
    show=[{"at": "0.05", "event": "the excerpt is framed with four notes"},
          {"at": "0.16", "event": "line 604 highlights - the guard"},
          {"at": "0.44", "event": "line 605 highlights - playing or stream_paused"},
          {"at": "0.72", "event": "line 611 highlights - the cold start"}]))

beats.append({
    "beat_id": "B09", "act": "RESULT",
    "role_note": "C4 RESULT. Recorded suite output, not a re-run claim. Two checks: "
                 "the ordinary retry and the pause-then-retry regression.",
    "narration_text":
        "Both of those are checks now. An ordinary retry leaves the playhead at half a "
        "second and moving. Pause, then retry, and it resumes instead of restarting - "
        "that one exists because it did not, once.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 15,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "output-lines",
             "show": [{"at": "0.08", "event": "the first recorded line lands"},
                      {"at": "0.45", "event": "the regression check lands"},
                      {"at": "0.80", "event": "the suite total lands"}],
             "remotion": {"pattern": "GodotDevWorkbench", "props": {
                 "mode": "code", "title": "Recorded output - tests/test_game.gd",
                 "project": PROJECT, "path": "godot/tests/test_game.gd  (recorded run)",
                 "source": "godot/tests/test_game.gd",
                 "code": "a-retry-does-not-restart-the-track\n"
                         "  before 0.467 s   after 0.557 s   went_backwards false\n"
                         "\n"
                         "retry-while-paused-resumes-rather-than-restarts\n"
                         "  at_pause 0.664 s   after_retry 0.755 s   stream_paused false\n"
                         "\n"
                         "WALKER TESTS: 99 checks / 0 failures",
                 "startLine": 1, "codeFontSize": 26,
                 "inspectorLabel": "Source notes - not Inspector values",
                 "notes": [{"label": "What this is",
                            "value": "Output recorded from a headless run, quoted. Not a live terminal and not a re-run inside the film."}],
                 "cues": [], "durationSeconds": 15}}}})

# ------------------------------------------------- C5 the blade
beats.append(code_beat(
    "B10", *EX["B10"][:1], EX["B10"][1], EX["B10"][2],
    title="The blade is not in the sprites, on purpose",
    notes=[
        {"label": "Three numbers, two consumers",
         "value": "ATTACK_PIVOT, attack_angle() and attack_reach drive both this drawing and the kill hitbox. The poses were prompted 'empty hand, NO weapon' to keep it that way."},
        {"label": "What baking it in would cost",
         "value": "The picture would stop tracking the hitbox the moment anyone touched the tuning - and nothing would report it. Both hitbox checks would still pass, because they measure the hitbox against the numbers, not against the picture."},
        {"label": "Measured",
         "value": "attack-hitbox-on-the-blade: 9 active ticks sampled each facing, worst endpoint error 3.8e-6 px right and 3.9e-6 px left."},
        {"label": "The honest cost",
         "value": "In a film about generated art, the character's most characteristic object is not generated."}],
    cues=[{"at": 4.0, "line": 678, "label": "the pivot the hitbox uses"},
          {"at": 10.0, "line": 680, "label": "the wedge only while it can kill"},
          {"at": 17.0, "line": 689, "label": "the blade itself"}],
    secs=24,
    narration=
        "The sprites carry the body, the scarf, the rim and the visor. They do not "
        "carry the blade. This function draws it from the same three numbers the kill "
        "hitbox is built from, and the bright wedge only appears while the swing can "
        "actually kill. Bake a blade into a sprite and it stops tracking that hitbox "
        "the moment anyone changes the tuning - and nothing reports it, because both "
        "hitbox checks measure the hitbox against the numbers, not against the "
        "picture.",
    role="C5 CODE. _draw_swing() verbatim from player.gd. Paired with B11.",
    show=[{"at": "0.05", "event": "the excerpt is framed with four notes"},
          {"at": "0.17", "event": "line 678 highlights - ATTACK_PIVOT"},
          {"at": "0.42", "event": "line 680 highlights - phase >= 2"},
          {"at": "0.71", "event": "line 689 highlights - the bar from a to b"}]))

beats.append(footage_beat(
    "B11", "take-p", [3.28, 4.32], 19,
    narration=
        "There it is at sixty frames a second: the wind-up pose, then the live window "
        "with the bright arc, and the blade leaving the hand the sprite is holding out. "
        "Nine active ticks, sampled both facings, and the worst disagreement between "
        "where the blade is drawn and where the hitbox sits is under four millionths of "
        "a pixel.",
    role="C5 RESULT. take-p's swing. The generated windup and live poses with the "
         "code-drawn blade over them, from the same pivot the hitbox uses.",
    show=[{"at": "0.10", "event": "windup - arm back, no sword in the sprite"},
          {"at": "0.34", "event": "the live window - the arc wedge appears"},
          {"at": "0.60", "event": "the blade sweeps down and forward"},
          {"at": "0.85", "event": "recovery, and back to idle"}]))

# ---------------------------------------------------------------- verdict
beats.append({
    "beat_id": "B12", "act": "VERDICT",
    "role_note": "WALKER BOOKEND 3/4. Separates implemented work, limitations and "
                 "human judgment. The placeholder sound effects and the missing seed "
                 "are stated here, not buried.",
    "narration_text":
        "So. Generated and in the game: one music loop and nine character images, each "
        "pose bound to a state the engine already names. Not generated, and I am not "
        "going to imply otherwise: all four sound effects, the dungeon, the enemies, "
        "the traps and the blade. Neither generator exposed a seed, so both reproduce "
        "as a request and not as an output - and that broke a rule this project had "
        "written down for itself. The test suite is a hundred and thirteen checks with "
        "no failures, and it asserts nothing at all about what the character looks "
        "like. Two real art bugs passed all of them.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 34,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "verdict-columns",
             "show": [{"at": "0.05", "event": "the artifact card rules on"},
                      {"at": "0.18", "event": "the generated lines fill"},
                      {"at": "0.48", "event": "the not-generated lines fill, greyed"},
                      {"at": "0.74", "event": "the seed line lands"},
                      {"at": "0.88", "event": "the open question closes the card"}],
             "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
                 "artifactTitle": "Verdict",
                 "artifactHeading": "Generated, not generated, and not checked",
                 "artifactLines": [
                     "Generated: 1 music loop, 16 bars, measured at 124.018 BPM.",
                     "Generated: 9 character images - 1 reference, 8 poses.",
                     "Generated art edits, declared: directional rim, visor restored.",
                     "NOT generated: all four sound effects. Synthesised placeholders.",
                     "NOT generated: dungeon, HUD, enemies, traps, and the blade.",
                     "No seed from either generator - request reproduces, output does not.",
                     "113 automated checks, 0 failures - and none of them sees the art.",
                     "Still open: two art bugs passed all 113. A human had to look."],
                 "brandLabel": "@NikBearBrown"}}}})

# ---------------------------------------------------------------- your turn
beats.append({
    "beat_id": "B13", "act": "TURN",
    "role_note": "WALKER BOOKEND 4/4. Reads a usable Walker prompt aloud and invites "
                 "ONE bounded change plus a prediction and the check that settles it. "
                 "Liam signs off here, not on the outro card.",
    "narration_text":
        "Your turn. Here is the prompt, and here is the change. Add the ninth pose - "
        "attack recovery - and wire it to phase three. Before you run it, predict "
        "this: recovery is three ticks, fifty milliseconds, so will you see it at all? "
        "Then run the pose key check and look at the contact sheet, because the suite "
        "will pass either way. That is the lesson, and it was mine before it was "
        "yours. This has been Liam, in for Bear.",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 27,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "turn-card",
             "show": [{"at": "0.06", "event": "the prompt card types on"},
                      {"at": "0.42", "event": "the one change lands"},
                      {"at": "0.62", "event": "the prediction lands"},
                      {"at": "0.82", "event": "the check that settles it lands"}],
             "remotion": {"pattern": "ClaudeYourTurn", "props": {
                 "heading": "Your Turn",
                 "prompt": "Please use Walker to add one more pose to my Godot "
                           "character: attack recovery, keyed to attack_phase() == 3, "
                           "using the same importer and the same eight-colour palette.",
                 "change": "One change: generate CHAR-P10 and wire 'recovery' into pose_key().",
                 "prediction": "Predict first: recovery lasts 3 ticks - 50 ms. Will you see it?",
                 "check": "Then: pose-key-matches-the-state-it-claims, and LOOK at the contact sheet.",
                 "brandLabel": "@NikBearBrown"}}}})

# ---------------------------------------------------------------- outro
beats.append({
    "beat_id": "B14", "act": "OUTRO",
    "role_note": "LOCKED ClaudeTitleOutro. Exact title, @NikBearBrown, one "
                 "slug-seeded mascot, no subline. No narration, no game SFX, no "
                 "themed voice on the card. Existing stock jingle only.",
    "narration_text": "",
    "voice": "am_onyx", "engine": "kokoro", "estimated_duration_s": 5,
    "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
             "motion": "title-outro",
             "show": [{"at": "0.10", "event": "the title card rules on"},
                      {"at": "0.55", "event": "the mascot settles"}],
             "remotion": {"pattern": "ClaudeTitleOutro", "props": {
                 "title": TITLE, "channel": "@NikBearBrown", "slug": SLUG}}}})

metadata = {
    "title": TITLE, "slug": SLUG,
    "topic": "WALKER - GODOT GAMEDEV TEARDOWN",
    "kind": "gamedev", "playlist": "Brutalist", "brand": "claude-liam",
    "audience": "Course reviewers and Brutalist fellows reading a Godot asset-generation pass",
    "register": "Teardown", "engine": "kokoro", "voice": "am_onyx",
    "voice_kokoro": "am_onyx", "palette": "claude", "style_preset": "claude",
    "ground": "#FAF9F5", "aspect_ratio": "16:9", "fit": "contain",
    "captions": False, "channel_title": "@NikBearBrown", "channel": "@NikBearBrown",
    "folderLabel": "@NikBearBrown", "greeting": "Sawubona, Liam",
    "greeting_note": "hello lexicon: Sawubona (Zulu), one word, the Liam persona "
                     "budget. Wagwan is Bear's alone and is not used.",
    "mode": "walker",
    "teaching_contract": "code-then-result-v1",
    "game": GAME,
}

io.open(os.path.join(REEL, "beat_sheet.json"), "w", encoding="utf-8", newline="\n").write(
    json.dumps({"metadata": metadata, "beats": beats}, indent=1, ensure_ascii=False) + "\n")
print("beat_sheet.json: %d beats, %.0f s estimated" % (
    len(beats), sum(b["estimated_duration_s"] for b in beats)))
for b in beats:
    print("  %-4s %-8s %5.1fs  %s" % (
        b["beat_id"], b["act"], b["estimated_duration_s"],
        b["shot"]["remotion"]["pattern"] if "remotion" in b["shot"] else
        "FOOTAGE " + b["shot"]["capture"]))
