# canvas-reasoning

A Claude Code plugin for **collaborative spatial reasoning**. During reasoning-heavy
sessions — brainstorms, architecture reviews, debugging — Claude draws architecture
diagrams, data flows, decision graphs, and dependency structures to a
[JSON Canvas](https://jsoncanvas.org/) `.canvas` file that you open in
[Obsidian](https://obsidian.md/). The canvas becomes a shared surface: Claude writes
structure, you drop inline annotations, and the reasoning record is checked into the repo.

It is **not** for organizing brainstorm questions or tradeoff tables — those stay in chat.
The canvas earns its place only when the content is genuinely graph-shaped (nodes with
real relationships to *multiple* other nodes). See the skill for the full "graph-shape"
and "seeing-vs-reading" tests.

This augments [`superpowers:brainstorming`](https://github.com/obra/superpowers) — same
reasoning discipline, different medium.

## What's in here

```
.claude-plugin/
  marketplace.json   # marketplace descriptor (lets the repo be added as a marketplace)
  plugin.json        # plugin manifest (points at ./skills/)
skills/
  canvas-reasoning/
    SKILL.md         # the skill itself
    scripts/
      validate-canvas.py  # post-write validator (JSON, ids, dangling edges, overlaps)
```

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [Obsidian](https://obsidian.md/) (the renderer — open the working repo as a vault).
  Any JSON Canvas renderer works; Obsidian is the one this skill is tuned for.

## Install

Add this repo as a marketplace, then install the plugin:

```bash
# from a GitHub remote
claude plugin marketplace add ckelly8/canvas-reasoning
claude plugin install canvas-reasoning@canvas-reasoning

# or from a local clone
claude plugin marketplace add /path/to/canvas-reasoning
claude plugin install canvas-reasoning@canvas-reasoning
```

`canvas-reasoning@canvas-reasoning` is `plugin-name@marketplace-name` — both happen to
be `canvas-reasoning` here.

## Usage

Once installed, the skill activates automatically when a session turns reasoning-heavy
(3+ candidate models, competing debug hypotheses, a dependency-structured plan), or when
you explicitly ask for a canvas. Claude confirms consent first, writes the canvas under
`docs/canvases/` (by default), validates it with the bundled
`scripts/validate-canvas.py`, and tells you what's on it. You open the file in Obsidian.

To leave Claude a note on the canvas, add a text node prefixed with `{NOTE}` and connect
it by an edge to the node(s) it concerns.

## Status

Early, single-developer dev tooling — an experiment in whether spatial reasoning between
user and Claude is worth the workflow cost. Intentionally rough; iterated as sessions
accumulate evidence. Version `0.2.0`.

## License

MIT — see [LICENSE](LICENSE).
