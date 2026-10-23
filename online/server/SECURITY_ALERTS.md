# RetroVerse Local Suspicious-Activity Alerts

The loopback-only RetroVerse Online prototype can summarize security history for the authenticated account. Send `{"action":"security_alerts"}` on the signed-in connection. The endpoint never accepts a different account identifier, so users cannot request another account's alerts.

Rules consider the last 15 minutes of that account's allowlisted security audit events:
- Three or more failed password logins, or a login throttle event: repeated login failures (warning)
- Three or more failed PIN, TOTP, or recovery-code challenges, or factor throttling: repeated factor failures (warning)
- Recovery-code rotation: recovery codes changed (notice)
- PIN or authenticator activation: authentication settings changed (notice)

These are informational indicators, **not confirmation of account compromise**. The module doesn't send email, texts, or push notifications, doesn't inspect device/IP metadata, and doesn't automatically suspend accounts. Audit retention and local SQLite storage remain bounded and are not tamper-resistant. Additional security review, recovery management, deployment-safe authentication and production monitoring must precede internet access.
