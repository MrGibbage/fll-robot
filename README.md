# fll-robot

Rules, a parts catalog and validation tools that let an AI coding agent (Claude Code, Codex, and
similar) help design **FIRST LEGO League** competition robots: SPIKE Prime, studless Technic,
modeled in **Stud.io**.

The "prompt" is the whole repository. **People: start at [Guide for people](#guide-for-people-what-to-prepare).**

| File | For | What it is |
|---|---|---|
| `AGENTS.md` (+ `CLAUDE.md`) | the AI | Workflow, how to write `.ldr` files, how to write new validation tools |
| `DESIGN_RULES.md` | both | Glossary, coordinates, feasibility limits, structural rules, the design procedure, checks |
| `BRIEF_TEMPLATE.md` | you | The design inputs for a new robot: wheels, drive layout, size limits, PTO, weights, photos… |
| `profile/TEAM_PROFILE.example.md` | both | One team's standing choices; copy to `TEAM_PROFILE.md` (git-ignored) and make it yours |
| `PARTS_AVAILABLE.csv` | both | The parts available to design with (one FLL team's collection, by category) |
| `PARTS_CATALOG.md` | both | Every part in that list: size, through-holes per direction, built-in pins, notes (generated) |
| `tools/` | the AI | Python checks: connections, collisions (incl. tires), brick bond, pins, symmetry, hub clearance, parts owned, rendering |

## How it works

1. You describe the robot you want in a **brief**, and give the agent your past robots (`.ldr`
   exports) and photos.
2. The agent checks the brief is feasible, designs the robot, writes an `.ldr` file, and runs
   `tools/run_checks.py` until it's clean.
3. You open the `.ldr` in Stud.io, look it over, and send back screenshots and comments. The agent
   fixes what you find. When a problem slipped past the checks, it **writes a new check first**.

The rules came out of designing a real robot this way. Every rule and tool exists because something
went wrong once. Expect a first design you can open and critique, then several rounds of fixes, not a
finished robot in one go.

## Setup

```bash
git clone https://github.com/MrGibbage/fll-robot
cd fll-robot
./setup.sh                 # Python venv + downloads the official LDraw parts library into lib/
```

Recommended: copy your **own** Stud.io parts library to `lib/studio-ldraw` (the `ldraw` folder in
your Stud.io install). It has the SPIKE Prime hub and other parts the official library lacks. It
can't be redistributed, so it isn't included.

## Guide for people: what to prepare

Everything below lives in folders git ignores, so none of your team's work ends up in the
repository by accident.

| What | Where it goes | How |
|---|---|---|
| **Team profile** (once per team) | `profile/TEAM_PROFILE.md` | Copy `profile/TEAM_PROFILE.example.md` to that name and edit it |
| **Brief** (one per robot) | `briefs/<robot-name>.md`, e.g. `briefs/2026-big-wheels.md` | Copy `BRIEF_TEMPLATE.md` and fill it in |
| **Past robots** | `designs/` | Stud.io: File → Export As → LDraw (`.ldr`). Name them so you can refer to them, e.g. `2025-season-robot.ldr` |
| **Photos** | `photos/<robot-name>/` | Name each file for what it shows: `top.jpg`, `bottom.jpg`, `front-left.jpg`, `pto-closeup.jpg` |
| **Parts list** (only if yours differs) | `profile/parts.csv` | Copy `PARTS_AVAILABLE.csv` and add or delete rows |

```bash
mkdir -p briefs designs photos
cp profile/TEAM_PROFILE.example.md profile/TEAM_PROFILE.md
cp BRIEF_TEMPLATE.md briefs/2026-big-wheels.md
.venv/bin/python tools/run_checks.py designs/2025-season-robot.ldr   # optional: see what the checks say about a robot you know
```

### The team profile: your standing style

Write the things that stay the same from robot to robot: how you mount motors, how attachments
connect (the PTO), where the color sensor goes, how you charge the hub, how you use weights. The
example is a real team's profile; keep what matches, change what doesn't, delete what you don't care
about. A brief only needs to say what's **different** for one robot.

### The brief: this robot

Fill in what you know and leave the rest blank; blanks fall back to the team profile, and the agent
will tell you which defaults it used. You don't need everything up front: much of it gets settled
during the rounds and the real build ("the drive cables don't reach port A"), and you add it then. Be specific where it matters to you: "56 mm wheels, max
width 22 studs, the existing attachments from 2025 must still fit" helps more than "a fast robot".
Write **why** when you have a reason ("weights counterbalance heavy front attachments"): the agent
makes better trade-offs when it knows the purpose.

### Photos: inspiration or a copy?

Photos help a lot. They show how real parts sit, how much things flex, where cables run and what a
robot looks like from underneath, none of which is in a model file. But an agent **can't reliably
rebuild a robot part-for-part from photos**: hidden pins and parts inside the structure aren't
visible. So say what each photo is for, in the brief's photo section:

- **Reference:** "this is our current robot", so the agent knows the starting point. If you want
  the new robot to *be* this one with changes, also give its `.ldr` export. That's what the agent
  edits.
- **Match:** "copy this specific feature", e.g. how the weight sits in the corner pocket, or how
  attachments latch. The agent reproduces the idea, fitted to the new design.
- **Inspiration:** "something like this", e.g. another team's robot or a mechanism you saw. The agent
  borrows the idea and follows your rules and parts list, not the photo's exact build.

With no label, the agent treats a photo as **inspiration** and asks before copying anything exactly.

Good photos: plain background, good light, the whole robot in frame, and at least top, bottom, front,
back and one side. Add close-ups of anything tricky. Stud.io screenshots work the same way and are
better for showing a problem in a model: collisions show as transparent parts.

### The first prompt

Open the repository folder in your agent (Claude Code, Codex, …) and start with something like:

> Read AGENTS.md and follow it. Design a new robot from `briefs/2026-big-wheels.md`. Our team
> profile is `profile/TEAM_PROFILE.md`. Reference designs are in `designs/`: start from
> `2025-season-robot.ldr`, which is our current robot. The photos in `photos/2026-big-wheels/` are
> labeled in the brief. Before you design, tell me if anything in the brief is infeasible or
> unclear. Write the model to `out/`, run the checks, and give me the bill of materials.

Keep it short: the brief and profile carry the detail. Point the agent at files rather than pasting
their contents. When the agent asks a question, answer it in the brief too, so the next robot
starts with it.

### After the first design

1. Import the `.ldr` into Stud.io (File → Import → LDraw) and look at it from every side.
2. Tell the agent what's wrong **using the robot's coordinate language**: `R3 F1 lvl2` means 3 studs
   right of center, front row, second level up (see `DESIGN_RULES.md` §2). Attach screenshots.
3. Expect several rounds. When you state a new preference ("never use 1L beams"), ask the agent to
   add it to your team profile (team-specific) or `DESIGN_RULES.md` (general), so it sticks.
4. Build it for real and send photos. Real bricks find things the model can't (§15).

### What else helps

- **The season's missions:** which models the robot must reach, push or lift, and what heights
  and distances matter. A photo of the field mat with the target areas marked is plenty.
- **Size rules:** this season's Robot Game Rules (launch area, height limit). Write the numbers in
  the brief.
- **Existing attachments** that must still fit: their `.ldr` exports, or photos and measurements of
  the part that meets the robot.
- **Drive code** that must keep working: wheel diameter, track width, motor ports, hub orientation.
- **The builders:** their experience and how much time there is to build. A simpler robot that gets
  built beats a clever one that doesn't.
- **What went wrong before:** "the old robot drifted left", "the caster caught on the mat edge",
  "attachments fell off on fast turns". The agent can design against a problem it knows about.
- **Colors:** if you sort by color or want a team look, say so.

## The parts list

`PARTS_AVAILABLE.csv` is the set of parts the agent may design with: one real FLL team's
collection (SPIKE Prime set plus extras), grouped by category. The agent treats anything not on it as
"needs ordering". If your parts differ, copy it to `profile/parts.csv` and edit; the tools use yours
when it exists. Columns are `part_number,category,part_name`. `part_number` is the LDraw id; it may
be blank when the name holds the numbers, e.g. `Axle 16 (50451 / 69732)`. Run
`tools/partslist.py` to see how each row resolves, then `tools/catalog.py` to rebuild the catalog.
To get usage counts from your own designs, write your catalog elsewhere:
`FLL_CATALOG_OUT=my_catalog.md .venv/bin/python tools/catalog.py`.

Paths can also come from environment variables, to keep your private files outside the clone:
`LDRAW_LIB`, `STUDIO_LIB`, `FLL_PARTS`, `FLL_DESIGNS`, `FLL_CATALOG_OUT`.

## Requirements

Python 3.10+, `numpy`, `matplotlib`. No binary files are
stored in the repository; the parts library is downloaded by `setup.sh`.

## Limits

The checks reason about geometry: holes, pins, collisions, clearances. They don't model stud
connections, strength under load, build order, cable routing, or parts Stud.io can't place (see
`DESIGN_RULES.md` §15). A person with real bricks still has the last word.

## Credits and trademarks

- Parts geometry: the [LDraw](https://www.ldraw.org) parts library (CC BY 4.0), downloaded at setup.
- LEGO®, SPIKE™ and Technic™ are trademarks of the LEGO Group. FIRST® and FIRST® LEGO® League are
  trademarks of FIRST. Stud.io is a BrickLink product. This project isn't affiliated with or
  endorsed by any of them.
- Code and documentation: MIT License (see `LICENSE`).
