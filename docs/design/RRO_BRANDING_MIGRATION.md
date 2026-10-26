# RRO — Retro Relay Online branding migration

**Working name approved by owner:** Retro Relay Online (**RRO**).
**Former working name:** RetroVerse Systems Edition.
**Status:** branding transition; name clearance and technical migration remain pending.
**Scope:** ARM removable-media operating system and its optional network services, Phases 1–5 only. Phase 6 remains strictly reserved.

## Project separation
- **RRO Systems Edition:** bootable ARM OS for supported TV boxes, sticks and consoles; functions fully offline for library, local saves, controllers, solo games and single-player cheats.
- **RetroRelay PC:** separate existing Windows/Linux desktop application. This is not the RRO ARM image or repository.
- **RRO Online services:** optional account, friends, lobbies, spectators, chat and compatible netplay; internet is needed only for those functions. Cheats are blocked in *all* multiplayer.

## Migration rules
1. Use `Retro Relay Online (RRO)` in new user-facing names, docs, mockups and original artwork; do not copy the unrelated ArtStation artwork.
2. Keep historical Git commit messages, old milestone documentation, existing boot paths, script names and source identifiers functional until there is a tested migration. Do not globally replace strings in kernel, boot scripts, paths or hardware profiles.
3. Keep the GitHub repository `Cardsmageanime/RetroVerse` unchanged for now, preserving scheduled automation links. GitHub repository rename and automation updates are a separate coordinated step.
4. Prior to public release, search current trademark databases for `Retro Relay Online`, `RetroRelay` and `RRO` plus similar names and assess software/service class collisions; no clearance or exclusivity is implied by preliminary web searches.
5. New naming does not relax the external-only boot or 1 TB SD-card policy and never permits writes to Android/eMMC.
6. Create new original logo/icons/art only under the new brand after design approval; quarantine unknown-provenance assets.

## Acceptance criteria
- Consistent project identity in UI, product overview and end-user documentation.
- Backward compatibility or explicit migration paths for existing RetroVerse-labelled configuration files and profiles.
- Tests show that boot tooling, GPIO/SD safety validations and documentation links are unaffected.
- Live accounts, DNS, GitHub repository slug, packages and firmware artifacts only renamed after the owner approves their impact.
