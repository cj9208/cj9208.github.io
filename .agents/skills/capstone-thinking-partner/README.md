# capstone-thinking-partner

Skill bundle for the AI Chief of Staff Capstone: an AI that acts as a
professional *thinking coach* while the participant identifies, frames,
validates and advances one real organisational transformation opportunity
over a multi-week (roughly four-week-window) programme.

This folder is self-contained. To use it in a different repo or a dedicated
capstone project, move the whole `capstone-thinking-partner/` folder (skills
+ `reference/` move together) into that project's `.opencode/skills/`.

## Why six skills (design rationale)

The bundle mirrors the layering the source docs themselves insist on:

> The prompt tells AI what to do. Project Instructions tell it how to behave.
> Codified expertise tells it how strong practitioners think. What Good Looks
> Like tells it the quality standard. The conversation supplies the context.
> The human owns the decision.

| Layer in the docs | Where it lives in this bundle |
|---|---|
| How the AI should behave (06) | `capstone-coaching-core` |
| How strong practitioners think (02) | `capstone-coaching-core` (distilled) + `reference/02` |
| The task prompts (03, Part A) | the five phase skills |
| What good looks like / framing template (04) | `capstone-project-framing` + `reference/04` |
| Building new expertise (03, Part B) | `capstone-build-expertise` |
| Raw information base (01) | `reference/01` |

Split by **reuse frequency**, not by document:

- `capstone-coaching-core` is the always-on brain: coaching persona + the
  judgement model. Loads in any capstone conversation. Other skills defer to
  it instead of restating it.
- The phase skills trigger at specific workflow moments and each ends with a
  handoff note that seeds the next session.
- `capstone-build-expertise` is a rare, meta workflow used only when codifying
  a *new* professional judgement via Deep Research.

## Skill map

| Skill | When it loads | Purpose / output |
|---|---|---|
| `capstone-coaching-core` | start or continue capstone / transformation-opportunity thinking | Persistent coaching behaviour + codified judgement model |
| `capstone-compare-opportunities` | 2–3 candidate ideas, need a provisional direction | Fair comparison → provisional direction + handoff |
| `capstone-deepen-opportunity` | a direction is chosen and needs depth | Larger transformation first, then the four-week advance → **Capstone Working Brief** |
| `capstone-fieldwork` | planning interviews/observation, or returning with evidence | Pre: plan a small fieldwork sprint. Post: debrief reality, update the brief |
| `capstone-project-framing` | a clean senior-readable framing document is needed | Turns brief + evidence into the framing artefact (quality bar = 04) |
| `capstone-build-expertise` | a new professional judgement needs codifying (rare) | Deep Research brief → research → handbook → audit loop |

## Reference material

`reference/` holds cleaned transcripts of the original source documents
(numbered as in the source bundle). Skills point at the relevant file rather
than duplicating it. Canonical prose, decision rules and worked examples live
there; each `SKILL.md` is the operational distillation.

## When a capstone session is over

Close with a handoff note (the coaching-core behaviour) capturing the current
framing, the larger transformation, decisions and reasoning, evidence,
assumptions, unknowns, the four-week advance and evidence of progress. The
next session starts by pasting that note.
