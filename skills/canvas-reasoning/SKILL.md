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
- **Coordinate system:** positive x = right, positive y = down. Coordinates are in pixels.
- **Sizing — err larger than feels necessary.** Obsidian's default text-node size is small enough that almost any node with a heading + a few lines of content will show an internal scrollbar, and edge labels collide with adjacent nodes when gutters are tight. The cost of *too-large* is zoomable visual noise; the cost of *too-small* is unreadable nodes and overlapping labels. Default toward more space. Concrete starting points (use as **floors, not targets** — go bigger when in doubt):
  - **Small text nodes** (one-line label + one-line detail): ~300 × 120
  - **Medium text nodes** (heading + 3–4 lines): ~460 × 180
  - **Large / central nodes** (heading + 5+ lines, hub component): ~510 × 330
  - **Horizontal gutter between columns:** ~120 px (so edge labels fit between nodes)
  - **Vertical gutter between same-column nodes:** ~80 px (where edge labels collide most)
  - **Gutter between independent groups:** ~200 px

  When iterating to relieve density on an existing canvas, **resize nodes and reposition gutters as separate decisions.** Uniformly scaling every `(x, y, w, h)` by the same factor changes the visual ratio not at all — it's just zoom. To actually open up a cramped canvas, the node-size multiplier and the gutter-size multiplier should differ (commonly: nodes 1.5×, gutters 2–3× on the previously-tight axes).
- **Colors** (built-in palette `"1"`–`"6"`): `1` red, `2` orange, `3` yellow, `4` green, `5` cyan, `6` purple. Hex strings also work. Use colors to convey state — e.g., `4` green for "decided/chosen", `1` red for "rejected", `5` cyan for "observed fact", no color for neutral commentary.
- **Edges:** `fromSide`/`toSide` are one of `top`, `right`, `bottom`, `left`. Always pick sides intentionally — auto-routing through wrong sides produces unreadable crossings. Use `label` to name the relationship (`"imports"`, `"depends on"`, `"asserted-equal-to"`).
- **Markdown in text nodes:** node `text` accepts markdown. Use `## Heading` for the node title and short prose below. Keep nodes to ~3–6 lines of content; if a node needs more, split into linked nodes.

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
4. **Tell the user what's on it** in one sentence (e.g., "Wrote the current vs proposed renderer architecture to `grid-system.canvas`. Left panel is what's in tree today; right panel is option (a)").
5. **Continue the conversation in chat.** Add to or edit the canvas when a new architectural artifact would clarify the next exchange — not on every turn.
6. **Re-read the canvas at session start** if returning to a session that already has one — it IS the conversation state.

## What to NOT do

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
