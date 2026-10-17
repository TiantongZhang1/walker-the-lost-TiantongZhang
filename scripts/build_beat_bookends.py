#!/usr/bin/env python3
"""Replace the four invented-prop beats with the real components' shapes.

`./art scenes --check` rejected ClaudeHesitantWriter and ClaudeYourTurn - both
were names I made up - and ClaudeComposerAsk's real props are nothing like the
ones I guessed. The shapes below are read off Assignment 1's beat sheet, which
rendered.
"""
import base64, io, json, os

ROOT = r"D:\Graduate\2026Fall\7270\walker-ninja-TiantongZhang"
os.chdir(ROOT)
REEL = "youtube/claude-liam-walker-ninja-gamedev"
BS = os.path.join(REEL, "beat_sheet.json")
doc = json.load(io.open(BS, encoding="utf-8"))

b64 = base64.b64encode(open(os.path.join(REEL, "media/B05-poses.png"), "rb").read()).decode()
DATA_URI = "data:image/png;base64," + b64

PROJECT = "walker-ninja-TiantongZhang"
by_id = {b["beat_id"]: b for b in doc["beats"]}

# ---------------------------------------------------------------- B00
by_id["B00"]["shot"]["remotion"] = {"pattern": "ClaudeComposerAsk", "props": {
    "greeting": "Sawubona, Liam",
    "topic": "WALKER - GODOT GAMEDEV TEARDOWN",
    "segment": "Walker Ninja, Generated",
    "command": "Please use Walker to convert my game design document about a "
               "cyber-ninja in a torchlit dungeon - a second jump, one air dash, a "
               "sword on his back, spikes that pop out of the floor and enemies that "
               "patrol - into a playable Godot project, and then help me replace the "
               "code-drawn character with generated art without letting the blade and "
               "its hitbox come apart.",
    "runningText": "reconstructed prompt - illustrative, not a transcript",
    "output": [
        "1 music loop + 9 character images, generated",
        "8 poses bound to 8 states the engine already names",
        "the blade stays in code, on purpose"],
    "folderLabel": "@NikBearBrown",
    "modelLabel": "Claude Opus 5",
    "effortLabel": "High"}}

# ---------------------------------------------------------------- B01
by_id["B01"]["shot"]["remotion"] = {"pattern": "BrutalistHesitantWriter", "props": {
    "contextTitle": "What Assignment 2 generated",
    "text": "Walker generated my game.\nHere is what it actually generated.",
    "face": "serif", "fontSize": 92, "lineSpacing": 1.35, "align": "center",
    "triggerWords": "game", "replacementWords": "character",
    "mistakeRate": 0, "hesitateWithin": 0, "hesitateBetween": 6,
    "charMs": 28, "jitter": 15,
    "contextItems": [
        {"label": "Generated",
         "detail": "1 music loop, 16 bars - 9 character images, 1 reference + 8 poses"},
        {"label": "Unchanged",
         "detail": "3072 px level - the same 8 movement values - the 18x28 collider"},
        {"label": "NOT generated",
         "detail": "all 4 sound effects - the dungeon, enemies, traps - and the blade"}]}}

# ---------------------------------------------------------------- B05
by_id["B05"]["shot"]["remotion"]["props"].update({
    "title": "All eight, at the size the player sees them",
    "path": "godot/assets/poses/p1-idle.png ... p8-death.png",
    "image": DATA_URI,
    "imageLabel": "on the dungeon wall / as a silhouette / on the torchlit edge",
})
by_id["B05"]["narration_text"] = (
    "Here are all eight at the size the player actually sees them. Top row on the "
    "dungeon wall, middle row as solid silhouettes, bottom row on the torchlit "
    "platform edge. Six point three per cent of the figure read against that wall "
    "before the rim was added. Twenty four point two after. The code-drawn character "
    "it replaced measures nine point one on the same test - and the prone pose at the "
    "end is the only one in the game wider than it is tall.")
by_id["B05"]["estimated_duration_s"] = 24
by_id["B05"]["shot"]["remotion"]["props"]["durationSeconds"] = 24
by_id["B05"]["shot"]["evidence_media"] = "media/B05-poses.png"

# ---------------------------------------------------------------- B13
by_id["B13"]["shot"]["remotion"] = {"pattern": "ClaudeComposerAsk", "props": {
    "greeting": "Your turn, Liam",
    "topic": "WALKER - ONE MORE POSE",
    "segment": "Generate The Ninth",
    "command": "In walker-ninja, generate the ninth pose - attack recovery - from "
               "CHAR-REF-01, run it through scripts/import_pose.py, and wire "
               "'recovery' into pose_key() for attack_phase() == 3. Tell me whether "
               "you can see it before you change its length.",
    "runningText": "one pose - one prediction - one look",
    "output": [
        "predict first: recovery is 3 ticks, 50 ms",
        "pose-key-matches-the-state-it-claims will pass either way",
        "so LOOK at the contact sheet"],
    "folderLabel": "@NikBearBrown",
    "modelLabel": "Claude Opus 5",
    "effortLabel": "High"}}

doc["beats"] = [by_id[b["beat_id"]] for b in doc["beats"]]
io.open(BS, "w", encoding="utf-8", newline="\n").write(
    json.dumps(doc, indent=1, ensure_ascii=False) + "\n")

total = sum(b["estimated_duration_s"] for b in doc["beats"])
print("beat_sheet.json rewritten: %d beats, %.0f s (%d:%02d)" % (
    len(doc["beats"]), total, total // 60, total % 60))
for b in doc["beats"]:
    sh = b["shot"]
    pat = sh["remotion"]["pattern"] if "remotion" in sh else "FOOTAGE " + sh["capture"]
    print("  %-4s %-8s %5.1fs  %s" % (b["beat_id"], b["act"], b["estimated_duration_s"], pat))
