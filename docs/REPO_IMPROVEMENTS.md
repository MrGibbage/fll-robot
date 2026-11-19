# Proposal: a reliable single-prompt robot workflow

Updated after the team supplied a recolored Stud.io export and identified a missed roller collision.
This document proposes future tooling; it does not claim complete production-color or stock validation.

## Keep normal team input simple

A team should be able to say “make the wall beams red” and use its saved mechanical preset.
A color-by-color inventory must not be a prerequisite. The normal workflow needs:

- A broad palette, or a reference model whose colors should be preserved.
- Repository-provided component identities and conservative, verified part-color knowledge.
- Optional overrides for a team's unusual stock or strict requirements.

Detailed per-color stock counts are an advanced, opt-in audit. Blank or absent stock data stays
unknown; the report must not call it verified. Do not assume every kit part is owned merely because
it appears in a generic example.

## Color knowledge belongs with the parts

Keep three facts separate: production availability, reference/default appearance, and actual stock.
A default seen in a working export is useful, but does not prove that no other color was produced.
A DAT accepting a color code does not establish production availability either.

Build a repository component registry with export ID, official geometry ID, origin conversion,
assembly members, inherited export color, palette eligibility, verified color options where known,
and the evidence/source for those facts. Maintain this centrally rather than asking each team to
research it. Pin/axle variants and functional attachment-ID colors must retain their meaning.
Multi-color electronics must retain their intrinsic appearance.

Apply broad palette instructions to eligible structural pieces. Treat unqualified style requests
as preferences; an explicit “must” or “only” is a hard requirement. If a constrained part cannot
match the palette, retain its established color and briefly list the exception. For an explicit
hard color requirement, find another suitable construction or report infeasibility.

For this team, the edited `low_wide_v1_studio_updated_colors.ldr` is the color reference: gray
alternating beams and frames, azure motors, gray rims and 4L axles, and mostly yellow half bushes.
Repairs must preserve these edits. These are reference defaults, not an exhaustive factory-color list.

Extend the BOM to list part/color usage. Add production-color and optional stock validation when
those data sources are available. Do not burden normal users with filling those databases.

## Import compatibility needs its own evidence

The original instructions already named the correct Stud.io electronics. The agent nevertheless
substituted official LDraw aliases. A successful local render did not establish import compatibility.
The working sample convention is hub `bb1142c01`, separate battery `55422c01` at the same pose,
and sensor `37308c01`. Preserve a minimal reference export fixture without embedded proprietary
geometry, and test identity/origin substitutions against it.

The current import-ID regression check catches this particular error. Generalize the component
mapping into the registry rather than scattering aliases and offsets across tools.

## Collision checks must include passive rollers

The original tire check covered the large tires and omitted 4185 rollers. The user then found that
both small rollers intersected the lower rear beam. This now has a dedicated swept-disk check,
including triangle faces that can cross the disk even when their vertices lie outside it.
A known-good axle/bush stack and the real wheel/beam failure are regression cases.

Spoke openings are not safe space for a stationary part when the wheel rotates. AABB overlap is
only a broad-phase candidate test, not proof of collision. Keep axle holes and legitimate mating
contacts as narrowly defined exceptions, rather than exempting all nearby shafts or bushings.

## Organize the instructions and completion gates

- AGENTS.md: workflow, broad color input, preservation of user edits, and evidence required for delivery.
- DESIGN_RULES.md: mechanical requirements, applicability, and each rule's verification method.
- TEAM_PROFILE.md: standing interface and palette defaults; a named low-wide-two-PTO preset.
- BRIEF_TEMPLATE.md: a generic template; filled answers go into a project brief.
- Inventory: owned part types, with optional color/quantity detail.
- Component registry/catalog: reusable import, geometry, function, and color facts.
- Tests: small known-good cases and each previously missed failure.

Distinguish automated checks passed, hard requirements met, and physical checks still needed.
Documenting a hard-rule exception does not make it compliant. The lower caster-bearing height was separate from the wheel/beam collision; the deeper v3
perimeter now encloses that hardware. Its actual floor clearance must still be distinguished from
an assumed one-beam gap.

## Minimal prompt after one-time setup

> Follow AGENTS.md. Use our low-wide, two-PTO preset and 69 mm wheels. Target 27 × 18 studs;
> maximum 29 × 20. Existing attachments need not fit. Make the wall beams red. Preserve established
> constrained-part colors and use profile defaults for everything else. Ask only about blocking
> ambiguities. Deliver the LDraw model, inspected renders, BOM and validation report.

Aim for one prompt to a coherent, import-compatible, checked build candidate. Cable routing,
stiffness, attachment retention, and sensor performance still need physical testing.

## Implemented after the wall-height and bracing feedback

- The generic brief now separates total layers, complete layers below the drive axle, approximate
  clearance targets, hard minimum clearance and conflict priority. The initial filled brief was saved.
- Rules, profile and catalog notes now conserve rare alternating-hole beams as a qualitative
  preference, consider small perpendicular connectors, and require rigid motor retention.
- `ldground.py` measures full wall courses and the true pitched contact plane; `ldmotorbrace.py`
  checks the specific short-link hinge failure. These join the existing automated suite.
- Molded pins on 2393/48989 now count as connections and occupied holes and participate in overlap
  detection. Regression tests cover valid molded-pin seating and accidental double-filling.
- The v3 model uses three full courses below the axle and continuous longitudinal motor rails.
  This row count predicts 6.46 mm clearance at the drive axle and 4.29 mm at the lowest front edge;
  it does not certify an 8 mm minimum. The team has confirmed that this interpretation is correct; no strict 8 mm minimum is intended.

## Additional connection and rare-beam guidance

Audit the actual sideways holes used along each rare beam. One such hole is a red flag for a
small perpendicular connector; all-one-direction usage suggests rotating an ordinary beam.
Retain a rare beam only when its distributed mixed-direction connections justify it.

Aligned usable holes in adjacent parts should normally be connected. The audit must include
motor case holes below longitudinal rails and interpret real round versus axle holes, blind
depth, thin end-ring primitives, cosmetic negative reliefs and existing shafts. The new default
is a full mating-hole pass, not merely a wall-pin fill. Rare intentional omissions require a reason.
