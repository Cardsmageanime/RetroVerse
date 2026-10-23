"""Ephemeral, cryptographically random login sessions for the local prototype.

Sessions are tied to a client connection. No tokens are transmitted or stored
in SQLite. This is NOT remote authentication or an Internet-ready auth service.
"""
import secrets
import time

SESSION_SECONDS = 30 * 60

class SessionRegistry:
    def __init__(self, clock=None, ttl=SESSION_SECONDS):
        self.clock = clock or time.monotonic
        self.ttl = ttl
        self.sessions = {}

    def create(self, connection, user_id):
        self.revoke(connection)
        key = secrets.token_urlsafe(32)
        self.sessions[connection] = (key, user_id, self.clock() + self.ttl)
        return key

    def user(self, connection):
        entry = self.sessions.get(connection)
        if entry is None:
            return None
        key, uid, expiry = entry
        if self.clock() >= expiry:
            self.revoke(connection)
            return None
        return uid

    def revoke(self, connection):
        self.sessions.pop(connection, None)
