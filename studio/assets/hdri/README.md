# Environment maps

Photographed environments for the engine's `sky.kind: "hdri"` (`studio/engine/lights.py`), each 1024 x 512, from
[Poly Haven](https://polyhaven.com), released under CC0 (public domain): no attribution needed, any use allowed.
Fetched from the copies in [pmndrs/drei-assets](https://github.com/pmndrs/drei-assets/tree/master/hdri), the only
mirror this environment's network reaches:

| file | Poly Haven asset | what it is |
|---|---|---|
| `studio_small_03_1k.hdr` | Studio Small 03 | a small photo studio with softboxes |
| `lebombo_1k.hdr` | Lebombo | a sunlit apartment with large windows |
| `st_fagans_interior_1k.hdr` | St Fagans Interior | a museum interior with windows |
| `empty_warehouse_01_1k.hdr` | Empty Warehouse 01 | an empty warehouse with skylights |

    for f in studio_small_03_1k lebombo_1k st_fagans_interior_1k empty_warehouse_01_1k; do
      curl -sS -o studio/assets/hdri/$f.hdr https://raw.githubusercontent.com/pmndrs/drei-assets/master/hdri/$f.hdr
    done

At 1k they are for light and reflections, not for a background the camera sees in focus: keep `sky.visible: false`
(the camera then sees `sky.backdrop`) or put them behind a set.
