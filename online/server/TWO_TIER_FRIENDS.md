# Two-Tier Friends System (Stage 2)

RetroVerse Online now has two independent, mutually accepted relationship tiers in the SQLite prototype.

## Public friends
- `public_friend_request` with `name` submits a request by username.
- `public_friend_requests` shows pending senders.
- `public_friend_accept` with `name` accepts one.
- `public_friends` returns mutual public connections.
- `public_friend_remove` with `name` removes both public edges.

## Private friends (Inner Circle)
- `friend_code` returns the authenticated user's private invitation code.
- The account owner shares that code privately.
- `friend_request` with `code` submits an Inner Circle request.
- `friend_requests` shows pending senders.
- `friend_accept` with `name` approves a request.
- `friends` returns private Inner Circle connections.
- `friend_remove` with `name` removes both private edges.
- `friend_code_rotate` requires current password and issues a replacement code, invalidating the old code without deleting accepted friendships.

Public friendship does **not** imply private friendship; public connections cannot join friends-only lobbies. Private rooms require authenticated accepted inner-circle friendship and host-issued recipient-specific invite. In this local prototype, `friends` is the existing private tier name for compatibility.

## Remaining limitations
No dedicated direct-message service or profile UI is implemented. Future security work must add request throttling, decline/block controls, code-guessing protections, privacy controls and revocation handling for members currently in a room. Never expose the loopback prototype directly to the internet.

Run `python -m unittest discover -s online/server -p 'test_*.py' -v` and confirm latest GitHub Actions verification before calling the milestone complete.
