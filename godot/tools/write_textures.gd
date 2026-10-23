extends SceneTree
## Writes every texture Assignment 5 part 3 needs, from code.
##
##   godot --headless --path godot --script res://tools/write_textures.gd
##
## Assignment 5 requires the 3x1 hint-experiment PNG to be written by a
## committed GDScript. The other two are written here as well because
## CHANGE-BRIEF.md's material plan chose code-written textures over sourced
## ones: the provenance is then the source, with no licence to track, and the
## assignment allows it explicitly ("Textures written by code are fine; show
## the code").
##
## No normal map is written. A code-written normal map would have to pass the
## curl check in Step 3, and the calibration pair that check needs is a Poly
## Haven _nor_gl/_nor_dx download. The brief says so and says what it forgoes.

const OUT := "res://assets/textures/"

## The hint experiment's three bands, as 8-bit values. CHANGE-BRIEF.md section 7
## predicts 64/128/192 unchanged through the source_color sampler and
## 137/188/225 through the one without it.
const HINT_BANDS := [64, 128, 192]


func _init() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_write("hint_bands.png", _hint_bands())
	_write("stone_albedo.png", _stone_albedo())
	_write("wetness_mask.png", _wetness_mask())
	_verify()
	quit(0)


func _write(name: String, img: Image) -> void:
	var path := OUT + name
	var err := img.save_png(path)
	print("  %-20s %dx%d  %s  -> %s" % [
		name, img.get_width(), img.get_height(),
		"RGB8" if img.get_format() == Image.FORMAT_RGB8 else str(img.get_format()),
		"OK" if err == OK else "ERROR " + str(err)])


## 3 x 1, one texel per band. Written as RGB8 with no alpha so nothing can
## premultiply the values on the way in or out.
func _hint_bands() -> Image:
	var img := Image.create(3, 1, false, Image.FORMAT_RGB8)
	for i in HINT_BANDS.size():
		var v := float(HINT_BANDS[i]) / 255.0
		img.set_pixel(i, 0, Color(v, v, v))
	return img


## Dungeon stone. sRGB COLOUR: this one is sampled WITH source_color.
## Deterministic, so a reviewer who reruns the script gets the same file.
func _stone_albedo() -> Image:
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261023
	var size := 256
	var img := Image.create(size, size, true, Image.FORMAT_RGB8)
	var base := Color8(0x3A, 0x3E, 0x44)
	var mortar := Color8(0x23, 0x26, 0x2B)
	var brick_h := 32
	var brick_w := 64
	for y in size:
		var row := y / brick_h
		var offset := (row % 2) * (brick_w / 2)
		for x in size:
			var bx := (x + offset) % brick_w
			var by := y % brick_h
			var is_mortar := bx < 3 or by < 3
			var c := mortar if is_mortar else base
			# Per-texel grain, so roughness and the mask have something to bite.
			var n := rng.randf_range(-0.045, 0.045)
			img.set_pixel(x, y, Color(
				clampf(c.r + n, 0.0, 1.0),
				clampf(c.g + n, 0.0, 1.0),
				clampf(c.b + n, 0.0, 1.0)))
	return img


## Where water pools. DATA: sampled WITHOUT source_color, so these numbers mean
## "how submerged", not "how bright". Low in the mortar channels, which is
## where water would actually sit, plus smooth blobs for standing puddles.
func _wetness_mask() -> Image:
	var size := 256
	var noise := FastNoiseLite.new()
	noise.seed = 20261023
	noise.frequency = 0.012
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	var img := Image.create(size, size, true, Image.FORMAT_RGB8)
	var brick_h := 32
	var brick_w := 64
	for y in size:
		var row := y / brick_h
		var offset := (row % 2) * (brick_w / 2)
		for x in size:
			# 0..1 from the noise field
			var v := (noise.get_noise_2d(float(x), float(y)) + 1.0) * 0.5
			# Mortar lines hold water: push them toward 1.
			var bx := (x + offset) % brick_w
			var by := y % brick_h
			if bx < 3 or by < 3:
				v = minf(1.0, v + 0.45)
			v = clampf(v, 0.0, 1.0)
			img.set_pixel(x, y, Color(v, v, v))
	return img


## Read the hint PNG back and print the stored values, so the prediction in
## CHANGE-BRIEF.md section 7 is checked against the actual file rather than
## against what this script intended to write.
func _verify() -> void:
	var img := Image.load_from_file(ProjectSettings.globalize_path(OUT + "hint_bands.png"))
	print("\n  hint_bands.png stored values, read back from the file:")
	var ok := true
	for i in HINT_BANDS.size():
		var got := int(round(img.get_pixel(i, 0).r * 255.0))
		var want: int = HINT_BANDS[i]
		if got != want:
			ok = false
		print("    texel %d: %3d  (brief section 7 predicts %3d)  %s"
			% [i, got, want, "OK" if got == want else "MISMATCH"])
	print("  ", "all three bands match the brief" if ok else "FILE DOES NOT MATCH THE BRIEF")
