# Study Group Playbook: Running the System Design Roadmap as a Group


The [System Design Master Roadmap](https://cj9208.github.io/blog/AI_study/system_design/system-design-master-roadmap/) has a clear internal logic: three parts plus a verification loop. Reading it alone, though, creates a false sense of security—the same failure mode the roadmap itself warns about. A study group replaces "read then chat" with "produce comparable artifacts, present them, and get challenged."

The roadmap already ships the sharing formats: trade-off cards (V.1), what-if whiteboarding (V.2), post-mortem audits (III.1), and micro-experiments (III.3). The group's job is to turn those into a repeatable rhythm.

## Core Principle: Three Angles, Two Tracks Plus a Lens

Map the three parts of the roadmap onto the group's mechanics. Part II is **not a fourth slot—it is a lens applied inside the other two**, because every mechanism discussion is implicitly a pole choice:

* **Track A — Stage Ladder (Part I):** go stage by stage, one to two stages per session.
* **Track C — Experience (Part III):** over the cycle, each member must deliver one post-mortem audit and run one lab.
* **The Part II lens:** each week picks one trade-off axis; that axis decides which trade-off every teach-back, grilling question, whiteboard move, and post-mortem is forced to name. The week's axis makes Part II explicit instead of implicit.

## Session Rhythm (90–120 minutes)

| # | Time | Activity | Track |
|---|---|---|---|
| 1 | 10 min | Stage teach-back (must end with the trade-off line) + grilling that attacks the card | A + lens |
| 2 | 30 min | What-if whiteboarding (every move declares its pole + criterion) | A/B |
| 3 | 30 min | Post-mortem presentation (audit Q5 mapped to a named axis) | C + lens |
| 4 | 20 min | Trade-off card exchange (cards born in teach-back, now compared) | lens |
| 5 | 10 min | Lab bench review | C |

## Worked Example: Stage 2 — Cache + Read Replicas

All four mechanisms below use the same topic so you can see how one stage feeds the whole rhythm.

### Stage Teach-Back (Track A, 5 min)

The presenter compresses the stage into "bottleneck → requirement → implementation" and must be able to say why the previous stage broke:

> "At Stage 1, read traffic saturates the primary DB's CPU and maxes out connection pools, point-read latency spikes, and the primary is a single point of failure. So we split the read path: a Redis cache absorbs hot reads, read replicas absorb the rest of the query load, writes stay pinned to the primary. The price is replication lag—a reader can see stale data."

Rules: no reading from notes, five minutes, and the group grades two things: did they explain why the old design broke, and did they end with the **trade-off line**—what the stage sacrificed (in the example above, replication lag). The trade-off card is born here, not in a separate slot.

### Group Grilling (Track A, 5–10 min)

Grilling questions target trade-offs and failure thresholds, never surface facts:

* "You added read replicas—is the write path still a single point of failure?" *(expected: yes, still a SPOF; that is Stage 4's job)*
* "Cache-Aside can serve stale data. What bounds the staleness?" *(TTL ceiling / invalidation policy)*
* "With async replication, how much data do you lose on failover? Why is sync replication expensive?" *(lag window vs write latency)*
* "One hot key gets 100x traffic during a flash sale. What happens to your cache?" *(hot key + stampede)*

### Trade-Off Card (Track B)

Every member fills the same three-question schema for the mechanism of the week. Example for Cache-Aside:

| Question | Answer |
|---|---|
| What exact problem does it solve? | Stops repeated reads from hitting the DB; absorbs read spikes |
| What does it sacrifice? | Staleness window, invalidation complexity, cold-start stampede |
| At what threshold does it fail? | Hit ratio collapses when working set > cache; hot-key stampede; write-heavy workloads |

Cards are comparable only because the schema is fixed—the group argues about the answer, not the format.

### What-If Whiteboarding (Track A/B, 30 min)

One driver on the whiteboard, everyone else feeds constraint shifts.

Every move the driver makes must declare its **pole + decision criterion**—"I chose Cache-Aside over Write-Through because miss cost is high and staleness is tolerable" (axis II.4). The week's axis tells the group which trade-off to keep forcing; a move that cannot name its pole is an unfinished decision.

Problem: "Product detail page—10k reads/s, 500 writes/s, p99 < 200ms."

* **Step A (minimal skeleton):** Client → API → App → Postgres.
* **Step B (evolve):** add Redis (Cache-Aside) + read replicas + read/write splitting; writes pinned to primary.
* **Step C (stress-test shifts thrown by the group):**
  * "One SKU becomes 100x hot during a flash sale" → driver reacts (local cache / single-flight / XFetch).
  * "The primary dies" → driver rehearses failover and stale-read behaviour under lag.
  * "The cache is completely cold" → driver handles prewarm / stampede.

Output: a one-pager capturing the final design plus the list of shifts that were applied—this becomes the group's retained artifact for the week.

## Grilling vs Whiteboarding: Why Both

They look similar—both interrogate a design and push on edge cases. The difference is what is tested and what the answer looks like:

| | Group Grilling | What-If Whiteboarding |
|---|---|---|
| Interrogates | A single mechanism's trade-offs and failure thresholds | The whole system's ability to synthesize under shifting constraints |
| Does the design change? | No—probe the boundary of one mechanism | Yes—the driver must actually evolve the architecture |
| Nature of the answer | A fixed, correct boundary ("write path is still a SPOF—that is Stage 4's job") | A sequence of design moves plus justification ("add local cache + single-flight; the cost is …") |
| Format | Oral exam on one concept | System-design interview round, with constraints as the driver |
| Cost | Cheap (5–10 min)—every member can be grilled every session | Expensive (30 min)—only the driver gets the full reps |

One-line rule: **grilling tests whether you understand a card; whiteboarding tests whether you can compose the cards.** Both are needed: grilling distributes cheap verification to everyone and catches "memorized the words but don't know the boundary"; whiteboarding is the only thing that exposes "knows every card but can't assemble a system"—the biggest false-confidence source of all.

### Coverage Boundary: Keep Whiteboarding Fair

The apparent contradiction: Track A teaches one stage per session, so how can a Week-2 whiteboard combine cache, replicas, and sharding that hasn't been taught yet? The rule: whiteboarding is a **backward-accumulating recombination**, never full-system synthesis.

* **Bound the problem to the covered set.** In week N, the problem may only require mechanisms from stages 0..N. Week 2 (after stages 0–2) gets read-heavy problems only (cache + replicas + read/write splitting); nobody throws "a single server cannot hold the dataset"—that is Stage 4's sharding, not yet taught.
* **This week's mechanism is the intended move.** Build the baseline with the old mechanisms; the one move that saves the design under pressure must be the current session's new point. If a problem is solvable without this week's mechanism, the problem is badly designed.
* **Shifts stay inside covered territory.** Constraint shifts may only stress the accumulated set. If someone throws an uncovered constraint, record it as a *teaser* ("that is next week's Stage 4 problem") and move on.
* **Difficulty scales with coverage.** The only session that crosses the whole ladder is the Week 6 capstone, after every stage is taught—that is when full synthesis becomes fair.

| Week | Covered | Whiteboard problem domain |
|---|---|---|
| 2 | Stage 0–2 | Read-heavy detail page: cache + replicas + read/write splitting |
| 4 | Stage 0–4 | Data growth added: hot keys + sharding |
| 6 | Full ladder | Capstone: Stage 0 → 5 under any shift |

This keeps "one new point per session" consistent with "recombine what we have": you learn points, you practice re-arranging the accumulated set into a system—which is how real engineers actually learn sharding, as a layer on top of cache, replicas, and microservices.

## Artifacts and Schemas

Everything the group produces must follow a fixed schema so it stays comparable:

* **Trade-Off Card** — the three questions above.
* **Lab report** — a short benchmark write-up (numbers, not opinions): the metric, the measurement, the deviation from theory. E.g., the Storage Lab: write throughput vs point-lookup latency, mini LSM implementation vs SQLite.
* **Post-mortem audit** — the five questions from III.1 of the roadmap, answered for one production migration, with Q5 (new trade-offs introduced) mapped to a named axis.
* **Whiteboard one-pager** — the final design plus the constraint shifts applied.

## Carriers

* **Git:** each member opens a branch with their cards and reports, opens a PR, and the group's review *is* the critique. Everything is retained and reviewable.
* **Blog:** session one-pagers and teach-back summaries can be published as posts—this site is a Hugo blog—giving public accountability and a durable log.

## Running the Whole Cycle

A suggested six-week cycle over Part I of the roadmap:

| Week | Focus |
|---|---|
| 1 | Stage 0–1 |
| 2 | Stage 1–2 |
| 3 | Stage 2–3 |
| 4 | Stage 3–4 |
| 5 | Stage 4–5 |
| 6 | Whiteboard capstone: cross the whole ladder (Stage 0 → Stage 5) under stress |

Track C (post-mortems + labs) runs in parallel every week, while the week's trade-off axis acts as the lens across teach-back, whiteboarding, and post-mortems—so a cycle ends with the full three-angle coverage the roadmap intends.
