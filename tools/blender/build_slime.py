"""A3-SLIME — the ground enemy, built from three basic shapes.

Spec: CHANGE-BRIEF.md revision 3.0.0.
  size   1.375 x 1.375 x 1.00 m  (W x D x H, Blender X x Y x Z)
  origin centre of the underside
  budget 3 shapes, <= 120 triangles
  colour body #7ab648, eyes #17300d

Why a cut sphere and not a sphere sitting on the floor. `_draw_slime()` builds
its outline as `PI * i / steps` with `-sin(th) * high`, which is the UPPER half
of an ellipse: a dome with a flat bottom resting on the ground, finished with a
darker base band. A whole squashed ball balanced on one point would be a
different creature. So the icosphere is scaled to the dome's proportions,
bisected at z = 0, and the opening filled — three primitives, one cut, and the
base is flat by construction rather than by luck.

An icosphere at subdivision 1 is used rather than a UV sphere: 80 triangles for
a round shape where a default UV sphere would spend about 960, and the
assignment warns that a default sphere eats the budget.

Run two ways, the same code both times:
  - through the MCP as `exec(open(<this file>).read())`;
  - standalone, the script-route fallback:
      blender -b --factory-startup --python-exit-code 1 \
          --python tools/blender/build_slime.py
"""

import bmesh
import bpy

W, D, H = 1.375, 1.375, 1.00   # metres, from the brief
SUBDIV = 2                     # icosphere subdivisions; see brief revision 3.0.1
#   1 gives 80 triangles but a visibly pointed apex: an icosphere at that
#   level is a 20-sided solid, and the 2D slime is a smooth dome. Raised to
#   2 after looking at it. Still far inside the 500-triangle course limit.

EYE = 0.11                     # eye cube edge
EYE_X = 0.20                   # half the gap between the eyes
EYE_Z = 0.64                   # height up the dome
EYE_Y = -0.46                  # towards the front (-Y in Blender)

BODY_HEX = "7ab648"
EYE_HEX = "17300d"


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(hex_str):
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


def flat_material(name, hex_str):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = rgba(hex_str)
    bsdf.inputs["Roughness"].default_value = 0.65
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.35
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


def fit_to_size(obj, target_w, target_d, target_h):
    """Scale the mesh so its bounding box is exactly the brief's size.

    An icosphere at subdivision 1 is a faceted polyhedron, not a sphere: its
    vertices sit on the nominal radius but there is no vertex ring at z = 0,
    so after the cut the widest geometry is narrower than the semi-axis asked
    for. Built nominally at 1.375 m wide it measured 1.171 — 14.8 % under, and
    outside the brief's own +/-5 % tolerance in P2.

    Multiplying by a constant found from that one measurement would fit the
    code to the number. This measures the mesh after the cut and scales to the
    target, so the asset matches the brief whatever the primitive's faceting
    does, and changing SUBDIV later cannot silently reintroduce the error.
    """
    verts = obj.data.vertices
    lo = [min(v.co[a] for v in verts) for a in range(3)]
    hi = [max(v.co[a] for v in verts) for a in range(3)]
    have = [hi[a] - lo[a] for a in range(3)]
    want = (target_w, target_d, target_h)
    factor = [want[a] / have[a] if have[a] > 1e-9 else 1.0 for a in range(3)]
    for v in verts:
        for a in range(3):
            v.co[a] *= factor[a]
    obj.data.update()
    print("  fit: %.3f x %.3f x %.3f -> %.3f x %.3f x %.3f  (x%.4f, x%.4f, x%.4f)"
          % (have[0], have[1], have[2], want[0], want[1], want[2], *factor))


def cut_flat_bottom(obj):
    """Bisect at z = 0, drop everything below, and fill the opening."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(
        bm, geom=geom, dist=1e-6,
        plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 0.0, 1.0),
        clear_inner=True,        # remove the half below the plane
    )
    boundary = [e for e in bm.edges if e.is_boundary]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    clear_scene()

    body_mat = flat_material("A3_SlimeBody", BODY_HEX)
    eye_mat = flat_material("A3_SlimeEye", EYE_HEX)

    # 1. body — an icosphere scaled to the dome's semi-axes, then cut at z = 0.
    #    Semi-axes: W/2 and D/2 across, H tall, so the kept upper half is
    #    exactly H high and W wide.
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=SUBDIV, radius=1.0, location=(0.0, 0.0, 0.0))
    body = bpy.context.active_object
    body.name = "Slime_Body"
    body.scale = (W / 2.0, D / 2.0, H)
    apply_transforms(body)
    cut_flat_bottom(body)
    fit_to_size(body, W, D, H)
    body.data.materials.append(body_mat)

    # 2-3. eyes — two small cubes pressed into the front of the dome.
    #
    # The Y position is derived, not typed: the dome is an ellipsoid with
    # semi-axes D/2 across and H tall, so its front surface at height z sits at
    #     y = -(D/2) * sqrt(1 - (z/H)^2)
    # and the cube is sunk a quarter of its own edge into that surface. Typing
    # a constant here broke once already — fit_to_size() widens the body after
    # it is built, and eyes placed for the pre-fit width ended up inside it.
    import math
    front_y = (D / 2.0) * math.sqrt(max(0.0, 1.0 - (EYE_Z / H) ** 2))
    eye_y = -(front_y - EYE * 0.25)
    for i, sign in enumerate((-1.0, 1.0)):
        bpy.ops.mesh.primitive_cube_add(
            size=EYE, location=(sign * EYE_X, eye_y, EYE_Z))
        eye = bpy.context.active_object
        eye.name = "Slime_Eye_%d" % (i + 1)
        apply_transforms(eye)
        eye.data.materials.append(eye_mat)

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

    print("A3-SLIME built")
    print("  objects   %d  (budget 3, course limit 6)" % len(objs))
    print("  triangles %d  (budget 120, course limit 500)" % tris)
    print("  size      %.3f x %.3f x %.3f m  (brief: 1.375 x 1.375 x 1.000)"
          % (size[0], size[1], size[2]))
    print("  bottom z  %+.4f m  (0 means the origin is at the base)" % lo[2])
    for o in objs:
        print("  - %-18s scale (%.3f, %.3f, %.3f)  rot (%.1f, %.1f, %.1f)"
              % (o.name, o.scale.x, o.scale.y, o.scale.z,
                 *[a * 57.2957795 for a in o.rotation_euler]))
    return tris, size, lo[2]


if __name__ == "__main__":
    build()
