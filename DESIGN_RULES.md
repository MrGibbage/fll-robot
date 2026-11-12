# Robot Design Rules

General rules for designing FIRST LEGO League (FLL) competition robots: SPIKE Prime hub and motors,
studless Technic, modeled in Stud.io and exchanged as LDraw (`.ldr`) files. Each rule says **why**.
Most have an automated check in `tools/` (§13).

Team-specific choices (your PTO interface, your inventory, your preferences) live in
`profile/TEAM_PROFILE.md` (start from `TEAM_PROFILE.example.md`). Where this file says "per the team
profile", look there.

---

## 1. Glossary and units

| Term | Meaning |
|---|---|
| **LDU** | LDraw Unit, the coordinate unit in `.ldr` files. 1 LDU = 0.4 mm. |
| **stud / module / hole** | The Technic grid pitch: **20 LDU = 8 mm**. Hole centers on a liftarm are 1 stud apart. |
| plate / brick | 8 LDU (3.2 mm) / 24 LDU (9.6 mm) tall (System bricks; rarely used except weight bricks). |
| **liftarm (beam)** | Studless Technic beam. "Thick" = 1 stud wide and 1 stud tall (all structural ones here); "thin" = half as thick. Named by hole count: **3L, 5L, 7L…** |
| **bent liftarm** | e.g. 32526: L-shaped 3×5, 90°. Typical wall corner. |
| **frame** | e.g. 64179: 7×5 open-center frame. |
| **alternating-hole liftarm** | 2391 (7L), 6612 (9L), 73507 (11L), 71710 (15L). **The two end holes go straight through, and the direction alternates inward from the ends.** So on the 7L/11L/15L the center hole is sideways; on the 9L the center goes straight through. |
| **pin** | Friction pins: **2L** = 2780, **3L** = 6558. 43093 = axle-pin (half axle, half pin). Pins join liftarms through holes. |
| **axle / bush** | Cross-section axles (4519 = 3L, 3706 = 6L, 60485 = 9L…). Bushes stop things sliding along an axle: **half bush** 32123 = 10 LDU, **full bush** 3713 = 20 LDU. |
| **cross block** | Small connectors with holes in two directions: 32184 (axle-pin-axle), 2393 (pin-pin-pin with **2 built-in pins**), 48989 (4 built-in pins). |
| **hole direction** | **vertical** (up/down), **fore-aft** (front/back), **across** (left/right). |
| **level (lvl)** | One liftarm layer of wall height. `lvl1` = bottom wall layer. |
| **row (F)** | Position front-to-back. `F1` = front wall. |
| **column** | One hole position along a wall, all levels stacked. |
| **joint / seam** | Where two liftarms end next to each other in one level. A **seam** = joints at the same spot on adjacent levels (bad). |
| **brick bond** | Staggering joints level to level like a brick wall, so there are no seams. |
| **isolated hole** | A vertical hole with no vertical hole directly above or below it (e.g. next to an alternating liftarm's sideways hole). It can't be pinned. |
| **drive layout** | Where the drive wheels sit along the robot's length: front, mid, or rear wheel drive. |
| **track width / wheelbase** | Distance between the drive tires' centers / from the drive axle to the caster. |
| **caster / drag wheel** | The passive support at the other end from the drive wheels. |
| **PTO** | Power take-off: how the accessory motors deliver motion to an attachment. |
| **attachment** | Mission tool that mounts on the robot and is driven by the PTO. |
| **attachment ID** | Colored bricks on each attachment, read by a color sensor, so the hub picks the mission program. |
| **launch area / height limit** | FLL Robot Game limits on the robot at the start of a run. Check the current season's rulebook. |

## 2. Coordinates (robot-relative)

| Axis | Name | Meaning |
|---|---|---|
| Across | `C`, `R1`…`Rn`, `L1`…`Ln` | studs from the centerline, robot's own right/left (as if driving it) |
| Front/back | `F1`, `F2`, … | rows counted back from the front wall |
| Height | `lvl1`, `lvl2`, … | layers up from the bottom wall layer. A pin spanning two levels is `lvl1.5` |

LDraw conventions used by the tools: **−Y is up**, +Z is the robot's front (set `FLL_FRONT=-z` if
yours faces −Z), +X is the robot's right. The tools find the walls automatically (`tools/frame.py`;
override with `FLL_FRAME="LX,RX,FZ,RZ,Y1"`). `tools/ldcoord.py MODEL x y z` converts between the
two systems.

## 3. The design brief (inputs)

Every robot starts from a brief. Use `BRIEF_TEMPLATE.md`. The inputs are:

1. **Wheels and tires** (rim + tire part numbers): set the axle height, the track width (with the
   bushing stack) and the tire clearance.
2. **Drive layout:** front / mid / rear wheel drive. Mid pivots about the robot's center.
3. **Size envelope:** max width, length, height (launch area + height limit + your own limits).
   Drives the layout choice (§4b, §5).
4. **Ground clearance:** default *a liftarm slides under the robot*. For obstacles, raise the walls
   by one level.
5. **PTO design:** number of accessory motors, output direction, spacing and position, coupling
   (gear type), how attachments locate and stay on, whether existing attachments must still fit.
6. **Attachment ID sensor:** yes/no, facing up or forward, where.
7. **Weights:** purpose (counterbalance heavy front attachments → back; traction → near the drive
   axle), how many, which part.
8. **Charging:** the hub's micro-USB port must be reachable with a normal straight cable.
9. **Inventory / colors:** what you own (`profile/inventory.csv`), colors to use or avoid.
10. **Software:** values your drive code needs (wheel diameter, track width, motor ports and
    directions, hub orientation for buttons, display and gyro).

## 4. Component reference

| Part | Size (LDU) | Facts that matter |
|---|---|---|
| Hub bb1142c01 (+battery 55422c01) | 140×80×220 (7×4×11 studs) | **Micro-USB** at one short end, near the top. **Ports A–F** on the two long sides. Pin holes in the end faces (±2 studs across, 3 heights) and along the sides. |
| Large motor 54675 (drive) | 100×80×180 | Output on its side. Pin holes on its faces, including the back. |
| Medium motor 54696 (accessory) | 60×80×180 | Round output boss near one end. Holes on both faces and the tail end; two motors' tail ends can sandwich a color sensor. |
| Color sensor 37308c01 | 60×58×59 | Stud.io's model is offset 49 LDU from official LDraw (handled by `STUDIO_FIX`). |
| Tire 44771 on rim 15038 | ⌀172, 88 wide | Rim is **dished**: its axle hub is 20 LDU long and off-center. |
| Tire 41897 on rim 41896 | ⌀140, 70 wide | |
| Wheel 39367pb01 | ⌀140, 35 wide | |
| Caster wheel 4185 | ⌀60, 10 wide | |
| Weight brick 73090b | 120×52×40 | Often mounted in ways Stud.io can't model. Reserve space. |

Everything else: **`PARTS_CATALOG.md`** (size, through-holes per direction, built-in pins,
inventory tray, notes). If a spot needs "a piece with a sideways hole here and a pin hole there",
search its Holes column. **Design with owned parts.** `tools/ldbom.py` lists a model's parts by tray
and flags anything not owned, which must be called out as "needs ordering".

## 4b. Feasibility: is the brief even possible?

Run this before designing. The core parts have a minimum size no layout can beat. In studs;
*S* = wheel stack (motor face to wall: bushings + rim hub), set by the tire width (≈4 for a 35 mm
tire, ≈3 for 28 mm).

| | Layout A: hub flat between drive motors | Layout B: hub on top of drive motors |
|---|---|---|
| **Width** | 2 walls + 2·S + 2 drive motors (4 each) + 2 port clearances (1 each) + hub (7) = **19 + 2·S** (typ. 25–27) | 2 walls + 2·S + 8 + gap, ≥ hub (7). Typ. ~17. **Floor with no walls and the thinnest wheels: ~11.5 studs (92 mm)** |
| **Length** | front wall + PTO (3) + motor-back liftarm (1) + spacer (1) + hub (11) + rear wall ≈ **18** | ≥ hub (11) or drive motor (9), plus PTO and walls. Typ. ~22 |
| **Height** | ≥ tire diameter, and the walls + PTO gears. Typ. ~9 (70 mm) | drive motor (4) + hub (4) + ground clearance + PTO. Typ. ~11 (90 mm) |
| Accessory motors lying across the front + sensor between | 9 + 3 + 9 = 21 + walls 2 = **23** → fits any layout A | doesn't fit; mount them lengthwise or on top of the drive motors |

- "5 studs wide" is impossible: the two drive motors alone are 8 studs along the axle.
- The core parts (hub, 2 large motors, 2 medium motors, sensor) take ~900 stud³ before any structure.
- If the envelope is below a layout's minimum, change the layout (B is narrower but taller and
  longer) or the wheels (*S*). Otherwise, say plainly that the brief is impossible.

## 5. Layout decisions

- **Drive motors** sit symmetric about C, outputs facing outward. Wheels go outside the motors, side
  walls outside the wheels. Width follows from §4b.
- **Axle height** comes from the tire radius. The walls are built around the axle level, and the axle
  pokes through the side wall at the drive row.
- **Hub:** flat between the drive motors (wide/low) or on top of them (narrow). Orient it so the
  charging port faces a wall that has a gap for the plug.
- **Accessory motors (PTO):** at the end opposite the caster. Lying across (outputs at the outer ends,
  sensor between the tails) or lengthwise. **Keep them clear of the tires**: tires have a large
  radius, and a front module may need to move forward a stud.
- **Caster** at the far end from the PTO, between the drive motors (it can hang from them).
- **Spacer liftarms** across the robot between the drive section and the front module tie hub, drive
  mounts and front module together.
- **Weight pockets** where the brief's weight purpose says (counterbalance → rear corners).

## 6. Walls

- **Perimeter wall, rectangular, mirror-symmetric.** Side walls a constant height (e.g. 5 liftarms),
  +1 level if more ground clearance is needed. The rear wall may step up where it can reach
  something useful (e.g. motor rear-face holes), and stays low where a charging plug must pass.
- **Brick bond:** no joint lines up with a joint on the level directly above or below. (`ldseam.py`)
- **Corners interlock:** bent 3×5 liftarms alternate arm direction level by level.
- **Mount through the wall:** motors, axles and sensors attach through wall pieces with perpendicular
  holes (alternating-hole liftarms, cross blocks, frames), not hung from beams underneath.
- **Axles through walls** use a sideways hole of an alternating-hole liftarm.
- **Don't use a liftarm longer than its pins need.** Prefer fewer, longer pieces over many short ones.
- **Avoid 1L liftarms.** No strength. Only as a last-resort filler or to cap an exposed pin.

## 7. Pins

- **Goal: a pin in every hole.** Isolated holes stay empty. No half pins as fillers. (`ldholes.py`)
- **Every piece needs at least TWO pins into other parts, spread along it.** A piece on one pin spins;
  two pins close together on a long liftarm barely help. Exceptions: gears on their axle, 1L pieces.
  (`ldanchor.py`)
- **Stagger the pin breaks (1-2-3).** Vary where each column's pins end, so the levels are bridged at
  different heights in neighboring columns. Per column of stacked vertical holes:
  - 5 levels: alternate 3L+2L and 2L+3L
  - 4 levels: 2L+2L (the 3- and 5-level columns next to it supply the stagger)
  - 3 levels: one 3L; 2 levels: one 2L
- **No pin sticks out above the wall top or below its bottom.** (`ldpinsout.py`)
- **Mirror symmetry**, pins included. (`ldsym.py`)
- Built-in pins (2393, 48989) count as filled holes. The 2393's point **up** into the level above.

## 8. Hub

- **Charging port reachable** with a straight micro-USB plug. Leave a gap or low wall where the plug
  passes. (`ldclear.py`)
- **Long sides (ports A–F): ≥ 1 stud clear** for the cables. (`ldclear.py`)
- **Pin it into the structure on several faces** (front, sides, rear).
- **Buttons:** attachments must not block them. Rotating the hub moves them and swaps left/right in
  software.
- Mount it flat or in a known orientation, because the gyro is in the hub.

## 9. Drive train

- **Wheels are mirror images.** Dished rims: turn the left wheel 180° relative to the right.
- **Lock each wheel along its axle with bushings**, with no slop, e.g. from the motor face out:
  half bush · rim hub · full bush · full bush · half bush · wall.
- **Tires must clear everything.** `ldcheck.py` models each tire as a solid ring.
- **Ground clearance:** nothing structural hangs below the wall's bottom level.
- The caster's bottom vs the tires' bottom only tilts the robot (two tires plus a caster always all
  touch). Keep it close.

## 10. Balance and weights

- Counterbalance for heavy front attachments → weight at the back. Traction → weight near the drive
  axle. Weight over the caster mostly loads the caster.
- Reserve pocket space for anything Stud.io can't model (`ldfree.py`).

## 11. PTO and attachments

- The PTO geometry plus the attachment-ID sensor position **is the interface**. Moving either breaks
  existing attachments and the drive code. If the brief says existing attachments must fit, copy
  the interface exactly (per the team profile).
- Fix accessory motors front and back: perpendicular-hole liftarms in the front wall pinned into the
  motor fronts, and a liftarm behind them pinned into the motor backs (and on into the hub if it's
  there).
- A color sensor between the accessory motors' tail ends, pinned to both, also braces the module.

## 12. Procedure: a new robot from a brief

0. **Feasibility:** check the brief against §4b; pick layout A or B, or explain why it's impossible.
1. **Drive train:** wheels/tires → axle height → drive motor height. Mirror the motors about C.
   Bushing stack → wheel position → side-wall position → width. Check against the envelope.
2. **Hub:** flat between the motors (≥ 1 stud port clearance each side) or on top. Orient for charging.
3. **PTO:** accessory motors (+ sensor) at the end opposite the caster. Check the tire clearance.
4. **Caster** at the other end.
5. **Walls:** perimeter at the right levels. Choose liftarm lengths per level so there are no seams.
   Corners alternate. Perpendicular-hole liftarms where axles and motors attach.
6. **Ties:** spacer liftarms between the drive section and the front module, pinned into the hub,
   the drive mounts and the PTO frames.
7. **Pins:** fill every column with the stagger pattern; every piece ≥ 2 spread pins.
8. **Weights:** confirm pocket space.
9. **Run every check (§13), render, look.** Fix and repeat until clean. Hand over with a list of what
   the checks can't judge.

## 13. Checks

```bash
python tools/run_checks.py MODEL.ldr        # runs all of the below and summarizes
python tools/ldcheck.py   MODEL.ldr         # connections, floating parts, doubled pins, collisions incl. tires
python tools/ldseam.py    MODEL.ldr         # brick bond
python tools/ldholes.py   MODEL.ldr         # empty vertical wall holes (should be isolated holes only)
python tools/ldanchor.py  MODEL.ldr         # every piece held by >= 2 well-spread pins
python -I tools/ldpinsout.py MODEL.ldr      # pins sticking out of the walls
python tools/ldsym.py     MODEL.ldr         # left/right mirror twins
python -I tools/ldclear.py MODEL.ldr        # hub charge port + side-port clearance
python -I tools/ldfree.py MODEL.ldr x0 x1 y0 y1 z0 z1   # free space (pockets)
python -I tools/ldbom.py  MODEL.ldr         # parts by tray; flags anything not owned
python tools/ldrender.py  MODEL.ldr out.png --view iso [--highlight PART]
```

**When a rule has no check, write one** (see `AGENTS.md`). Every tool here started as a rule that a
person had to point out.

## 14. Lessons learned (each cost an iteration)

- A hole-based checker can't see **tires** (no holes). Model them as solid rings.
- The **alternating-hole** pattern decides which holes take vertical pins. Check before placing one.
- A bent liftarm's **origin** is at the end of its long arm, not the corner. Don't search by origin
  distance.
- The **2393's built-in pins point up**, filling the hole above.
- Stud.io's **color sensor** is offset from official LDraw.
- Dished **rims** mounted the same way on both sides are *not* symmetric.
- When something moves, look for holes that newly line up (moving a rear wall can line its pins up
  with the hub).
- Stud.io writes **Windows line endings** in `.ldr`. Preserve them when editing.
- Stud.io shows collisions as **transparent parts**. A screenshot of that is the fastest way for a
  person to show a problem.

## 15. Not captured: needs human judgment

Build order (can a part actually be inserted?), cable routing and length, attachment retention and
swap speed, strength under load (flex, pin wear), stud connections, sensor reading distance and
angle, real-world fit of things Stud.io can't model, aesthetics.
