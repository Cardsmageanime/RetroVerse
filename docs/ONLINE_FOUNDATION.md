# RetroVerse Online — protocol and security foundation (draft)

Status: **design + offline-testable validation only**. No production account server or matchmaking deployed.

## Account and access model
- Offline gaming requires no registration or network.
- RetroVerse Online requires an account when a future server is available. Never invent compatibility with EmuELEC or RetroArch lobbies.
- Server decides authentication, membership, match permissions, ban/cheat policy and rate limits. Client messages are untrusted.
- Use TLS for server connections; do not place secrets or passwords in URL parameters or repository files.
- Password hashes and MFA must be implemented with reviewed standard authentication components; no home-grown authentication cryptography.
- Default rooms private when creating an invite-only session. Public rooms require explicit opt-in.
- Spectators are read-only; cannot inject game inputs, execute commands, or acquire private invitations.
- Offline-only cheats must be blocked when a local or network multiplayer session is active, including spectators/host migration.

## Message envelope (preliminary)
Versioned JSON messages with an upper-size limit; strict known-type allowlist and validated room identifiers. Clients never control another user's ID, room owner, or privilege flags. Do not accept remote file paths or shell commands.

## Lobby classes
- Public Online Lobby
- Friends Lobby
- Spectator Lobby
- Creator/Host Lobby

## Reliability and privacy
- Heartbeat and reconnection grace with server-side expiration; explicit room state transitions.
- No storage of chat logs by default until retention and moderation policies are defined.
- No collection of device hardware identifiers for gameplay matchmaking.
- Do not promise rollback netcode or cross-emulator interoperability without protocol tests.

## Next implementation gates
1. Define server-authoritative state machine and input envelope parser, with unit tests.
2. Prototype local-only lobby state machine with no network listener.
3. Add authenticated server, TLS, abuse limits, privacy policy and safe session token handling.
4. Test latency, disconnects, replay, permissions, and cheat blocks before enabling online.
