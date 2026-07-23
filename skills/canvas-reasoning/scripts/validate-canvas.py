#!/usr/bin/env python3
"""Validate a JSON Canvas (.canvas) file.

Checks, in order:
  1. The file is well-formed JSON.
  2. Every node has a unique id (no duplicates).
  3. Every edge's fromNode / toNode references an existing node id (no dangling edges).
  4. No two node rectangles overlap (a group legally *containing* its children is allowed).

Exit status is 0 when clean, 1 when any check fails. Output is a human-readable
report. Run after writing or editing a canvas:

    python3 scripts/validate-canvas.py docs/canvases/<topic>.canvas
"""
import json
import sys


def _rect(n):
    x, y = n["x"], n["y"]
    return x, y, x + n["width"], y + n["height"]


def _contains(outer, inner):
    ox0, oy0, ox1, oy1 = _rect(outer)
    ix0, iy0, ix1, iy1 = _rect(inner)
    return ox0 <= ix0 and oy0 <= iy0 and ox1 >= ix1 and oy1 >= iy1


def _overlaps(a, b):
    ax0, ay0, ax1, ay1 = _rect(a)
    bx0, by0, bx1, by1 = _rect(b)
    # Touching edges (shared border) is fine; require real area of intersection.
    return ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1


def validate(path):
    errors = []
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return [f"file not found: {path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # 2. Duplicate ids
    seen = set()
    for n in nodes:
        nid = n.get("id")
        if nid in seen:
            errors.append(f"duplicate node id: {nid!r}")
        seen.add(nid)

    # 3. Dangling edges
    ids = {n.get("id") for n in nodes}
    for e in edges:
        for end in ("fromNode", "toNode"):
            ref = e.get(end)
            if ref not in ids:
                errors.append(
                    f"edge {e.get('id', '?')!r} {end} references missing node {ref!r}"
                )

    # 4. Overlaps. A group containing a node (either direction) is legal nesting,
    #    not an overlap. Everything else that intersects is flagged.
    placed = [n for n in nodes if all(k in n for k in ("x", "y", "width", "height"))]
    for i, a in enumerate(placed):
        for b in placed[i + 1 :]:
            if not _overlaps(a, b):
                continue
            a_is_group = a.get("type") == "group"
            b_is_group = b.get("type") == "group"
            if (a_is_group and _contains(a, b)) or (b_is_group and _contains(b, a)):
                continue
            errors.append(
                f"overlap: {a.get('id', '?')!r} and {b.get('id', '?')!r}"
            )

    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: python3 validate-canvas.py <path-to.canvas>", file=sys.stderr)
        return 2
    errors = validate(argv[1])
    if errors:
        print(f"FAIL ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — canvas is valid (JSON, unique ids, no dangling edges, no overlaps).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
