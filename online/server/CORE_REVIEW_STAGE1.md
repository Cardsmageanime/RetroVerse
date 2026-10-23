# Core Systems Review — Stage 1 (lobby identity)

This stage inspected the RetroVerse Online lobby policy, session integration, room membership and invite handling. A security issue was identified: the guest `hello` path accepted a display name matching an existing registered account, allowing misleading impersonation in lobby chat without authentication.

## Correction
A guest `hello` request now rejects registered account names, including case variants, using `name_reserved`. Registered accounts continue to authenticate with the established login flow. The regression suite covers both reserved-name refusal and continued access for unrelated guest names.

## Scope and remaining work
- This change does not guarantee globally unique names for simultaneous guests; further identity labeling is needed for public services.
- Existing invite capabilities and account-directed friend invites warrant additional policy tests and review.
- This stage does not certify the frontend, RetroArch netplay, or USB/ARM boot functionality; those require separate source inspection and actual target hardware testing.
- RetroVerse Online remains loopback-only. No production internet claims are made.

Verify with `python -m unittest discover -s online/server -p 'test_*.py' -v` and the GitHub Actions workflow before considering the new commit validated.
