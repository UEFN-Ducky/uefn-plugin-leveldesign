---
description: "Map Content Drawer (All → Fortnite → Props / Prefabs / Devices) to real MCP search paths — walls, floors, prop kits, Creative devices, and Verse digests that list every device API"
metadata:
  order: 2
  label: "Content catalog (Props / Prefabs / Devices)"
  default_enabled: false
  load_condition: "User asks to place props, walls, floors, prefabs, galleries, Creative devices, browse Content Drawer / Fortnite catalog, or find what Fortnite assets exist to build with"
---

## Content Drawer ≠ asset mount

In the editor UI: **Content Drawer → All → Fortnite → Props / Prefabs / Devices**.

That **Fortnite** tree is a **UI gallery filter**, not a registry path. These all return empty:

- `directory="/Fortnite"`
- `directory="/Game/Props"`
- `directory="/Game/Creative/Prefabs"`
- `directory="/Game/Creative/Galleries"`

**Placeable Fortnite Creative content lives under `/Game/Creative/...`.** Always scope `search_assets` / `list_assets` there (or a subfolder below). Param is **`search=`** (not `query` / `name_filter`). Prefer `limit=10..50` + `fields=["asset_name","package_path","asset_class"]` + `offset` to page.

Spawn placeables with the **`.…_C`** path from the hit (`BlueprintGeneratedClass`), then `set_actor_label` + `set_actor_folder` + `save_current_level`.

---

## Props (walls, floors, roofs, dressing)

| Content Drawer idea | Search here | Example |
|---------------------|-------------|---------|
| Walls / doors / windows | `/Game/Creative/BuildingActors/Walls` | `search_assets(search="Wall", directory="/Game/Creative/BuildingActors/Walls", limit=20)` |
| Floors / sidewalks | `/Game/Creative/BuildingActors/Floors` | `search="Sidewalk"` or `search="CP_"` |
| Roofs | `/Game/Creative/BuildingActors/Roofs` | `search="Roof"` |
| Indoor / clutter props | `/Game/Creative/BuildingActors/Props` | `search="Chair"` / `search="Crate"` (huge — keep `limit` small) |
| Cliff / nature pieces | `/Game/Creative/Environments/Props` | `search="Cliff"` / `search="Cave"` |
| Building greebles | `/Game/Creative/Items/Building_Parts` | `search="Ring"` |
| Themed kits (castle, military, graybox…) | `/Game/Creative/Sets/<Theme>` | e.g. `GrayBox`, `MilitaryBase`, `Spooky`, `PrincessCastle`, `Oak` |
| Prop-set packs | `/Game/Creative/Sets/PropSets` | `Playgrounds`, `Primitives`, … |
| Trees / hedges | `/Game/Creative/Environments/...` | `ApolloTrees`, `ApolloHedges`, `AthenaHedges`, … |

**Browse folders** (like expanding Content Drawer):

```
list_assets(directory="/Game/Creative/BuildingActors", recursive=false, limit=50)
list_assets(directory="/Game/Creative/Sets", recursive=false, limit=50)
list_assets(directory="/Game/Creative/Sets/GrayBox", recursive=false, limit=50)
```

**Name patterns:** Creative props often use `CP_*` or theme prefixes (`GrayBox_*`, `MilitaryBase_*`). Prefer a short keyword + a **narrow `directory`** over a global `/Game` crawl.

**Do not** greybox with `/Engine/BasicShapes/Cube` when the user asked for Fortnite props — search the table above first.

---

## Prefabs / kits (Content Drawer “Prefabs”)

There is **no** `/Game/Creative/Prefabs` mount for MCP. What the drawer calls Prefabs maps to:

1. **Themed Creative kits** under `/Game/Creative/Sets/<Theme>` (and BuildingActors pieces) — place each Blueprint `_C` like a prop.
2. **Scene Graph prefabs** (entities) — different system: `skill_read_subskill("scenegraph", …)` → `create_prefab_from_entities` / `instantiate_prefab`.
3. **Playsets** (`FortPlaysetItemDefinition`, `PID_*` under `/Game/Playsets`) — item definitions, **not** the usual `spawn_actor` prop path. Prefer Sets / BuildingActors for level dressing.

Workflow for a themed kit:

```
list_assets(directory="/Game/Creative/Sets", recursive=false, limit=50)   # pick theme
search_assets(search="GrayBox", directory="/Game/Creative/Sets/GrayBox", limit=30,
              fields=["asset_name","package_path","asset_class"])
# spawn only BlueprintGeneratedClass …_C hits
```

---

## Devices (Content Drawer + Verse APIs)

Two layers — never confuse them:

| Layer | What it is | How to discover | How to place / use |
|-------|------------|-----------------|--------------------|
| **Blueprint in level** | Creative device actor | `search_assets(search="Teleporter", directory="/Game/Creative/Devices", limit=10)` or `directory="/Game/Creative"` | `spawn_actor(asset_path="…_C")` → label → folder → `inspect_creative_device` / `set_creative_device_fields` |
| **Verse API type** | `teleporter_device`, `button_device`, … | Digests (below) | `@editable` typing / `get_verse_api` — **never** `spawn_actor(actor_class="teleporter_device")` |

Device folders live under `/Game/Creative/Devices/<Name>/` (Button, Teleporter, CharacterSpawner, CaptureArea, … — 100+ folders). List them:

```
list_assets(directory="/Game/Creative/Devices", recursive=false, limit=200)
```

Deep dive: `skill_read_subskill("uefn", "creative_devices")`.

### Digests list every device API

Offline OK — no listener. **All** Epic Creative/Verse device types are in the Fortnite digest:

```
list_verse_digests()
list_verse_types(digest="fortnite", kind="class", name_filter="_device", limit=50)
# page with offset; total is hundreds — always name_filter
search_verse_digest(query="teleporter")
get_verse_api(name="teleporter_device")
```

| Digest | Use for |
|--------|---------|
| `fortnite` | Epic devices, gameplay, characters (`*_device`, modules under `/Fortnite.com`) |
| `verse` | Language + Scene Graph |
| `unrealengine` | Engine APIs |
| `assets` | **This project's** Verse-visible custom materials/meshes/prefabs |

Do **not** call unfiltered `list_verse_devices` (huge dump). Prefer `list_verse_types(…, name_filter=…)` or `search_verse_digest`.

Custom project assets in Content Browser (weapons, imported meshes): `search_assets` under the project `/Game/<Project>/…` path — digests only cover Verse-visible ids.

---

## Golden search → place loop

```
1. Pick directory from tables above (never /Fortnite)
2. search_assets(search="<keyword>", directory="…", limit=20, fields=[…])
3. Pick a BlueprintGeneratedClass path ending in _C
4. get_asset_info / get_actor_bounds after one test spawn if scale is unknown
5. spawn_actor → set_actor_label → set_actor_folder → snap_actor_to_ground (props)
6. take_high_res_screenshot → save_current_level
```

If zero hits: broaden keyword **or** step up one folder (e.g. Walls → BuildingActors → Creative), never jump to inventing cube greybox unless the user asked for greybox.
