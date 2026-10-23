# RetroVerse Friends — Friend Codes and Private Access

This is the Stage 2 friend-policy prototype for the loopback-only RetroVerse Online server.

Each registered account receives a random 16-character hexadecimal friend code, retrieved after authentication through `{"action":"friend_code"}`. The owner shares this code privately. To request friendship, another authenticated user sends `{"action":"friend_request","code":"SHARED_CODE"}`; entering a username alone is insufficient. The recipient can read requests using `friend_requests` and approve a named pending sender via `friend_accept`. A code is an identifier for friend requests, **not a login credential** and **not evidence of mutual friendship**.

Friends-only rooms now require a signed-in owner, accepted friendship with that owner, and an invite issued to the recipient account using `friend_invite`. Generic transferable `invite` tokens are rejected for friends rooms. Guest access and attempted third-party reuse are denied. Chat within friends rooms also checks account friendship with the owner. Public and creator rooms retain their existing guest/bearer-invite behavior.

This changes previous prototype semantics. Friend codes should eventually support regeneration and abuse-prevention controls; pending requests need cancellation/decline/block options, rate limiting, privacy settings, and a UI. Room memberships should be rechecked on friend removal in the future. The prototype is local-only and not internet-ready.

Automated tests: `python -m unittest discover -s online/server -p 'test_*.py' -v`. Check the GitHub Actions run for the latest commit before declaring verification passed.
