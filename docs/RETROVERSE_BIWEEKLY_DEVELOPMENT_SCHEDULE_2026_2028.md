# RetroVerse — biweekly development and update calendar (Phases 1–5 only)

**Start:** Sunday, November 8, 2026, approximately **9:00 AM America/Chicago**. **Cadence:** every 14 days on Sunday; flexible delivery within about an hour. **End of planned cadence:** October 22, 2028 (52 check-ins). Local clocks switch CST/CDT automatically.

**Roadmap targets are planning estimates, not guarantees of completed features.** A scheduled check-in should inspect the connected GitHub repository, complete a safe scoped development task where tool access and tests permit, document source code for beginners, and send a factual progress report. If external dependency, tool access, platform limit, safety blocker, or hardware gate prevents progress, report that transparently. Physical testing cannot be performed unattended.

**Status report template:** date; active phase/sprint; new commits/changed files with actual links; tests run and results; milestone acceptance gates; blockers and user action only if indispensable; next sprint. Never invent commits, test results, deployments or hardware evidence.

**Phase 6 is strictly out of scope.** No release qualification, public publishing or Phase 6 coding. Hardware safety: do not flash internal Android/eMMC, run legacy EmuELEC `aml_autoscript`, write removable media, or authorize boot with a research-only DTB. Existing EmuELEC reference SD stays untouched.

## Biweekly schedule

| Sprint | Date (America/Chicago, ~9 AM) | Phase | Planned focus |
|---|---|---|---|
| 01 | 2026-11-08 | 1 | Review storage inventory and protect EmuELEC reference card |
| 02 | 2026-11-22 | 1 | SD capacity, errors and false-capacity evidence |
| 03 | 2026-12-06 | 1 | Board GPIO/card-detect reference audit |
| 04 | 2026-12-20 | 1 | SD regulator and voltage evidence audit |
| 05 | 2027-01-03 | 1 | DRAM and reserved-memory map research |
| 06 | 2027-01-17 | 1 | U-Boot command and external-device mapping review |
| 07 | 2027-01-31 | 1 | Kernel/initramfs reproducibility checks |
| 08 | 2027-02-14 | 1 | Offline DTB safety and compatibility test improvements |
| 09 | 2027-02-28 | 1 | USB removable-media preflight tooling |
| 10 | 2027-03-14 | 1 | Read-only bootchain diagnostic reports |
| 11 | 2027-03-28 | 1 | Boot readiness evidence and recovery checklist |
| 12 | 2027-04-11 | 1 | Controlled hardware-test preparation (no boot without approval) |
| 13 | 2027-04-25 | 1 | Phase 1 gate review; retain blocker if real GameBox evidence missing |
| 14 | 2027-05-09 | 2 | Offline-first system module and directory structure |
| 15 | 2027-05-23 | 2 | Local games library manifest schema |
| 16 | 2027-06-06 | 2 | ROMS path scan and read-only metadata tests |
| 17 | 2027-06-20 | 2 | RetroArch launch adapter design and dry-run tests |
| 18 | 2027-07-04 | 2 | Controllers and input mapping data model |
| 19 | 2027-07-18 | 2 | Save file organization and backup strategy |
| 20 | 2027-08-01 | 2 | Offline profiles with no internet dependency |
| 21 | 2027-08-15 | 2 | Local UI shell and navigation prototype |
| 22 | 2027-08-29 | 2 | Artwork and metadata fallback design |
| 23 | 2027-09-12 | 2 | Single-player-only cheat guard implementation |
| 24 | 2027-09-26 | 2 | Offline settings and language/accessibility groundwork |
| 25 | 2027-10-10 | 2 | Integration and regression tests of offline stack |
| 26 | 2027-10-24 | 2 | Phase 2 feature review; hardware claims remain separate |
| 27 | 2027-11-07 | 3 | ARM hardware profile schema and validation |
| 28 | 2027-11-21 | 3 | Board capability registry and compatibility tests |
| 29 | 2027-12-05 | 3 | External-media layout manifest design |
| 30 | 2027-12-19 | 3 | Versioned update metadata and signature checks |
| 31 | 2028-01-02 | 3 | A/B update strategy on simulated directories |
| 32 | 2028-01-16 | 3 | Atomic switch/rollback mock and failure injection |
| 33 | 2028-01-30 | 3 | ROM/save/config preservation tests |
| 34 | 2028-02-13 | 3 | Update integrity and downgrade policy |
| 35 | 2028-02-27 | 3 | Offline update bundle verification design |
| 36 | 2028-03-12 | 3 | Phase 3 test review |
| 37 | 2028-03-26 | 4 | Online/offline boundary and account threat model |
| 38 | 2028-04-09 | 4 | Account/MFA design and mock verification |
| 39 | 2028-04-23 | 4 | Friends/identity and permissions schemas |
| 40 | 2028-05-07 | 4 | Private/public lobby service prototype |
| 41 | 2028-05-21 | 4 | Cross-platform compatibility handshake checks |
| 42 | 2028-06-04 | 4 | Multiplayer anti-cheat enforcement for all rooms |
| 43 | 2028-06-18 | 4 | Networking retry/disconnect simulations |
| 44 | 2028-07-02 | 4 | Spectator access-control prototype |
| 45 | 2028-07-16 | 4 | Phase 4 integration/security review |
| 46 | 2028-07-30 | 5 | Theme schema and original palette starter themes |
| 47 | 2028-08-13 | 5 | Theme preview and fallbacks |
| 48 | 2028-08-27 | 5 | Optional backgrounds/artwork pipeline |
| 49 | 2028-09-10 | 5 | Offline playlist shuffle and continuous playback logic |
| 50 | 2028-09-24 | 5 | Chat/moderation and creator lobby design |
| 51 | 2028-10-08 | 5 | Platform badges and spectator presentation |
| 52 | 2028-10-22 | 5 | Phase 5 integration review; handoff only, Phase 6 reserved |

## Phase gates
- **Phase 1:** physical boot is not "done" until user-supervised target boot evidence, SD reliability, board-specific DTB and recoverable nonpersistent boot chain are verified. Continue other software work if blocked.
- **Phase 2:** usable offline RetroArch-based interface and local saves/controllers must be tested; simulated/dry-run modules don't prove full OS operation.
- **Phase 3:** profile compatibility and simulated safe updates must pass rollback and preservation tests; hardware rollout is separately gated.
- **Phase 4:** account security and netplay compatibility must be proven; mock services are not a deployed online platform. Cheats prohibited in all multiplayer.
- **Phase 5:** themes, music, spectators/chat/creator functionality must pass integration tests; live community moderation is required before any deployment.
- **Phase 6:** not scheduled, not developed, jointly determined later.

## Learning documentation rule
For each substantive code change, add/update a `docs/learning/` lesson explaining file paths, functions, tests, commands, and the difference between passing unit tests and live hardware verification.

## Automation limits
Scheduled automation check-ins can request a coding/review task. The task can only perform actions its run-time environment and connected permissions support. There is no guarantee that all phases will be finished by the target dates; unexpected errors, external approvals, and physical testing may delay a gate.
