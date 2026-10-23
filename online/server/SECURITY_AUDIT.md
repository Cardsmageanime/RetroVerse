# RetroVerse Online: local security audit milestone

The local account server records only these security outcomes: successful registration, attempted login success/failure, login throttling, logout, PIN activation, confirmed authenticator activation, second-factor success/failure/throttling, and recovery-code rotation.

The SQLite audit table stores an event label, account numeric ID when available, and a UTC timestamp. **It does not store passwords, PINs, TOTP secrets, recovery codes, full requests, IP addresses, or session tokens.** The prototype retains at most the most recent 500 records globally.

Authenticated account holders can retrieve their own 30 most recent records with `{"action":"security_history"}`. Guest connections cannot access that history. Tests cover allowlisted fields, retention, account isolation, and login events.

**Not production ready:** SQLite audit events are not tamper-evident, the local server has no TLS or distributed persistence, and this is not a real-time security alert or suspicious-activity detector. Further work should harden storage, notification delivery, authentication, and privacy handling before deployment.
