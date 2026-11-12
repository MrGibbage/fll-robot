# fll-robot

Rules, a parts catalog and validation tools that let an AI coding agent (Claude Code, Codex, and
similar) help design **FIRST LEGO League** competition robots: SPIKE Prime, studless Technic,
modeled in **Stud.io**.

The "prompt" is the whole repository:

| File | For | What it is |
|---|---|---|
| `AGENTS.md` (+ `CLAUDE.md`) | the AI | Workflow, how to write `.ldr` files, how to write new validation tools |
| `DESIGN_RULES.md` | both | Glossary, coordinates, feasibility limits, structural rules, the design procedure, checks |
| `BRIEF_TEMPLATE.md` | you | The design inputs for a new robot: wheels, drive layout, size limits, PTO, weights… |
| `profile/TEAM_PROFILE.example.md` | both | One team's standing choices; copy to `TEAM_PROFILE.md` (git-ignored) and make it yours |
| `profile/inventory.example.csv` | both | Example parts inventory by tray; copy to `inventory.csv` and edit |
| `PARTS_CATALOG.md` | both | ~100 likely parts: size, through-holes per direction, built-in pins, tray, notes (generated) |
| `tools/` | the AI | Python checks: connections, collisions (incl. tires), brick bond, pins, symmetry, hub clearance, parts owned, rendering |

## How it works

1. You fill in a brief and give the agent your past robots as `.ldr` exports (in `designs/`, which
   is git-ignored, so your designs stay private).
2. The agent checks the brief is feasible, designs the robot, writes an `.ldr`, and runs
   `tools/run_checks.py` until clean.
3. You import it into Stud.io (File → Import → LDraw), look, and send back screenshots or photos.
   The agent fixes what you find, and when a problem slipped past the checks, it **writes a new check
   first**.

The rules came out of designing a real robot this way. Every rule and tool exists because something
went wrong once.

## Setup

```bash
git clone https://github.com/MrGibbage/fll-robot
cd fll-robot
./setup.sh                 # Python venv + downloads the official LDraw parts library into lib/
```

Recommended: copy your **own** Stud.io parts library to `lib/studio-ldraw` (zip the `ldraw` folder in
your Stud.io install). It has the SPIKE Prime hub and other parts the official library lacks. It
can't be redistributed, so it isn't included.

Then:

```bash
cp profile/TEAM_PROFILE.example.md profile/TEAM_PROFILE.md     # edit for your team (git-ignored)
cp profile/inventory.example.csv  profile/inventory.csv        # edit to match your trays (git-ignored)
mkdir designs                                                   # put your .ldr exports here
FLL_CATALOG_OUT=my_catalog.md .venv/bin/python tools/catalog.py  # your catalog: your inventory + usage in designs/
.venv/bin/python tools/run_checks.py designs/my_robot.ldr       # try the checks on an existing robot
```

Then open the repository in your agent and point it at `AGENTS.md` with a filled-in brief.

Paths can also come from environment variables, to keep your private files outside the clone:
`LDRAW_LIB`, `STUDIO_LIB`, `FLL_INVENTORY` (CSV or .xlsx), `FLL_DESIGNS`, `FLL_CATALOG_OUT`.

## Requirements

Python 3.10+, `numpy`, `matplotlib` (and `openpyxl` for an `.xlsx` inventory). No binary files are
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
