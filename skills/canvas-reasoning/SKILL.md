---
name: canvas-reasoning
description: Use during reasoning-heavy sessions (brainstorms, architecture reviews, debugging) when the user has accepted the Obsidian canvas as a visual companion. Draws code-architecture diagrams, data flows, and system-component relationships to a .canvas JSON file that the user opens in Obsidian. NOT for organizing brainstorm questions (those stay in chat).
---

# Canvas Reasoning

Dev tooling for collaborative spatial reasoning with the user via Obsidian-rendered JSON Canvas files. Pre-existing context:

- **Wire format:** [JSON Canvas spec](https://jsoncanvas.org/) — nodes + edges, four node types (`text`, `file`, `link`, `group`), simple enough to write by hand without a library.
- **Renderer:** Obsidian. User opens the repo as a vault. `.obsidian/` is gitignored; `.canvas` files themselves are checked in.

## When to invoke this skill

**Trigger conditions (any of):**

- A brainstorm session is starting that has 3+ candidate models or 5+ open questions.
- A debugging session has 2+ live hypotheses competing.
- A plan with non-trivial dependency structure between steps is being written.
- The user explicitly asks for a canvas, or has accepted one in a prior turn.

**Skip if:**

- The session is conversational/informational.
- The reasoning is fundamentally linear (one chain of thought, no branching).
- The user has not consented to the canvas — ask first; do not unilaterally start writing one.

## What goes ON the canvas

The canvas is for **content that is genuinely spatial** — a real graph where nodes have non-trivial relationships to *multiple* other nodes, not a list pretending to be a graph. The scope is broader than "code as it exists today" — any reasoning shape that's truly graph-shaped fits. Examples:

- **Code architecture diagrams** — current state, proposed state, side-by-side comparisons. Module boundaries, import edges, dispatch tables rendered as graphs.
- **Data flow / dependency graphs** — where does a value originate, where is it consumed, what transforms happen between.
- **System component relationships** — what talks to what, in which direction, via which interface.
- **User journeys and UX flows** — current and proposed flows through a product, with branching paths and decision points.
- **Logical decision chains / decision trees** — where each branch leads to a genuinely different downstream path, not just a different opinion about the same path.
- **Behavioral flows, sequence diagrams** — agent loops, request lifecycles, deploy sequences.
- **lsmcp exploration output when call structure matters** — "X is called from these 5 sites, here they are with their context."

This list isn't exhaustive — it's a sampler of the underlying shape. New use cases will surface; the test below decides. When a new category proves out, add it here.

## What does NOT go on the canvas

The failure mode this skill exists to avoid: drawing the **structure of the conversation itself** as nodes. That's a list pretending to be a graph and produces visual clutter without insight.

These belong in **chat**, not the canvas:

- **Brainstorm question structure.** "Q1, Q2, Q3 with three options each" is a tree with one parent and N children — a nested list, not a graph. Use chat + `AskUserQuestion` for multiple-choice.
- **Tradeoff lists / pros-cons matrices.** Tables in chat handle these fine; rendering them as connected nodes adds noise without adding clarity.
- **Conceptual A/B/C choices** where the difference between options is conceptual (two architectural philosophies) rather than structural (two genuinely different graphs). If the candidates would render as the same shape with different labels, it's not spatial.
- **The session's todo list.** Use `TodoWrite` for that.

**The graph-shape test:** the canvas earns its keep when nodes have real relationships to *multiple* other nodes — when the same node is pointed at from several places, when paths cross, when the shape of the graph is itself the information. If the structure is one parent → N children with no cross-edges, it's a list — use chat.

**The seeing-vs-reading test:** would the user understand this better by **seeing** it than reading it? If yes, canvas. If no, chat. This matches the [`superpowers:brainstorming` visual-companion](https://github.com/obra/superpowers/blob/main/skills/brainstorming/visual-companion.md) per-question test — same rule, different medium.

## Conventions

- **File location & naming:** canvases live in a dedicated canvases directory in the working repo — `docs/canvases/` by default (the folder is `.gitkeep`'d since it's often empty between active sessions). Adjust the location per project if `docs/` doesn't fit the repo's layout. Name as `<topic>.canvas`, or `<date>-<topic>.canvas` when chronological ordering matters. Canvases are checked in — they're part of the reasoning record. Layout-coordinate noise in diffs is accepted as a cost.
- **Coordinate system:** positive x = right, positive y = down. Coordinates are in pixels. Negative coordinates are fine — canvases commonly span negative space. What matters is a clear reading axis, not staying near the origin.
- **Node types — use all four, not just `text`:**
  - **`text`** — the default. Markdown content (see below).
  - **`group`** — a labeled bounding box around a cluster of nodes. Use it to enclose a panel ("current", "proposed", a subsystem boundary) so the grouping is visible, not just implied by proximity. A node belongs to a group purely by sitting inside its rectangle — there is no parent field. Edges may target a `group` by its `id` (e.g. "this decision feeds *that whole panel*"). Required fields: `id`, `type`, `x`, `y`, `width`, `height`; optional `label`, `color`.
  - **`file`** — a node that points at a **real file in the vault/repo** via a vault-relative `file` path. In Obsidian it renders the file live and is clickable. This is the high-value type for **code-architecture diagrams: the node literally *is* the source file** rather than a hand-copied label that goes stale. Optional `subpath` (e.g. `#SomeHeading`) targets a heading within the file.
  - **`link`** — a node wrapping an external URL (`url` field): the spec being implemented, a dashboard, a ticket. Keeps the reference anchored in the diagram instead of buried in chat.
- **Scaffolding — start most canvases with a title node and a legend node** (skip only for tiny throwaway sketches):
  - **Title node**, top-left: what this canvas is, the **reading axis** ("reads left→right: …"), and links to any sibling canvases. Orients anyone — including you, next session — in one glance.
  - **Legend node**: what each color means *on this canvas*. Color semantics are only self-documenting if you document them. Keep it next to the title.
- **Leaf density — many short leaves, not few long ones.** A leaf node is a label or one short claim, not a paragraph. Think of what a whiteboard diagram looks like: a box holds one word, or three at most. The Obsidian canvas affords slightly more — a leaf can carry one short sentence ("A rename breaks nothing", "Kind never changes") — but not more than that. When a fact has two parts (a claim and its consequence, a rule and its exception), that is **two leaves and an edge**, not one leaf with two sentences. Splitting is the default move whenever a node's text stops being readable at a glance:
  - **One claim per leaf.** If drafting a node's text requires "and" or a semicolon to fit everything in, split it — each half becomes its own leaf, connected by an edge or grouped together.
  - **A heading is optional on a leaf; body text almost never needs one.** Reserve `## Heading` + multi-line body for hub nodes (title, legend, a group's one summary card) — never for an ordinary leaf.
  - **This changes the leaf-count budget, not the total-content budget.** A subject that used to be three medium nodes with 4 lines each becomes ten to fifteen tiny one-line leaves, grouped under a labeled `group` panel with an end-state doc (or source file) linked once for anyone who wants the full prose. More nodes is the intended outcome, not a side effect to minimize.
  - **Worked reference:** `docs/canvases/overall-product-vision.canvas` in the Deckspace repo — each subject is a `group` of one-line leaves (`"Kind never changes"`, `"A rename breaks nothing"`), with a single `📄 [[end-state-doc.md]]` node per group for detail, and a distinct color reserved for still-open/downstream tickets. Use it as the density model, not the worked example below (which predates this convention and still shows the old, denser style).
- **Sizing — err larger than feels necessary.** Obsidian's default text-node size is small enough that almost any node with a heading + a few lines of content will show an internal scrollbar, and edge labels collide with adjacent nodes when gutters are tight. The cost of *too-large* is zoomable visual noise; the cost of *too-small* is unreadable nodes and overlapping labels. Default toward more space. Concrete starting points (use as **floors, not targets** — go bigger when in doubt):
  - **Tiny leaf nodes** (a label or one short sentence, no heading — the default per **Leaf density**): ~300 × 64
  - **Small text nodes** (one-line label + one-line detail): ~300 × 120
  - **Medium text nodes** (heading + 3–4 lines): ~460 × 180
  - **Large / central nodes** (heading + 5+ lines, hub component): ~510 × 330
  - **Horizontal gutter between columns:** ~120 px (so edge labels fit between nodes)
  - **Vertical gutter between same-column nodes:** ~80 px (where edge labels collide most)
  - **Gutter between independent groups:** ~200 px

  When iterating to relieve density on an existing canvas, **resize nodes and reposition gutters as separate decisions.** Uniformly scaling every `(x, y, w, h)` by the same factor changes the visual ratio not at all — it's just zoom. To actually open up a cramped canvas, the node-size multiplier and the gutter-size multiplier should differ (commonly: nodes 1.5×, gutters 2–3× on the previously-tight axes).
- **Layout — compute coordinates, don't eyeball them.** Hand-guessed positions are the #1 source of overlapping, unreadable canvases. Use a **column grid**: assign each node a `(column, row)`, then derive coordinates by accumulation rather than picking numbers.
  - **x of a column** = (starting x) + Σ(widths of all columns to its left) + (gutter × number of gutters crossed).
  - **y of a node** = (column's starting y) + Σ(heights of nodes above it in that column) + (gutter × gutters crossed).
  - *Worked micro-example* — three 460-wide columns, 120 gutter, starting x = 0: column 0 → x = 0; column 1 → x = 0 + 460 + 120 = 580; column 2 → x = 0 + (460 + 460) + (120 × 2) = 1160. Same arithmetic vertically with row heights + the 80 vertical gutter. Stack within a column the same way.
  - Reading axis sets the grid: left→right for flow/time (columns = stages), top→bottom for hierarchy (rows = levels), side-by-side for comparison (one column block per alternative). When in doubt, leave a column empty rather than crowd — empty space is free; overlap is not.
- **Colors** (built-in palette `"1"`–`"6"`): `1` red, `2` orange, `3` yellow, `4` green, `5` cyan, `6` purple. Hex strings also work. Use colors to convey state — e.g., `4` green for "decided/chosen", `1` red for "rejected", `5` cyan for "observed fact", no color for neutral commentary.
- **Edges:** `fromSide`/`toSide` are one of `top`, `right`, `bottom`, `left`. Always pick sides intentionally — auto-routing through wrong sides produces unreadable crossings. Use `label` to name the relationship (`"imports"`, `"depends on"`, `"asserted-equal-to"`).
- **Markdown in text nodes:** node `text` accepts markdown. A leaf stays to the one short sentence described in **Leaf density** above. Reserve `## Heading` + ~3–6 lines of prose for hub nodes (title, legend, a rare central/summary node) — if one of those needs more than 6 lines, split the overflow into linked leaves rather than growing the node.

## Worked example

A complete, valid canvas showing the conventions above in one piece — a title node, a legend node, a `group` panel enclosing two nodes (one of them a `file` node pointing at real source), a colored "proposed" node, and an edge that targets the group itself. Coordinates follow the column grid (left panel x≈0, right panel x≈620). Use it as the shape to start from, not content to copy.

```json
{
	"nodes":[
		{"id":"title","type":"text","text":"# Grid renderer — current vs proposed\n\n*Reads left→right. Left panel is what's in `main` today; right is option (a). Sibling: `grid-perf.canvas`.*","x":0,"y":0,"width":520,"height":150},
		{"id":"legend","type":"text","text":"## Legend\n- 🟩 green — chosen\n- 🟥 red — rejected\n- ⬜ none — neutral / current","x":560,"y":0,"width":360,"height":150},
		{"id":"panel-current","type":"group","label":"Current","x":0,"y":280,"width":520,"height":420},
		{"id":"dispatch","type":"text","text":"## Dispatch table\nO(n) scan on every cell write.","x":40,"y":360,"width":440,"height":140},
		{"id":"src-grid","type":"file","file":"src/renderer/grid.ts","x":40,"y":540,"width":440,"height":120},
		{"id":"proposed","type":"text","text":"## Proposed (a)\nIndex by region key → O(1) lookup.","x":620,"y":360,"width":300,"height":160,"color":"4"}
	],
	"edges":[
		{"id":"e-dispatch-src","fromNode":"dispatch","fromSide":"bottom","toNode":"src-grid","toSide":"top","label":"lives in"},
		{"id":"e-current-proposed","fromNode":"panel-current","fromSide":"right","toNode":"proposed","toSide":"left","label":"replace with"}
	]
}
```

The `src-grid` node renders the actual `src/renderer/grid.ts` file in Obsidian — clickable, never stale. Note `panel-current` is a group, and the `e-current-proposed` edge points the whole panel at the proposed node.

## Inline annotations (user ↔ Claude on the canvas)

The canvas doubles as an async-dialogue surface. When the user wants to ask about a specific node or relationship, they drop an annotation node and connect it by edge to the target. Conventions:

- **Prefix the node text with `{NOTE}`** (user → Claude) or `{Q}` (Claude → user). The prefix is the signal — scannable and unambiguous, unlikely to collide with content.
- **Connect by edge with no label** to the node(s) the annotation concerns. Connection itself carries "this is about that" — no edge label needed.
- **Multi-target = note about a relationship.** An annotation with edges to two nodes means "about how these two relate."
- **Replies default to chat.** Faster for both sides; canvas stays focused on structure rather than dialogue history. Drop a reply node only when the user explicitly asks for one.
- **Resolution:** once an annotation is answered, recolor it `4` (green / decided) to preserve the reasoning record. Delete only when the answer caused the surrounding canvas content to be edited (and the note is now redundant).
- **Trigger to re-read:** do NOT re-read the canvas every turn. Only when the user signals new annotations ("I left a note", "look at the canvas") or asks a question that's clearly spatially anchored. Otherwise assume the canvas is unchanged from your last read.
- **Finding annotations efficiently** when canvases grow large (roughly 30+ nodes): prefer `grep "{NOTE}"` on the canvas file, or `git diff <path/to/canvas>` when the user has just edited and not yet committed. Either is surgical — ~hundreds of bytes vs. several KB for a full re-read. For small canvases, just read the whole file; the optimization isn't worth the complexity.

## The loop

1. **Confirm consent** (only if not already given). The user must opt in to the canvas before you start one. Phrase: *"Some of this might be easier to show on an Obsidian canvas. Open one?"* Wait for an answer.
2. **Pick a canvas file path** under the project's canvases directory (`docs/canvases/` by default).
3. **Write the initial canvas** — usually a title node + the first architectural diagram needed.
4. **Validate** after writing or editing — run `python3 scripts/validate-canvas.py <path>` (script ships in this skill's `scripts/` dir). It catches malformed JSON, duplicate ids, edges pointing at missing nodes, and overlapping nodes. If `python3` isn't available, fall back to the checklist in **Validation** below.
5. **Tell the user what's on it** in one sentence (e.g., "Wrote the current vs proposed renderer architecture to `grid-system.canvas`. Left panel is what's in tree today; right panel is option (a)").
6. **Continue the conversation in chat.** Add to or edit the canvas when a new architectural artifact would clarify the next exchange — not on every turn.
7. **Re-read the canvas at session start** if returning to a session that already has one — it IS the conversation state.

## Validation

A `.canvas` file is hand-written JSON with referential integrity (edges name node ids) — easy to break in ways that render badly or not at all. After every write/edit, run the bundled validator:

```bash
python3 scripts/validate-canvas.py docs/canvases/<topic>.canvas
```

It exits non-zero with a readable report on: invalid JSON, duplicate node ids, edges referencing a missing `fromNode`/`toNode`, and overlapping node rectangles (a group legally containing its children is not flagged).

**Fallback checklist** (when `python3` is unavailable) — eyeball the file for:

- Parses as JSON (no trailing commas, balanced braces/brackets).
- Every node `id` is unique; edges only reference ids that exist.
- Each node has `x`, `y`, `width`, `height`; each edge has `fromNode`/`toNode` (and intentional `fromSide`/`toSide`).
- No two non-nested rectangles overlap — the hard one to see by eye, which is exactly why the script is preferred. With the column-grid layout (compute, don't guess) overlaps mostly can't happen in the first place.

## What to NOT do

- Don't translate the entire conversation onto the canvas. Most exchanges stay in chat.
- Don't add canvas nodes for questions you're about to ask the user — ask in chat.
- Don't pre-emptively scaffold dozens of nodes "in case we need them" — add as the conversation calls for them.
- Don't write a leaf node with more than one short sentence — that is two claims wearing one node; split it (see **Leaf density**).
- Don't lay out nodes randomly; intentional placement is the signal. Left-to-right for time/flow, top-to-bottom for hierarchy, side-by-side for comparison.
- Don't reuse a node's `id` across edits. Pick a stable `id` (short slug like `q1-current-renderer`) and edit the `text` field in place; don't keep renaming ids.

## Evolving this skill

The lists above ("What goes ON / NOT on the canvas") are starting points, not closed rules. As more sessions accumulate evidence — a new use case that worked, a convention that needed nailing down, a failure mode the tests above didn't catch — edit this skill directly. Treat it as a living artifact, not a fixed contract.

Particularly worth capturing here as the skill matures:

- New categories of content that proved genuinely spatial (add to the YES list with a concrete example).
- New failure modes where the canvas added noise instead of clarity (add to the NO list).
- Conventions that got nailed down by doing (file naming variations, color usage patterns, when to split one canvas into several).

## Status

This is **dev tooling**, single-developer, not a product surface. It exists to test whether spatial reasoning between user + Claude is worth the workflow cost. Skill is intentionally rough — written during Session 1 of the experiment. Iterate on it as more sessions accumulate evidence; do not over-engineer it before then.

## Related

- [`superpowers:brainstorming`](https://github.com/obra/superpowers/tree/main/skills/brainstorming) — the main reasoning skill this augments.
- [`superpowers:systematic-debugging`](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) — hypothesis-tree debugging that would benefit from canvas.
- [JSON Canvas spec](https://jsoncanvas.org/) — wire format.
- [kepano/obsidian-skills json-canvas SKILL.md](https://github.com/kepano/obsidian-skills/blob/main/skills/json-canvas/SKILL.md) — existing scaffolding worth pilfering if/when this skill matures.
