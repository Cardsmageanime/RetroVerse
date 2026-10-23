"""Local-only PIN second step for RetroVerse prototype accounts.

A PIN is knowledge-based and therefore NOT phishing-resistant or an
independent possession factor. This is an optional extra login check, not a
production-grade MFA substitute. No SMS or PIN delivery is implemented.
"""
import hashlib
import hmac
import secrets
import sqlite3

PIN_ROUNDS=250_000

def valid_pin(pin):
    return isinstance(pin,str) and pin.isascii() and pin.isdigit() and 6 <= len(pin) <= 10

class PinStore:
    def __init__(self, database):
        self.db=database
        self.db.execute("CREATE TABLE IF NOT EXISTS account_pin (user_id INTEGER PRIMARY KEY, salt BLOB NOT NULL, digest BLOB NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")
        self.db.commit()

    def enabled(self,user):
        return self.db.execute("SELECT 1 FROM account_pin WHERE user_id=?",(user,)).fetchone() is not None

    def setup(self,user,pin):
        if not valid_pin(pin):
            raise ValueError("PIN must be 6-10 ASCII digits")
        if self.enabled(user):
            raise ValueError("PIN already enabled")
        salt=secrets.token_bytes(16)
        digest=hashlib.pbkdf2_hmac("sha256",pin.encode(),salt,PIN_ROUNDS)
        with self.db:
            self.db.execute("INSERT INTO account_pin(user_id,salt,digest) VALUES(?,?,?)",(user,salt,digest))

    def verify(self,user,pin):
        row=self.db.execute("SELECT salt,digest FROM account_pin WHERE user_id=?",(user,)).fetchone()
        if row is None or not valid_pin(pin):
            return False
        candidate=hashlib.pbkdf2_hmac("sha256",pin.encode(),row[0],PIN_ROUNDS)
        return hmac.compare_digest(candidate,row[1])
