# RetroVerse Online accounts and friend invitations — development prototype

RetroVerse now has an optional account identity system **owned by RetroVerse, not RetroArch**. Account records, pending friend requests, and accepted friendships can persist in a local SQLite database. Registered users have PBKDF2-HMAC-SHA256 salted password hashes rather than plaintext passwords.

**Security boundary:** This is still a **loopback-only development service**. Its JSON-lines connection is not TLS-protected; it has no rate limiting, MFA, password recovery, user verification, abuse prevention, or session-token reauthentication. Do **not** bind it to a public network. The old `hello` guest mode still exists for local demos and must not be mistaken for authentication.

### Development protocol
Start with a local SQLite database by constructing `LobbyServer("retroverse-dev.sqlite")` in a trusted local test harness. The default constructor uses an in-memory database.

Send one JSON command per line:
```json
{"action":"register","name":"PlayerOne","password":"a-long-local-dev-password"}
{"action":"login","name":"PlayerOne","password":"a-long-local-dev-password"}
{"action":"friend_request","name":"PlayerTwo"}
{"action":"friend_accept","name":"PlayerOne"}
{"action":"friends"}
```
`register` logs that connection in immediately; `login` should be used on a fresh connection. Only the named recipient can accept a pending request. A friend-only invitation is created by the room host after both accounts become friends:
```json
{"action":"create","kind":"friends","name":"Friends Game"}
{"action":"friend_invite","name":"PlayerTwo"}
```
The result includes `room` and `invite` values. The invited logged-in user can join that room with the returned ticket. Friend-specific tickets are one-time and bound to the recipient account. The `invite` action from the earlier guest-mode prototype still creates bearer tickets and is **not** a secure account invitation; it needs replacement before production.

To run automated checks:
```sh
python -m unittest discover -s online/server -p 'test_*.py' -v
```
GitHub Actions automatically runs these tests via **Check Online and ARM UI Foundations**.

### Remaining milestones

A production online network requires authenticated transport (TLS), session management, sensible rate limits, safe password storage parameters and migration strategy, privacy/moderation protections, secure account recovery and MFA, production database deployment, and explicit authorization across *all* legacy room APIs. In particular guest `hello` and bearer `invite` are retained only for isolated local testing.

No games are streamed or synchronized by these services. RetroArch is a separate optional emulator/network gameplay backend. RetroVerse's own public, friends, creator/host and spectator lobby services remain the owning layer.

## Session security milestone

Registered logins now get a per-connection, cryptographically random session with a 30-minute lifetime (measured on a monotonic clock). The session is held in server memory and is never persisted or sent as an API credential. The `session_status` action returns whether the current connection is authenticated. The `logout` action revokes the current session, leaves any room, and clears that connection's identity.

When an authenticated session expires, its client identity and room participation are cleared on the next request; host rooms are closed as needed. Account-specific friends and invitations require a currently valid session. The legacy guest `hello` action cannot rename a currently authenticated session.

Run `python -m unittest discover -s online/server -p 'test_*.py' -v` to validate the session lifecycle. These are development-only sessions bound to the live local connection, **not a secure remotely accessible authentication protocol**. MFA, TLS, account recovery, throttling, public service deployment, and removing legacy guest authorization remain future work.
