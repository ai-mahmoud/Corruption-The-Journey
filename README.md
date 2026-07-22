# Corruption: The Journey — Chapter 0 (complete)

The Hatchling's entire Chapter 0, start to finish: Cutscene 1 (The World),
Cutscene 2 (The Hatching), Beat 1 (Waking), Beat 2 (The Forest Floor),
Beat 3 (First Threat), Beat 4 (Awakening), and Beat 5 (The Pull Toward the
Master) — tight run/jump movement, a smooth-follow camera, contact-based
absorption, the wordless "corruption does not hurt me" discovery beat, her
first real threat (dodge under pressure, a soft-fail stumble where an
attack would be, a telegraphed beast) becoming the absorption-unlock beat
instead of a death, a real 2-heart HP system with checkpoints and
save/load, the game's first real verticality, and the reveal ending on the
one deliberate warm-palette break in the whole game. See `Corruption: The
Journey — Chapter 0.md` for the script this is built from — the game
stops exactly where the script says "Chapter 1 begins here," with an
honest end card rather than fabricated content.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate the placeholder sprites

Run once (already done, but re-run any time after editing a generator):

```bash
python tools/generate_hatchling_sprite.py
python tools/generate_enemy_sprite.py
python tools/generate_egg_sprite.py
python tools/generate_undergrowth_sprite.py
python tools/generate_heart_icon.py
python tools/generate_master_sprite.py
python tools/generate_room_backgrounds.py
python tools/generate_cutscene_backgrounds.py
python tools/generate_sound_effects.py

# Optional: overwrites the Hatchling sprite above with a third-party pack
# instead -- needs that pack's zip locally, see "The Hatchling's sprite"
# further down. Skip this to keep the fully-procedural design.
python tools/import_female_adventurer_sprite.py
```

The sprite generators write PNG + JSON pairs into `assets/sprites/`; the
background generators write plain PNGs into `assets/backgrounds/` (no
per-entity anchor/frame metadata needed for a static backdrop). Game code
never draws raw rectangles for any of this — it loads the generated PNGs
and scales them up with nearest-neighbor scaling for crisp pixel edges.
`generate_sound_effects.py` is the same idea for audio — see "Audio"
below.

## Building a standalone executable

Packaging is build-time only, so it's kept out of `requirements.txt`
(which lists what the game itself needs to *run*):

```bash
pip install pyinstaller
pyinstaller CorruptionTheJourney.spec
```

This produces `dist/CorruptionTheJourney`, a single-file executable with
`assets/` bundled inside it — nothing else needs to ship alongside it.
`CorruptionTheJourney.spec` (checked into the repo) is the source of
truth for the build, not the `pyinstaller` CLI flags — it pins
`console=False` (no terminal window popping up next to the game on
Windows) and bundles `assets` via `datas`. `src/settings.py` resolves
asset paths through `sys._MEIPASS` when running as a frozen build, so the
same code path works whether it's launched via `python main.py` or as the
packaged executable.

**Windows build:** PyInstaller doesn't cross-compile, so a `.exe` has to
actually be built on Windows — either the same three commands above, run
on a Windows machine, or `.github/workflows/build-windows.yml`, a manual
GitHub Actions workflow (run it from the Actions tab, or
`gh workflow run build-windows.yml`) that builds on a real
`windows-latest` runner and uploads `CorruptionTheJourney.exe` as a build
artifact — no Windows machine needed.

## Run the game

```bash
python main.py
```

It opens on the title screen (`src/title_scene.py`) — **New Game** (or
**Continue**, shown only when a save exists) / **Exit**. New Game plays
Cutscene 1 (auto-advancing narration; any key advances a card early), then
Cutscene 2 (the egg hatching, no input), then all four playable rooms in
sequence (Waking Hollow → Forest Floor → Clearing → Deeper Forest),
ending on the Master reveal and an honest end-of-content card. Continue
skips straight to the last checkpoint. Choosing New Game with a save
already present asks for confirmation first — it erases that save.
**Esc or X skips the current cutscene**; during gameplay, **Esc opens the
pause menu** (Resume / Settings / Hints / Exit).

**Controls:** Arrow keys / WASD to move, Space (or Up/W) to jump — tap for a
short hop, hold for a full jump. Left Shift to dodge (briefly invulnerable,
short cooldown). J is the attack key — she has no attack yet, so it just
leaves her briefly, vulnerably stumbling; that's intentional, not a bug.
Esc pauses; in the pause menu, Up/Down (or W/S) to navigate, Enter/Space to
select, Esc to back out. F11 toggles fullscreen at any time, in any scene.

## Layout

```
main.py     → entry point
src/        → game code: scenes, entities, physics, camera
assets/     → generated sprite PNGs + JSON metadata (not hand-edited)
tools/      → Pillow scripts that generate the assets above, run offline
data/       → hardcoded room/level/narration content (plain data, no pygame types)
the_journey/→ earlier abandoned prototypes, kept for reference only
```

### Scenes

`src/scene.py` defines the minimal interface (`handle_event` / `update` /
`draw`) that `Game.run()` switches between — a scene hands off to the next
one by returning it from `update()`. `Game()` always opens on
`TitleScene` (`src/title_scene.py`); from there, New Game leads into
`CutsceneWorldScene` → `CutsceneHatchingScene` → `GameplayScene` (and
Continue skips straight to `GameplayScene` at the saved checkpoint).

`GameplayScene` is room-data-driven rather than one class per beat — see
the optional keys in `data/rooms.py` (`enemy_spawn`, `hazards`,
`attack_beast_spawn`, `exit_zone` + `next_room`, `checkpoint_zone`,
`reveal_zone`, `log_obstacle` + `tutorial_prompt`). `TEST_ROOM` (the
original movement/absorption sandbox), `WAKING_HOLLOW` (Beat 1),
`FOREST_FLOOR` (Beat 2, hazards), `CLEARING` (Beat 3, an attack beast),
and `DEEPER_FOREST` (Beat 5) all load through the same scene class,
chained via `next_room`: Waking Hollow → Forest Floor → Clearing →
Deeper Forest.

`src/hazard.py`'s `CorruptedPlant` is *not* the absorption ability — it's
a separate, much quieter reaction (proximity-based withering that's
reversible, and a quick no-consequence death fade on contact, with zero
effect on the player: no lock, no flash, no sound). Kept as its own class
rather than an `Enemy` variant since none of `Enemy`'s patrol/absorption
behavior applies.

`src/attack_beast.py`'s `AttackBeast` is also deliberately not an `Enemy`:
touching an `Enemy` always triggers absorption (`GameplayScene.
_check_absorption`), but she hasn't discovered that ability yet at this
point in the story, so this beast's contact means a hit reaction instead
— never a kill. It's a small state machine (idle → telegraph → strike →
recover) with a generous, escalating wind-up before it strikes, reusing
the existing enemy sprite (the script wants its *motion* to read as
wrong, not its silhouette).

`Player` gained three new states for Beat 3 (`src/player.py`): `DODGE`
(brief, invulnerable, on a real cooldown — not just feel-tuning; Beat 4
needs a moment where dodging genuinely isn't an option, so unlimited
dodging would be the wrong foundation, not just "too easy"), `STUMBLE`
(pressing the attack key she doesn't have yet — vulnerable, unlike dodge),
and `HIT` (a beast strike landing — knockback plus brief i-frames so one
strike can't hit her twice). `Player` itself needed *no changes* for
Beat 4 — `start_absorb()`, `is_absorbing`, and `begin_hit_reaction()` are
reused completely as-is; Beat 4 is new consequences wired around existing
player behavior, not new player behavior.

`src/pause_menu.py`'s `PauseMenuScene` wraps whatever scene was active when
Esc was pressed during gameplay and draws it frozen (no `update()` calls
reach it while paused) behind a dim overlay. "Resume" just hands that exact
instance back — nothing is reconstructed, so player/camera/enemy state is
untouched by pausing.

### Hearts, the absorption-unlock moment, checkpoints, and save/load

`src/game_progress.py`'s `GameProgress` (`max_hearts`, `current_hearts`,
`absorption_unlocked`, `checkpoint_room_key`) is the one thing that
survives both room transitions *and* death/respawn — everything else
(`Player`, `GameplayScene`, the beast, hazards) is rebuilt fresh each
time. It's constructed once in `Game.__init__` (fresh, or loaded from
`savegame.json` via `src/save_system.py`) and threaded through every scene
constructor from there, cutscenes included.

Getting hit by `CLEARING`'s beast now costs a heart
(`GameplayScene._apply_beast_hit`) — except the first hit that would take
her last one, which is intercepted into Beat 4's absorption-unlock beat
(`_trigger_absorption_unlock`) instead of a death: `start_absorb()` +
`attack_beast.begin_absorbed()` (reusing the existing absorb-lock/flash
beat as-is), a brief slow-motion window ("time can slow slightly, for
weight" — `UNLOCK_SLOW_MOTION_FACTOR`), a level-up (2 → 3 max hearts,
ending at 2/3 — a scripted outcome, set directly rather than derived), and
a cosmetic "absorption unlocked" banner. From that point on, death is
real: running out of hearts respawns at `checkpoint_room_key`, healed.

`data/rooms.py`'s `ROOM_REGISTRY` maps each room's `"key"` back to its
data dict, so save files and respawns can name a room without serializing
one. `CLEARING`'s `checkpoint_zone` (same spot as its `exit_zone`) heals
to full and writes the save file on entry. `TitleScene` (`src/title_scene.py`)
checks for that file: if present, it offers **Continue** (straight to the
checkpoint, skipping both cutscenes) alongside **New Game** — which, if a
save exists, asks for confirmation before erasing it and starting fresh
from Cutscene 1.

### Beat 5: verticality, a gated-off path, and the reveal

`DEEPER_FOREST` is the first room where `world_height` (760) differs from
the window height (540) — every earlier room was exactly 540 tall, so the
camera's vertical follow (`src/camera.py`) has technically existed since
the vertical slice but never actually had anything to pan *to* until now.
A 3-jump ascending platform sequence levels out onto a walkway; one ledge
sits far above anything reachable — visible, never explained, never
reachable, "most paths are still gated shut here" done through geometry
alone, no ability-gating system built. (An earlier version of this
sequence used horizontal gaps that were actually impossible to clear —
caught by driving the jump headlessly and checking she landed *on* the
platform rather than fell through to the always-continuous ground below
it, not just that she ended up in the right x-range.)

`"reveal_zone"` (`GameplayScene`) is a new kind of trigger — unlike
`exit_zone`/`next_room` (always `GameplayScene` → `GameplayScene`), it
always leaves gameplay entirely for `src/cutscene_master.py`'s
`CutsceneMasterScene`: the Master training, ember flickering between two
frames, against the one deliberate palette break in the whole game (warm
amber/orange — `tools/generate_cutscene_backgrounds.py`'s
`generate_master_reveal_background`; every other background is grey-black/
corrupted). A hard cut to black, then an honest end card — the script says
"Chapter 1 begins here," but only Chapter 0 was ever in scope, so that's
where the built game actually stops.

### Art pass: bigger sprites, real animation, and generated backgrounds

Every sprite went through a second pass after the initial vertical slice,
gaining shading and, for the Hatchling, real animation:
`idle`/`run_a`/`run_b`/`jump`/`fall` poses with an actual alternating-
stride run cycle (one leg forward and bent, one planted), not a symmetric
stance wobble — `Player.draw()` (`src/player.py`) picks the frame by
state, cycles the run frames on a timer, and flips horizontally for
facing direction.

That pass also revealed a real bug: **collision size used to come
directly from the sprite's pixel dimensions**, so a more detailed sprite
silently grew the hitbox and broke every room's tuned jump clearances and
choke points. Fixed by decoupling them —
`settings.PLAYER_COLLISION_WIDTH/HEIGHT` (and the `ENEMY_`/`HAZARD_`
equivalents) are fixed constants independent of whatever the sprite
generator produces; `draw()` in `player.py`/`enemy.py`/`hazard.py`/
`attack_beast.py` centers the sprite over the fixed collision box instead.
A follow-up pass then found the *sprite* side of that same coupling —
the visual sprites had grown to ~2.5–3x their own collision boxes and
were visibly clipping through ceilings/logs despite the hitbox itself
being correct — so the Hatchling was rebuilt at native 12×20 * scale 3
(an exact 36×60 match to her hitbox), and the enemy/undergrowth sprite
scales were reduced to close matches too. The Hatchling was also
redesigned in that pass (longer hair, a tapered waist/hip silhouette) to
read clearly as female.

Rooms and all three cutscenes now load a generated background image
(`tools/generate_room_backgrounds.py`, `generate_cutscene_backgrounds.py`)
instead of a flat color fill — a blocky/banded gradient sky (deliberately
not a smooth gradient, to match the flat-shaded sprite style) plus layered
tree/root silhouettes and sparse ash specks, loaded 1:1 with world space
(no parallax scroll-speed math). Each room/cutscene seeds its own RNG, so
regenerating reproduces the same image. `master_reveal.png` is the one
exception to the grey-black palette everywhere else (see Beat 5, above).

This pass also went through one critique-and-fix cycle (a separate review
pass compared every generated asset against the game's own style rules and
flagged concrete issues, which were then fixed): a torso/leg gap in the
Hatchling's jump/fall poses, enemy feet floating above the ground line,
the run cycle inverting the character's established left/right shading
every other frame, the egg's palette nearly duplicating the corrupted-
enemy palette, backgrounds sitting too dark to show their own depth
banding, and a background-width rounding bug that could show a thin
unrendered edge at max camera scroll.

### The Hatchling's sprite: swapped for a third-party pack

`assets/sprites/hatchling.png/json` currently comes from "The Female
Adventurer - Free," a third-party asset pack, not the procedural
generator above — `tools/generate_hatchling_sprite.py` still exists and
still works (re-run it to go back to the original design), but
`tools/import_female_adventurer_sprite.py` runs after it and overwrites
its output.

**Two caveats, both accepted knowingly, not overlooked:**
- **Perspective mismatch.** The pack is a 3/4 top-down RPG asset (8
  compass-direction facings — `Idle_Down`, `Walk_Left_Up`, etc.), not a
  side-view platformer sprite like literally everything else in this game
  (enemy, hazard, egg, Master). `Right_Down` was picked as the
  least-mismatched facing and flipped horizontally for left, same as the
  procedural sprite before it, but it's still a visibly different camera
  convention grafted onto a side-view game — a deliberate compromise, not
  a bug.
- **Unknown license.** The pack's zip has no LICENSE or readme file
  inside it, so its redistribution terms are unverified. It's excluded
  from this repo's MIT grant (see `LICENSE`) the same way the three music
  tracks are, and the raw pack itself is never committed here — only the
  five cropped frames the game actually uses
  (`tools/import_female_adventurer_sprite.py` reads straight out of the
  original zip via Python's `zipfile`, so the full pack never touches the
  working tree). Track down the actual terms before sharing this build
  beyond a small private group.

The import script crops `idle` (1 frame), `run_a`/`run_b` (2 walk-cycle
frames), and `jump`/`fall` (2 frames from the jump strip) out of their
6-frame animation strips, then crops all five to one *shared* bounding
box (the union of each frame's own opaque pixels) rather than each
frame's individual tight crop — that's what keeps her from visibly
jittering side to side as her pose changes, since `Player.draw()`
bottom/center-aligns each frame by its own width/height with no separate
per-frame offset.

## Notes on the movement tuning

All physics constants live in `src/settings.py`. The feel: faster
deceleration than acceleration (crisp stops), asymmetric gravity (falling
pulls harder than rising, ~1.6x), and jump height that varies with how long
you hold the button (tap vs. hold), on top of coyote time (`COYOTE_TIME`)
and jump buffering (`JUMP_BUFFER_TIME`). If it feels off, that file is the
one to tune — nothing else hardcodes these numbers.

## Deliberate placeholders (not bugs)

- Every sprite/background except the Hatchling is procedurally generated
  pixel art (Pillow scripts building colored-rectangle sprite sheets), not
  hand-painted or AI-generated images — a deliberate pipeline choice so
  those assets are scriptable, regeneratable, and reviewable as code, not
  a capability gap being hidden. The Hatchling herself is a hand-drawn
  third-party sprite pack, swapped in on top of that pipeline (see "The
  Hatchling's sprite" above) — including its perspective mismatch and
  unresolved license, both knowingly accepted, not overlooked.
- Backgrounds don't yet have the script's "drifting particulate corruption
  like ash" as actual motion, or plants that "pulse... out of sync" — the
  ash specks and silhouettes are static per room, not an animated particle
  system, since none exists yet.
- Cutscene 1 and Cutscene 2 are deliberately silent (no music, no SFX),
  matching the script's "near-total silence" through the opening; audio
  starts once gameplay begins.
- She can walk past `CLEARING`'s beast toward the exit without engaging it
  at all; nothing forces the encounter to "complete," and reaching the
  checkpoint without ever being hit is fine too (it saves/heals regardless
  of whether absorption has been unlocked).
- The Beat 5 end card really is the end — there's no Chapter 1 content
  behind it, by design (see the top of this README).
- The pause menu's Settings screen only has a music volume slider so far —
  no rebindable keys yet. Hints is real content (a static control
  reminder, including F11 for fullscreen), not a placeholder.

## Audio

Three looping tracks, picked by *role* rather than by scene, live in
`assets/audio/` (`exploration.mp3`, `threat.mp3`, `warmth.mp3`) and are
generated content, not part of this repo's MIT license (see `LICENSE`) —
swap them for anything you have the rights to before distributing further.
`src/audio.py` is a thin wrapper over `pygame.mixer.music`: rooms opt into
a track via `data/rooms.py`'s `"music"` key (`"exploration"` for
Waking Hollow/Forest Floor/Deeper Forest, `"threat"` for the Clearing's
beast encounter), and `CutsceneMasterScene` switches to `"warmth"` for the
Master reveal, fading out into the hard cut to black. Since
`pygame.mixer.music` can only play one stream at a time, a track change is
a fade-out-then-fade-in rather than a true crossfade — good enough at this
scale, and avoids pulling in a second audio dependency.

Sound effects (`assets/audio/sfx/*.wav`) are procedurally synthesized by
`tools/generate_sound_effects.py` — sine sweeps, filtered noise, and small
bell-like chimes built with plain numpy (`tools/audio_synth.py`), no
recorded or licensed audio, no synthesis at runtime. Same "scriptable,
regeneratable, reviewable as code" pipeline as the Pillow sprite
generators, just audio instead of pixels, and unlike the three music
tracks these *are* covered by this repo's MIT license. Ten effects, each
tied to a specific player/world event rather than a scene: `jump`/`land`
(the moment a jump starts/lands), `dodge`/`stumble` (her two locked
reaction states with no attack), `hit` (a beast strike landing), `absorb`
(contact-absorbing an `Enemy`), `unlock` (the one-time absorption-unlock
beat — deliberately bigger and longer than `absorb`), `checkpoint`
(saving), and `menu_move`/`menu_select` (pause menu and title screen
navigation). `src/audio.py`'s `play_sfx()` plays these as one-shot
`pygame.mixer.Sound`s on their own channels, independent of the looping
`pygame.mixer.music` track, so they never interrupt or get interrupted by
the background music.
