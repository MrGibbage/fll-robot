# Team profile (example)

One team's standing choices, used as defaults when a brief leaves something blank. Copy to
`TEAM_PROFILE.md` and edit for your team.

## Building style
- **Wall-integrated mounting:** motors and sensors attach through perpendicular-hole pieces built
  into a symmetric, rectangular perimeter wall (small cross blocks
  2393/48989/32184/42003, perpendicular-hole pins 87082/15100, and 7×5 frames 64179;
  alternating-hole liftarms 2391/6612/73507/71710 only where their mounting advantage warrants them).
- Side walls **5 liftarms tall**, brick-bonded; corners from 32526 alternating direction.
- **A pin in every hole**, staggered 1-2-3; every piece held by ≥ 2 spread pins.
- Avoid 1L liftarms (18654). Use the shortest liftarm that holds its pins.
- Minimize rare/expensive alternating-hole beams without requiring a hard stock limit. Consider
  ordinary beams and small perpendicular connectors, especially 2393/48989, before adding another 71710.
- Audit rare beams by distinct sideways holes used along their length. A lone sideways
  connection should normally use a small perpendicular connector. All-one-direction usage
  should normally use an appropriately oriented ordinary beam; vertical pin filling alone
  does not justify an alternating beam.
- Connect usable aligned neighboring holes by default, including the motor case holes below
  longitudinal rails. Choose the correct pin type/length and explain exceptional omissions.
- Motor retainers must not be short pivot links. Prefer uninterrupted front-to-rear rails or
  properly anchored L/frame bracing; two pins into separate supports are not automatically rigid.
- Ground clearance: a liftarm slides under the robot; raise one level in obstacle seasons.

## PTO and attachments
- Two medium motors at the front, lying across, outputs **facing up**, symmetric about C, outputs at
  the motors' outer ends.
- Each output: 12T double-bevel gear (32270) on a 4L axle, rising through a 7×5 frame. Attachments
  drop on and mesh with the gears.
- **Attachment ID:** a color sensor between the accessory motors' tail ends, reading colored bricks
  on each attachment. The hub runs the matching mission when the left or right button is pressed.
  The sensor may face up or forward.

## Hub
- Charging with a normal straight micro-USB cable. Rotate the hub so the port faces a wall with a
  slot (e.g. the rear wall kept one level lower at C/L1/R1).
- ≥ 1 stud clear along the long sides for the cables. Attachments must not block the buttons.

## Weights
- Purpose: **counterbalance** heavy front attachments. Upright 73090 weight bricks in the rear
  corner pockets (behind each drive tire, between drive motor and side wall), held by a thin liftarm
  and pinned into the drive motor. Keep ≥ 2 studs of pocket.

## Drive
- Mid-wheel drive, caster (two 4185 wedge-belt wheels on an axle) at the rear.
- Wheels mirrored, locked with bushing stacks, no slop.

## Colors
- Give broad instructions, e.g. “prefer red wall beams with gray frames.” A per-color inventory
  is optional; it is only required if we request a strict stock audit.
- Preserve verified constrained-part colors, functional ID colors, and the colors in supplied
  working references. Apply the palette to eligible structural pieces and briefly list exceptions.
- If no palette is supplied, use the reference design's scheme; otherwise choose a coherent scheme
  from verified part/color choices and state the assumption. Do not assume every part can be black.
- A single color observed in a reference is a default, not a claim of exclusive manufacture.
