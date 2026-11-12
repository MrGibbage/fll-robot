# Robot design brief

Copy this file to `briefs/<robot-name>.md`, fill it in, and point the agent at it. Leave an item
blank to use the default from your team profile. Say **why** where you have a reason.

**You don't have to answer everything.** Every item here matters eventually, but most get settled
along the way, often once the robot is being built. For example: you didn't say the drive motor
cables *must* go in ports A and E. Then the first build shows they don't reach, so the design
changes. That's normal. Fill in what you know and care about now; the agent uses defaults for the
rest, says which ones it used, and you add to the brief as you learn.

**Robot name:**

1. **Wheels and tires** (part numbers, or "same as <design>"):
2. **Drive layout** (front / mid / rear wheel drive):
3. **Size limits** (max width × length × height, in studs or mm; note any season rules):
4. **Ground clearance** (default: a liftarm slides under; "+1 level" for driving over obstacles):
5. **PTO**
   - number of accessory motors:
   - output direction (up / forward / …):
   - spacing and position:
   - coupling (e.g. 12T double-bevel on a 4L axle):
   - how attachments locate and stay on:
   - must existing attachments still fit? (if yes, attach or name the reference design):
6. **Attachment ID sensor** (yes/no; facing up / forward; where):
7. **Weights** (purpose: counterbalance / traction; how many; part):
8. **Charging access** (default: straight micro-USB cable reaches the hub without removing parts):
9. **Parts and colors** (default: `PARTS_AVAILABLE.csv`, or `profile/parts.csv`; parts to add or rule out; colors to use or avoid):
10. **Software constraints**: the numbers your program depends on, which would break if the build
    changed underneath it. List the ones that **must not change**; leave out what's easy to change
    in your code.
    - *Wheel diameter*: distance moves convert wheel turns into distance; 56 mm → 88 mm wheels makes
      every straight move about 1.6× too long.
    - *Track width* (distance between the drive wheels): turns by wheel rotation depend on it.
    - *Motor ports*: which port each motor uses, and whether its cable reaches that port.
    - *Motor directions*: a motor mounted the other way spins backwards for the same command
      (mirrored drive motors usually need one reversed).
    - *Hub orientation*: the gyro's axes and the display follow the hub; turn the hub 180° and yaw
      flips, tilt readings change sign, and the display is upside down.
    - *Attachment motors*: which port drives which PTO output, and which way is "up" or "close".

    How hard these are to change depends on your software. Some (Pybricks, for example) make it a
    one-line setting to reverse a motor or rotate the display, so the design is freer. Any
    programming environment works with this repo; just say which values are fixed for you.
    Example: "keep 56 mm wheels and 14.5 cm track width; drive motors on A and E."
    -
11. **Reference designs** (`.ldr` files in `designs/`; say which one, if any, to start from):
12. **Photos** (folder, then one line per photo: file, what it shows, and **reference** / **match** /
    **inspiration**; unlabeled = inspiration):
    - `photos/<robot-name>/top.jpg`: current robot from above, reference
13. **Missions** (which field models the robot must reach, push or lift; heights and distances):
14. **Builders and time** (experience, build deadline):
15. **Problems with past robots** (drift, caster catching, attachments falling off…):
16. **Anything else**:
