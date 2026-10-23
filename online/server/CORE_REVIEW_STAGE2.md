# Core Systems Review — Stage 2: Invite Permissions

Scope: RetroVerse Online local multiplayer lobby permissions and private-room invite lifecycle.

## Changes
- Add the `invite_revoke` action for the current room host.
- Reject revocation attempts by guests and other room members.
- Invalid or previously consumed tokens are rejected.
- Revocation removes both the bearer invite token and its optional account-target mapping.
- Existing one-use invite consumption is preserved.
- Added regression tests for host authorization, revoked token refusal, unaffected tickets, and one-time use.

## Follow-up review
The generic `invite` feature still creates transferable bearer invites even in friends rooms. Those invites are deliberately not account-bound. By contrast, `friend_invite` targets a registered friend account. Before any public deployment, decide whether friends rooms must require authenticated friendship for *all* join paths or continue supporting host-issued guest invites. The current protocol is loopback-only, and this feature does not make it internet-ready.

Verification: GitHub Actions workflow `check-online-arm-foundation.yml` must pass for the latest commit. This stage has not validated ARM, RetroArch, or SD-card boot.
