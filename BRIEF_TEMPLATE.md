# Robot design brief

Copy this into `designs/PROJECT_brief.md`. Fill only the differences from your team profile.
Plain language is sufficient; the agent resolves part numbers and records its assumptions.

1. **Robot goal / reference style:**
2. **Wheels:** profile preset, or a description / rim and tire numbers:
3. **Drive layout:** front / middle / rear (profile default if blank):
4. **Size:** target width × length × overall height; hard maximum; permitted flexibility:
5. **Walls and ground clearance:**
   - Total wall layers, if important (separate from overall robot height):
   - Complete wall layers **below the drive axle center**, if important:
   - Clearance: about one full beam (8 mm), **at least** 8 mm everywhere, obstacle clearance, or other:
   - If layer count and clearance conflict, which governs? Clearance / layer count / ask me:
   - Notes: one layer containing the axle does not count as below it. Measure clearance to the
     actual resting contact plane, including caster-induced pitch, not the floor of an unpitched render.
6. **PTO / attachments:**
   - Number of motors, output direction, coupling, and mounting style (profile defaults if blank):
   - Must existing attachments fit? If yes, name the reference model/interface:
7. **Attachment-ID sensor:** yes/no; up/forward; existing position must be preserved?:
8. **Weights:** purpose, count, part/preset; reserve space only or model a verified mount?:
9. **Charging:** normal straight cable without removing parts (default), or other:
10. **Colors:** e.g. “blue wall beams; preserve the usual colors of constrained parts.”
    Use “must/only” for a hard requirement. Per-color inventory counts are optional.
11. **Inventory / buying policy:** team inventory by default; may any missing parts be ordered?:
12. **Software:** hub orientation, ports or other existing-code constraints:
13. **References:** `.ldr` files and/or pictures; identify the latest file to preserve:
14. **Other preferences:**

Common building defaults belong in the team profile and DESIGN_RULES, not in repeated user prompts:
minimize rare/expensive alternating-hole beams where ordinary beams and small perpendicular
connectors work; use rigid, continuous front-to-rear motor bracing rather than short pivot links.

Example of precise wall placement: “Use six full wall layers, with three complete layers below
the drive axle. Treat about one beam of ground clearance as a preference.” This is different from
“Maintain at least 8 mm under every wall edge”; the agent must check whether both are feasible.
