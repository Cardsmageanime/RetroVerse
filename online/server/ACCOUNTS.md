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

## Optional PIN second-step prototype

The local RetroVerse account service now supports an optional PIN second step. After `register` or an authenticated `login`, call `{"action":"pin_setup","pin":"123456"}` once to enable it (sample PIN **not** recommended for actual use). Pins are 6–10 ASCII digits and are stored as independently salted PBKDF2-HMAC-SHA256 hashes in SQLite.

On a subsequent login with a correct password, the service returns `{"ok":true,"authenticated":false,"pin_required":true}` instead of immediately establishing a session. Send `{"action":"pin_verify","pin":"YOUR_PIN"}` from the same local connection to complete login. During the challenge, authenticated friends and invitations remain unavailable. Three incorrect guesses end the pending challenge; begin login again after that. `logout` clears pending state.

**This is not production MFA:** A password and static PIN are both knowledge factors, and there is no independent mobile possession proof. A PIN is vulnerable to guessing and phishing; the local prototype still lacks rate limits across login attempts/connections, HTTPS, recovery, delivery verification, secure MFA enrollment reauthentication, and public deployment hardening. Do not reuse real account passwords or PINs in this prototype. The system does not currently offer PIN removal or recovery; a production rollout must build those pathways before accounts depend on it.

The current code remains loopback-only. Tests cover PIN setup, pending challenges, and failed-attempt limits. No SMS has been integrated.

## Authenticator app (TOTP) prototype

The local RetroVerse account service now implements RFC 6238-style six-digit authenticator codes (30-second steps, ±one time-step clock tolerance) with replay prevention. On an authenticated connection, `{"action":"totp_setup"}` generates a Base32 secret. **Do not enable on valuable accounts:** this early prototype immediately enables the secret and has **no recovery or re-enrollment** if the authenticator is lost. A production enrollment must require proof of possession, recovery codes, and reauthentication.

After password login, `totp_required` signals that a code is needed. Submit `{"action":"totp_verify","code":"123456"}` on the same connection. Three failed attempts cancel the challenge. If a separate PIN was previously enabled, PIN verification is required afterward. Codes are verified locally; no SMS service is integrated.

Secrets are stored in local SQLite without at-rest encryption. This is **not deployable internet MFA**: HTTPS/TLS, encrypted secrets, enrollment confirmation, password-rate limiting, recovery, trusted devices, and operational controls remain necessary. The tests use a synthetic clock and do not prove live phone-app compatibility.

## Confirmed TOTP enrollment milestone

TOTP enrollment is now **two-stage** in the local prototype. A logged-in user calls `totp_setup` to receive a pending secret. This does **not** activate a login requirement. Configure that secret in an authenticator app, then submit `{"action":"totp_confirm","code":"CURRENT_CODE"}` while authenticated. Only a valid six-digit code activates TOTP. Unconfirmed secrets can be replaced by repeating setup; enabled enrollments cannot be replaced by this action.

After confirmation, future sign-ins require a fresh authenticator code. Codes used to confirm enrollment cannot be replayed as a login code in the same time step. **Account recovery and safe factor removal are still not implemented.** Do not enable this for real users. Production must encrypt stored TOTP secrets, require recent reauthentication for enrollment changes, provide single-use recovery codes, add throttling, and audit account security events.

## One-time recovery codes (local prototype)

After confirming TOTP enrollment, the user may request eight recovery codes with `{"action":"recovery_create","password":"CURRENT_PASSWORD"}` from an authenticated connection. The response reveals eight random 24-character lowercase hexadecimal codes **once**. Store them offline; they are not retrievable later. Rotating the set invalidates all previous codes. Only salted hashes are stored in SQLite.

If the authenticator is unavailable, finish the password step of `login`, then use `{"action":"recovery_verify","code":"A_SAVED_CODE"}` on the **same connection** while TOTP verification is pending. Each valid code can be used once. A recovery code bypasses only TOTP; if a PIN is enabled, the PIN is still required. After three incorrect attempts, the pending verification challenge is cancelled.

This feature is still development-only: it lacks external credential throttling, storage encryption, auditing, recovery-key setup confirmation, secure device management and account support processes. The existing loopback-only policy remains mandatory.
