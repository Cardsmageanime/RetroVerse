"""One-time account recovery codes for local RetroVerse development.

Recovery codes are salted SHA-256 digests; plaintext values are returned only
once when generated. The feature requires completed TOTP enrollment and an
already authenticated session to create the codes.
"""
import hashlib
import hmac
import secrets

class RecoveryStore:
    def __init__(self, db):
        self.db = db
        db.execute("""CREATE TABLE IF NOT EXISTS recovery_codes (
            user_id INTEGER NOT NULL,
            salt BLOB NOT NULL,
            digest BLOB NOT NULL,
            PRIMARY KEY (user_id, digest),
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        db.commit()

    def create(self, user_id, count=8):
        if count != 8:
            raise ValueError("fixed code quantity")
        raw = [secrets.token_hex(12) for _ in range(count)]
        with self.db:
            self.db.execute("DELETE FROM recovery_codes WHERE user_id=?", (user_id,))
            for value in raw:
                salt = secrets.token_bytes(16)
                digest = hashlib.sha256(salt + value.encode("ascii")).digest()
                self.db.execute("INSERT INTO recovery_codes(user_id,salt,digest) VALUES(?,?,?)",
                                (user_id,salt,digest))
        return raw

    def use(self, user_id, candidate):
        if not isinstance(candidate, str) or len(candidate)!=24 or any(ch not in "0123456789abcdef" for ch in candidate):
            return False
        rows = self.db.execute("SELECT salt,digest FROM recovery_codes WHERE user_id=?",(user_id,)).fetchall()
        for salt,digest in rows:
            computed=hashlib.sha256(salt + candidate.encode("ascii")).digest()
            if hmac.compare_digest(digest,computed):
                with self.db:
                    cursor=self.db.execute("DELETE FROM recovery_codes WHERE user_id=? AND digest=?", (user_id,digest))
                return cursor.rowcount == 1
        return False

    def remaining(self, user_id):
        return self.db.execute("SELECT COUNT(*) FROM recovery_codes WHERE user_id=?",(user_id,)).fetchone()[0]
