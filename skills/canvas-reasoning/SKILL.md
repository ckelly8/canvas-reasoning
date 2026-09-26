---
name: canvas-reasoning
description: Use during reasoning-heavy sessions (brainstorms, architecture reviews, debugging) when the user has accepted the Obsidian canvas as a visual companion, and whenever writing or editing any .canvas file. Draws code-architecture diagrams, data flows, and system-component relationships to a .canvas JSON file that the user opens in Obsidian. NOT for organizing brainstorm questions (those stay in chat).
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

## Nodes are labels

A text node says what a box on a whiteboard diagram says: **one to three words**. It may run to one short sentence — about eight words — when the claim needs a verb: "Kind never changes". That is the ceiling.

A text node is exactly one of:

- **a label** — a noun phrase: `Placement`, `Graph screen`, `leads to`;
- **a claim** — one short sentence: `A rename breaks nothing`;
- **a hub** — `## Name` plus at most one short line, for a node several edges point at.

More content means more nodes, never a longer node:

- A list inside a node → one leaf per item, stacked in a cluster.
- Two claims → two leaves. A node whose text needs "and" or a semicolon holds two claims; a claim and its consequence are two leaves and an edge.
- A heading over several leaves → a labelled `group` around them. Groups nest; a nested group is a sub-heading.
- Rationale and detail → the document that holds it, reached by a `file` node or a `[[link]]` leaf. The canvas shows the shape; the document holds the words.

The validator warns on any text node over 12 words outside heading lines (`title` and `legend` are exempt).

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
    - **Every legend entry MUST open with the matching color emoji circle** — `🔴 🟠 🟡 🟢 🔵 🟣`, and `⚪` for uncolored. Write `🔵 cyan — observed fact`, never `cyan — observed fact`. A legend that only *names* a color makes the reader translate a word back into the hue they are looking at, one entry at a time; the circle is the thing their eye is already matching against the nodes, so the mapping lands in one glance rather than a lookup. It also survives being read in a diff, a terminal, or a paste into chat — every context where the canvas colors themselves are invisible.
- **Sizing — by lines of text.** Obsidian's default card is 250 × 60. At 300 wide a line holds about 26 characters:
  - **Leaf, one line:** 300 × 64
  - **Leaf, two lines:** 300 × 96
  - **Hub** (`## Name` + one line): 300 × 76, plus 32 per wrapped line under the heading
  - **Title / legend:** as large as they need; they are scaffolding, not leaves

  A node that scrolls internally is too small — grow its height; never shrink its text.
- **Gutters follow the edges.** Stacked leaves in one cluster with no edges between them: ~24 px. Clusters side by side: ~60 px. Anywhere a labelled edge runs: ~120 px across, ~80 px down. Between groups: ~200 px. To open up a cramped canvas, change gutters and node sizes as separate decisions — scaling every `(x, y, w, h)` by one factor is only zoom.
- **Layout — compute coordinates, don't eyeball them.** Hand-guessed positions are the #1 source of overlapping, unreadable canvases. Use a **column grid**: assign each node a `(column, row)`, then derive coordinates by accumulation rather than picking numbers.
  - **x of a column** = (starting x) + Σ(widths of all columns to its left) + (gutter × number of gutters crossed).
  - **y of a node** = (column's starting y) + Σ(heights of nodes above it in that column) + (gutter × gutters crossed).
  - *Worked micro-example* — three 460-wide columns, 120 gutter, starting x = 0: column 0 → x = 0; column 1 → x = 0 + 460 + 120 = 580; column 2 → x = 0 + (460 + 460) + (120 × 2) = 1160. Same arithmetic vertically with row heights + the 80 vertical gutter. Stack within a column the same way.
  - Reading axis sets the grid: left→right for flow/time (columns = stages), top→bottom for hierarchy (rows = levels), side-by-side for comparison (one column block per alternative). When in doubt, leave a column empty rather than crowd — empty space is free; overlap is not.
  - **Past ~40 nodes, generate the canvas.** Write a short script in the scratchpad that holds the content as data — groups → clusters → leaves, plus an edge list — and computes every coordinate by the accumulation above. Edit the data and re-run; never hand-edit coordinates on a large canvas. Serialize one node or edge per line (tab-indented, compact JSON, as Obsidian writes it) so a diff shows what changed.
- **Colors** (built-in palette `"1"`–`"6"`), each with the emoji circle its legend entry must carry: `1` 🔴 red, `2` 🟠 orange, `3` 🟡 yellow, `4` 🟢 green, `5` 🔵 cyan, `6` 🟣 purple, and no color ⚪. Hex strings also work — give those the nearest circle. Use colors to convey state — e.g., `4` 🟢 for "decided/chosen", `1` 🔴 for "rejected", `5` 🔵 for "observed fact", no color for neutral commentary.
- **Edges:** `fromSide`/`toSide` are one of `top`, `right`, `bottom`, `left`. Always pick sides intentionally — auto-routing through wrong sides produces unreadable crossings. Use `label` to name the relationship in a word or two (`"imports"`, `"binds"`, `"is a"`).
- **Edges stay short.** Place each group under or beside what it connects to, so an edge spans one gutter. An edge that would cross a group or pass through other nodes is noise: move the group, or drop the edge and let the leaf's words carry the relation. A leaf that sends an edge sits at the end of its cluster nearest the target, so the edge leaves without crossing its neighbours. Group membership is shown by the group box, never by hub→leaf edges — those draw a list.
- **Markdown in text nodes:** plain text for leaves. `##` only on hubs, `#` only on the title node. Inline code and `[[links]]` are fine.

## Worked example

A complete, valid canvas showing the conventions above in one piece — a title node, a legend node, two `group` panels of leaves (one leaf a `file` node pointing at real source), and an edge that targets a group itself. Every leaf is a label or one short claim; the panel labels carry the headings. Use it as the shape to start from, not content to copy.

```json
{
	"nodes":[
		{"id":"title","type":"text","text":"# Grid renderer — current vs proposed\n\n*Reads left→right: `main` today, then option (a). Sibling: `grid-perf.canvas`.*","x":0,"y":0,"width":540,"height":150},
		{"id":"legend","type":"text","text":"## Legend\n🟢 green — chosen\n🔴 red — rejected\n⚪ none — current","x":580,"y":0,"width":380,"height":150},
		{"id":"panel-current","type":"group","label":"Current","x":0,"y":230,"width":380,"height":392},
		{"id":"dispatch","type":"text","text":"Dispatch table","x":40,"y":270,"width":300,"height":64},
		{"id":"scan","type":"text","text":"O(n) scan per cell write","x":40,"y":358,"width":300,"height":64},
		{"id":"src-grid","type":"file","file":"src/renderer/grid.ts","x":40,"y":482,"width":300,"height":100},
		{"id":"panel-proposed","type":"group","label":"Proposed (a)","x":580,"y":230,"width":380,"height":232,"color":"4"},
		{"id":"index","type":"text","text":"Region-key index","x":620,"y":270,"width":300,"height":64},
		{"id":"lookup","type":"text","text":"O(1) lookup","x":620,"y":358,"width":300,"height":64}
	],
	"edges":[
		{"id":"e-scan-src","fromNode":"scan","fromSide":"bottom","toNode":"src-grid","toSide":"top","label":"lives in"},
		{"id":"e-current-proposed","fromNode":"panel-current","fromSide":"right","toNode":"panel-proposed","toSide":"left","label":"replace with"}
	]
}
```

The `src-grid` node renders the actual `src/renderer/grid.ts` file in Obsidian — clickable, never stale. The `e-current-proposed` edge points one whole panel at the other, and `scan` sits last in its panel so its edge to `src-grid` crosses nothing.

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
4. **Validate** after writing or editing — run `python3 scripts/validate-canvas.py <path>` (script ships in this skill's `scripts/` dir). It catches malformed JSON, duplicate ids, edges pointing at missing nodes, and overlapping nodes, and warns on wordy nodes. If `python3` isn't available, fall back to the checklist in **Validation** below.
5. **Tell the user what's on it** in one sentence (e.g., "Wrote the current vs proposed renderer architecture to `grid-system.canvas`. Left panel is what's in tree today; right panel is option (a)").
6. **Continue the conversation in chat.** Add to or edit the canvas when a new architectural artifact would clarify the next exchange — not on every turn.
7. **Re-read the canvas at session start** if returning to a session that already has one — it IS the conversation state.

## Validation

A `.canvas` file is hand-written JSON with referential integrity (edges name node ids) — easy to break in ways that render badly or not at all. After every write/edit, run the bundled validator:

```bash
python3 scripts/validate-canvas.py docs/canvases/<topic>.canvas
```

It exits non-zero with a readable report on: invalid JSON, duplicate node ids, edges referencing a missing `fromNode`/`toNode`, and overlapping node rectangles (a group legally containing its children is not flagged). It also prints a `WARN` line, without failing, for every text node over 12 words outside heading lines — split each into leaves before telling the user the canvas is ready.

**Fallback checklist** (when `python3` is unavailable) — eyeball the file for:

- Parses as JSON (no trailing commas, balanced braces/brackets).
- Every node `id` is unique; edges only reference ids that exist.
- Each node has `x`, `y`, `width`, `height`; each edge has `fromNode`/`toNode` (and intentional `fromSide`/`toSide`).
- No text node runs past a short sentence, `title` and `legend` aside.
- No two non-nested rectangles overlap — the hard one to see by eye, which is exactly why the script is preferred. With the column-grid layout (compute, don't guess) overlaps mostly can't happen in the first place.

## What to NOT do

- Don't write paragraphs into nodes. A node is a label or one short claim; more words means more nodes (see **Nodes are labels**).
- Don't translate the entire conversation onto the canvas. Most exchanges stay in chat.
- Don't add canvas nodes for questions you're about to ask the user — ask in chat.
- Don't pre-emptively scaffold dozens of nodes "in case we need them" — add as the conversation calls for them.
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
