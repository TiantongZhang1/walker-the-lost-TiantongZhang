"""A3-SPIKE — the pop-up floor trap, built from four basic shapes.

Spec: CHANGE-BRIEF.md revision 3.0.0.
  size   1.50 x 0.50 x 1.00 m  (W x D x H, Blender X x Y x Z)
  origin centre of the underside of the base plate
  budget 4 shapes, <= 80 triangles
  colour teeth #d24e42, plate #2b2430

The tooth count is three because the game's own `spike_count()` is
`rect.size.x / SPIKE_PITCH` = 24 / 8 = 3. The size comes from the level file's
trap rect `[1160, 304, 24, 16]` at 16 px = 1 m.

This file is run two ways and is the same code both times:
  - through the MCP, as `exec(open(<this file>).read())`, so the saved script
    IS what Blender executed rather than a copy of it;
  - standalone, as the assignment's script-route fallback:
      blender -b --factory-startup --python-exit-code 1 \
          --python tools/blender/build_spike_trap.py

P5 from the brief is why colours are set on the Principled BSDF's Base Color
input and never on `material.diffuse_color`: the MCP server's own guidance
says diffuse_color only affects the viewport, so a colour set that way looks
right in Blender and exports grey.
"""

import bpy

W, D, H = 1.50, 0.50, 1.00     # metres, from the brief
PLATE_H = 0.15                 # base plate thickness
TOOTH_R = 0.22                 # tooth base radius; 0.44 across < 0.50 pitch
TOOTH_N = 3                    # = spike_count() in the 2D game
SEGMENTS = 8                   # cylinder/cone sides: a cone costs 2N-2 tris

TEETH_HEX = "d24e42"           # the 2D spike colour
PLATE_HEX = "2b2430"           # the dungeon mortar colour


def srgb_to_linear(c):
    """Blender's Base Color is linear; the game's hex values are sRGB."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(hex_str):
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


def flat_material(name, hex_str):
    """A flat-colour material: colour on the shader input, not diffuse_color."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    # Look the node up by TYPE, never by name: node names are localized.
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba(hex_str)
    bsdf.inputs["Roughness"].default_value = 0.8
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.2
    return mat


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def apply_transforms(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def build():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    clear_scene()

    teeth_mat = flat_material("A3_SpikeTeeth", TEETH_HEX)
    plate_mat = flat_material("A3_SpikePlate", PLATE_HEX)

    # 1. base plate — a cube, scaled, bottom face sitting on z = 0
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, PLATE_H / 2.0))
    plate = bpy.context.active_object
    plate.name = "SpikeTrap_Plate"
    plate.scale = (W / 2.0, D / 2.0, PLATE_H / 2.0)
    apply_transforms(plate)
    plate.data.materials.append(plate_mat)

    # 2-4. three teeth — cones standing on the plate, tips at z = H
    tooth_h = H - PLATE_H
    pitch = W / TOOTH_N                     # 0.50 m, the game's 8 px pitch
    for i in range(TOOTH_N):
        x = (i - (TOOTH_N - 1) / 2.0) * pitch
        bpy.ops.mesh.primitive_cone_add(
            vertices=SEGMENTS,
            radius1=TOOTH_R,
            radius2=0.0,
            depth=tooth_h,
            location=(x, 0.0, PLATE_H + tooth_h / 2.0),
        )
        tooth = bpy.context.active_object
        tooth.name = "SpikeTrap_Tooth_%d" % (i + 1)
        apply_transforms(tooth)
        tooth.data.materials.append(teeth_mat)

    return report()


def report():
    """Print what was built, so the numbers can be checked against the brief."""
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    tris = 0
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    for o in objs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
        for corner in o.bound_box:
            world = o.matrix_world @ __import__("mathutils").Vector(corner)
            for a in range(3):
                lo[a] = min(lo[a], world[a])
                hi[a] = max(hi[a], world[a])
    size = [hi[a] - lo[a] for a in range(3)]

    print("A3-SPIKE built")
    print("  objects   %d  (budget 4, course limit 6)" % len(objs))
    print("  triangles %d  (budget 80, course limit 500)" % tris)
    print("  size      %.3f x %.3f x %.3f m  (brief: 1.500 x 0.500 x 1.000)"
          % (size[0], size[1], size[2]))
    print("  bottom z  %+.4f m  (0 means the origin is at the base)" % lo[2])
    for o in objs:
        print("  - %-22s scale (%.3f, %.3f, %.3f)  rot (%.1f, %.1f, %.1f)"
              % (o.name, o.scale.x, o.scale.y, o.scale.z,
                 *[a * 57.2957795 for a in o.rotation_euler]))
    return tris, size, lo[2]


if __name__ == "__main__":
    build()
