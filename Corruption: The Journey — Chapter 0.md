# Corruption: The Journey — Chapter 0 (Game Script)

*Prologue: Birth*

---

## CUTSCENE 1 — The World

**Format:** Pre-rendered or in-engine cinematic. No player input. Visuals: sweeping shots of ruined cities reclaimed by nature, mana-lit sigils flickering in old stonework, a distant silhouette of a robed figure surrounded by light, then consumed by shadow-static.

**Narration (voiceover, slow, mythic cadence):**

> Before memory, there was mana.
> It moved through every living thing — root and vein alike — and from it, the world built its wars, its wonders, its gods of small renown.
>
> Then came a second hunger. One that did not glow, but consumed.
>
> It had no name the old tongues could hold, so they simply called it Corruption.
>
> It did not fight for territory. It did not fight for belief. It only spread, and where it passed, living things forgot how to be alive.
>
> Armies broke against it. Kings knelt to it. Then, from nowhere anyone could account for, a single warrior rose carrying nothing but Light — the rarest of all mana — and did what no army could.
>
> They pushed it back.
>
> Cities rebuilt. Orders were founded to keep the old wound closed. And the warrior who saved them all simply… disappeared.
>
> No grave. No farewell.
>
> Without them, Corruption crept back — not all it had lost, but enough. Enough to remind the world it had never truly been beaten.
>
> Scholars found a mercy after that: mana, condensed beyond reason, could slow the creeping dark. Not stop it. Slow it.
>
> So the borders hold, inch by inch, year by year — every edge of the world still bleeding, only slower now than before.
>
> At this pace, they say, the world has perhaps a thousand years left to it.
>
> Perhaps less.

**Visual button:** Screen fractures to black, briefly showing a flash of a cracking eggshell — smash cut to Cutscene 2.

---

## CUTSCENE 2 — The Hatching

**Format:** In-engine cinematic, camera close and intimate, unlike the wide mythic framing of Cutscene 1.

**Visuals:** A single egg, veined with faint dark light, resting in a hollow of dead roots deep in a corrupted forest. The canopy above is choked with grey-black rot. No wind. No birdsong. The world here has gone still in the specific way only Corruption produces — not peaceful, just paused.

The egg trembles. A hairline crack spiders across its surface. No score swells — just a held silence, then the small, wet sound of shell splitting.

A hand pushes through first. Human. Unblemished. Pale in the dim light.

**No narration here.** The player's first sensory information should be diegetic only — sound design of breathing, cracking shell, distant forest ambience. This is intentional: nobody is going to explain her to the player. She isn't explained to herself either.

**Cutscene ends** on her eyes opening for the first time — a hard cut to gameplay as her point of view resolves into player camera control.

---

## PLAYABLE SEGMENT — "First Breath"

### Beat 1: Waking

**Setting:** The hatching hollow, small, enclosed by roots and fallen logs — a natural tutorial box.

Player regains control mid-motion — she's already lying on the forest floor, control handed over as she stirs. This avoids a dead "stand up" animation lock feeling like a loading screen.

**Tutorial prompts (diegetic, minimal UI):**
- Move: guided by a sliver of dim light between two roots — the only visible way out of the hollow.
- Look: camera drifts naturally toward movement, no forced prompt needed beyond first analog nudge.
- Basic climb/traverse: a fallen log blocks the direct path; prompt appears only once, first time she nears it.

No dialogue. No inner monologue text yet. She doesn't have words for anything, so the game shouldn't give her any.

### Beat 2: The Forest Floor

**Setting:** A short, mostly linear corridor of corrupted forest — enough space for 2–3 minutes of unhurried movement. Visually: grey-bled color palette, drifting particulate corruption in the air like ash, distorted plant silhouettes that pulse faintly out of sync with each other.

**Discovery moment (core to your "learn by doing" philosophy):**
A patch of corrupted undergrowth blocks a narrow path — visually threatening, animated like it might lash out. Player has no way around it except through.

- If the player hesitates near it: it doesn't react with hostility. It just... withers slightly wherever she's closest to it, like her mere presence unsettles it.
- If the player walks into/touches it: it recoils and dies quietly on contact. No sound cue of harm to her. No damage taken.

This is the entire lesson, delivered without a single line of text: *Corruption does not hurt me.* The player should be allowed to test this themselves — maybe even backtrack and touch another corrupted plant just to confirm it wasn't a fluke.

### Beat 3: First Threat

**Setting:** A small clearing, wider sightlines, the first real combat space.

**Encounter:** A weak corrupted beast (design note: something small and doglike or insectile — not yet a dangerous silhouette, but wrong in its movement, twitchy and arrhythmic) notices her and attacks.

**Mechanical beat:**
- Dodge prompt introduced here under real pressure — first attack should be telegraphed generously (long wind-up) so the tutorial teaches through survival, not failure.
- She has no attack input yet. If the player tries to attack (likely instinct), nothing happens — a soft failure state, maybe a small vulnerable stumble animation, reinforcing that she has no conventional way to fight back yet.
- The beast should not be able to actually kill her in this encounter — cap damage or give her an unseen safety net — because the real teaching moment is next.

### Beat 4: Awakening (Basic Absorption)

**Trigger:** After a few dodges, the beast corners her or she's forced into a moment with no dodge option remaining.

**Beat:** Instead of a death, her hand instinctively snaps out and makes contact with the creature. Time can slow slightly here for weight. The beast's corruption visibly drains into her — a slow pull of grey-black particulate flowing from its body into her open palm — and it collapses, inert, unmade rather than killed in the traditional sense.

**This is the ability unlock moment.** UI should introduce the absorption prompt/icon here for the first time, tied to this exact input — she's now armed with her first real tool, taught entirely through a moment of desperation rather than a menu screen.

Give the player a small beat of stillness afterward — no immediate next objective — so this can land. Maybe she looks at her own hand. No dialogue needed; a simple animation beat is enough.

### Beat 5: The Pull Toward the Master

**Setting:** Deeper forest, denser corruption, verticality starting to open up (early metroidvania shape-of-things-to-come, even if most paths are still gated shut here).

**Guidance:** A distant flicker of orange light through the trees — warm, out of place against the grey-black palette everywhere else. Optionally paired with a faint sound (crackling fire, or the rhythmic thud of someone striking a training post) to pull the player's attention without a waypoint marker.

This should read as the first "different" thing she's encountered — everything so far has been dead, still, or hostile. This is warmth.

**Chapter ends** as she pushes through a final curtain of hanging roots into a small clearing — and sees him for the first time: a man, mid-strike against a scorched training post, his motions sharp and controlled, small flickers of real fire dancing along his knuckles. He doesn't look corrupted. Not yet.

**Hard cut to black.** Chapter 1 begins here.

---

## Design Notes

- No spoken/written dialogue exists anywhere in Chapter 0 except the two cutscene narrations. This is deliberate — she has no language yet, and everything she learns about herself should be shown, not told.
- All three "lessons" (harmless to corruption, no conventional attack, absorption unlock) should be discoverable through play with zero forced tutorial text boxes. If a UI hint system exists elsewhere in the game, Chapter 0 should be the one place it stays almost entirely silent.
- The tonal pivot from grey/dead to orange/warm at the very end is the emotional hook into Chapter 1 — visually promising the player their first relationship before it's torn away.
