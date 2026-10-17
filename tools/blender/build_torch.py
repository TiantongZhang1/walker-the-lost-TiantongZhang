"""A3-TORCH — the dungeon wall torch, built from four basic shapes.

Spec: CHANGE-BRIEF.md revision 3.0.0.
  size   0.22 x 0.22 x 0.70 m  (W x D x H, Blender X x Y x Z)
  origin centre of the underside of the handle
  budget 4 shapes, <= 160 triangles
  colour handle #3a2f26, flame #ff9a3c, flame core #ffe08a

The height comes from the 2D drawing: `_draw_torch()` draws the handle as
`draw_rect(cx-1, cy, 2, 10)`, and 10 px at 16 px = 1 m is 0.625 m; the flame
polygon adds 8 px above it, giving 0.70 m, which is 40 % of the player's
1.75 m. The widest part is the flame, and it sets the 0.22 m width.

Run two ways, the same code both times:
  - through the MCP as `exec(open(<this file>).read())`, so the saved script IS
    what Blender executed;
  - standalone, the assignment's script-route fallback:
      blender -b --factory-startup --python-exit-code 1 \
          --python tools/blender/build_torch.py

Colours go on the Principled BSDF's Base Color input, converted from the
game's sRGB hex to linear. Verified on A3-SPIKE: Blender stores linear, glTF
carries linear, and Godot converts back to sRGB on import, so
`albedo_color.to_html()` in Godot comes out as the original hex exactly.
Setting the raw sRGB value instead would arrive washed out (#d24e42 would read
as #ea968b).
"""

import bpy

W, D, H = 0.22, 0.22, 0.70     # metres, from the brief
SEGMENTS = 8                   # a cylinder costs 4N-4 tris, a cone 2N-2

HANDLE_R, HANDLE_H = 0.030, 0.46
COLLAR_R, COLLAR_H = 0.055, 0.05
FLAME_R, FLAME_H = 0.110, 0.24   # 0.11 radius -> 0.22 across, the W above
CORE_R, CORE_H = 0.055, 0.15

HANDLE_HEX = "3a2f26"
FLAME_HEX = "ff9a3c"
CORE_HEX = "ffe08a"


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(hex_str):
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


def flat_material(name, hex_str, emission_hex=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    # By TYPE, never by name: node names are localized and this Blender is zh.
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba(hex_str)
    bsdf.inputs["Roughness"].default_value = 0.8
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.2
    if emission_hex and "Emission Color" in bsdf.inputs:
        # The flame is the only light-looking thing in the asset; glTF carries
        # emissiveFactor, so Godot shows it lit without a lamp.
        bsdf.inputs["Emission Color"].default_value = rgba(emission_hex)
        bsdf.inputs["Emission Strength"].default_value = 1.0
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


def cylinder(name, radius, depth, z_centre, mat):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEGMENTS, radius=radius, depth=depth, location=(0.0, 0.0, z_centre))
    obj = bpy.context.active_object
    obj.name = name
    apply_transforms(obj)
    obj.data.materials.append(mat)
    return obj


def cone(name, radius, depth, z_centre, mat):
    bpy.ops.mesh.primitive_cone_add(
        vertices=SEGMENTS, radius1=radius, radius2=0.0, depth=depth,
        location=(0.0, 0.0, z_centre))
    obj = bpy.context.active_object
    obj.name = name
    apply_transforms(obj)
    obj.data.materials.append(mat)
    return obj


def build():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    clear_scene()

    wood = flat_material("A3_TorchHandle", HANDLE_HEX)
    flame = flat_material("A3_TorchFlame", FLAME_HEX, emission_hex=FLAME_HEX)
    core = flat_material("A3_TorchCore", CORE_HEX, emission_hex=CORE_HEX)

    # 1. handle — base on z = 0 so the origin sits at the underside
    cylinder("Torch_Handle", HANDLE_R, HANDLE_H, HANDLE_H / 2.0, wood)

    # 2. collar — the wider band the flame sits in, overlapping the handle top
    collar_z = HANDLE_H - COLLAR_H / 2.0
    cylinder("Torch_Collar", COLLAR_R, COLLAR_H, collar_z, wood)

    # 3. flame — tip at exactly H, so the asset is 0.70 m tall by construction
    flame_base = H - FLAME_H
    cone("Torch_Flame", FLAME_R, FLAME_H, flame_base + FLAME_H / 2.0, flame)

    # 4. flame core — a brighter inner cone, sitting inside the outer one
    core_base = flame_base + 0.02
    cone("Torch_FlameCore", CORE_R, CORE_H, core_base + CORE_H / 2.0, core)

    return report()


def report():
    import mathutils
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    tris = 0
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for o in objs:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
        for corner in o.bound_box:
            world = o.matrix_world @ mathutils.Vector(corner)
            for a in range(3):
                lo[a] = min(lo[a], world[a])
                hi[a] = max(hi[a], world[a])
    size = [hi[a] - lo[a] for a in range(3)]

    print("A3-TORCH built")
    print("  objects   %d  (budget 4, course limit 6)" % len(objs))
    print("  triangles %d  (budget 160, course limit 500)" % tris)
    print("  size      %.3f x %.3f x %.3f m  (brief: 0.220 x 0.220 x 0.700)"
          % (size[0], size[1], size[2]))
    print("  bottom z  %+.4f m  (0 means the origin is at the base)" % lo[2])
    for o in objs:
        print("  - %-20s scale (%.3f, %.3f, %.3f)  rot (%.1f, %.1f, %.1f)"
              % (o.name, o.scale.x, o.scale.y, o.scale.z,
                 *[a * 57.2957795 for a in o.rotation_euler]))
    return tris, size, lo[2]


if __name__ == "__main__":
    build()
