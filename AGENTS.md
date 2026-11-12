# Instructions for AI agents

You are helping design a FIRST LEGO League competition robot (SPIKE Prime, studless Technic). The
person works in Stud.io and exchanges models with you as LDraw `.ldr` files. You write and edit those
files, check them with the tools in `tools/`, and explain the result in terms a builder can act on.

## Read first, in this order

1. `DESIGN_RULES.md`: the rules, why each exists, the feasibility limits and the design procedure.
2. `profile/TEAM_PROFILE.md` if it exists, else `profile/TEAM_PROFILE.example.md`: this team's PTO
   interface, preferences and defaults.
3. `PARTS_CATALOG.md`: parts with their holes, inventory trays and notes. Use it to find "the right
   piece" instead of guessing.
4. The brief (`BRIEF_TEMPLATE.md` filled in), and any reference designs the person gives you
   (usually in `designs/`, which is git-ignored). Study them before designing: they show the team's
   style better than any rule.

## Workflow

1. **Brief.** If an item in `BRIEF_TEMPLATE.md` is missing, use the team profile's default and say
   so. Ask only for things with no sensible default.
2. **Feasibility** (`DESIGN_RULES.md` §4b). If the brief is impossible, say so and why, with the
   nearest possible alternative. Don't design something that can't meet it.
3. **Design** following §12 of the rules. Write the `.ldr` (primer below). Prefer modifying a
   reference design over starting from nothing when the brief allows.
4. **Validate:** `python tools/run_checks.py MODEL.ldr`. Fix and rerun until clean. Then render
   (`tools/ldrender.py`) and look at the picture: it catches gross mistakes the numbers miss.
5. **Report:** what you built and why; the check results; the parts list (`ldbom.py`), flagging
   anything not owned; and **what the checks can't judge** (§15 of the rules). Use the robot
   coordinate language (`R3 F1 lvl2`).
6. **Iterate on feedback.** Ask for Stud.io screenshots (collisions show as transparent parts) and
   photos of the real build. They carry information the model file doesn't.

## Writing validation tools (do this)

Every check here exists because a rule was broken and nothing caught it. **When you meet a rule with
no automated check, or a person reports a problem the tools missed, first write a tool that catches
it, then fix the model.**

Conventions:
- Load a model with `ldcheck.parse_model` + `ldcheck.flatten_model` (world position and rotation of
  every part, submodels expanded).
- **Holes and connections:** official LDraw library primitives via `ldcheck.merged_bores(ref)`. Each
  hole is a segment (point, axis, span). Pins and axles: `ldcheck.shaft_def`.
- **Shape and clearance:** set `LDGEOM=studio` so geometry comes from the Stud.io library (what the
  person sees). Use `ldcheck.geom_vertices`.
- **Report in robot coordinates:** `frame.detect(parts)` + `ldcoord.set_frame()` + `ldcoord.name(P)`.
- **Validate the validator:** run it on a known-good design first. It must not flag things a person
  would call fine. (Real examples of false alarms we had: a beam hole is two thin ring primitives,
  not one long hole; a wheel's rim legitimately sits inside its tire; holes in motors are blind.)
  Then make sure it catches the real case.
- Add it to `tools/run_checks.py` and to `DESIGN_RULES.md` §13.

## LDraw primer (what you need to write `.ldr` files)

- One part per line:
  `1 <color> <x> <y> <z> <a b c d e f g h i> <part>.dat`, where the 9 numbers are a row-major
  rotation matrix applied to the part's local coordinates. Units are LDU (20 per stud). **−Y is up.**
- `0 FILE name` … `0 NOFILE` wraps each (sub)model; Stud.io references submodels by name, spaces
  allowed (`1 16 … wheel & tire`). Comment lines start with `0 //`.
- Stud.io writes Windows line endings; keep them. The person imports via File → Import → LDraw.
- Hole centers sit on the 20-LDU grid; a level is 20 LDU tall.
- **Verified rotation matrices** (from a working model; +Z = robot front, +X = right):

| Part, orientation | Matrix |
|---|---|
| Thick liftarm along X (across), holes vertical | `0 0 1 0 1 0 -1 0 0` |
| Thick liftarm along Z (fore-aft), holes vertical | `1 0 0 0 1 0 0 0 1` |
| Thick liftarm along X, on edge (holes fore-aft) | `0 0 1 1 0 0 0 1 0` |
| 2391 in a side wall along Z, sideways holes across (axle through) | `1 0 0 0 1 0 0 0 1` |
| Pin 2780/6558, vertical | `0 0 1 1 0 0 0 1 0` |
| Pin, fore-aft | `0 0 1 0 1 0 -1 0 0` |
| Pin, across | `1 0 0 0 1 0 0 0 1` |
| Bush 32123/3713, axis across | `0 0 1 0 1 0 -1 0 0` |
| 43093 axle-pin vertical, axle end up | `0 1 0 -1 0 0 0 0 1` |
| 32184 along X: end axle holes vertical, middle pin hole fore-aft | `0 1 0 1 0 0 0 0 -1` |

  For anything else, compute it from the part's local axes (`tools/ldflat.py PART` lists its hole
  primitives and their axes), then **check with `ldcheck.py`** that the pins actually land in holes.
- Never invent part numbers. A part must exist in `lib/ldraw` (or `lib/studio-ldraw`) and should be
  owned (`ldbom.py`).

## Don'ts

- Don't change the PTO interface or the attachment-ID sensor position unless the brief says so:
  existing attachments and the drive code depend on them.
- Don't claim a fit for things Stud.io can't model (e.g. a weight brick wedged in by hand). Reserve
  space and say so.
- Don't hand over a model you haven't run the checks on.
