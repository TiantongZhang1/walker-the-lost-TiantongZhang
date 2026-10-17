"""Save the current Blender scene as a .blend source and export it as .glb.

Shared by all three A3 assets so the export settings are written once and
cannot drift between them.

Two settings are deliberate rather than defaults:

  export_format='GLB'
      The operator's default for this property is the EMPTY STRING, measured
      on this install (Blender 5.2.2, glTF add-on 5.2.40). The File > Export
      menu fills it in; calling the operator from Python does not, and without
      it you do not get a .glb. Found by reading the operator's RNA before
      exporting rather than by exporting and wondering.

  export_yup=True
      glTF is Y-up and Blender is Z-up. This is already the default here
      (measured, not assumed), but the brief's P1 predicts an asset arriving
      on its side, so the setting it depends on is stated rather than
      inherited.

export_apply=True is also passed. These assets carry no modifiers, so it
changes nothing today; it is here so that adding one later cannot silently
export the unmodified mesh.
"""

import os

import bpy


def save_and_export(blend_path, glb_path):
    for path in (blend_path, glb_path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("saved  .blend  %s" % blend_path)

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format="GLB",      # NOT the operator default; see the docstring
        export_yup=True,
        export_apply=True,
        use_selection=False,
        export_materials="EXPORT",
    )
    size = os.path.getsize(glb_path)
    print("wrote  .glb    %s  (%d bytes)" % (glb_path, size))
    return size
