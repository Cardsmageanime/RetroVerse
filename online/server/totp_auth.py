"""RFC 6238 compatible TOTP verification for local RetroVerse development.

Secrets are stored in SQLite for this prototype. Production requires
encrypted secret storage, recovery, reauthentication and anti-abuse controls.
"""
import base64
import hashlib
import hmac
import secrets
import struct
import time

def make_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")

def code(secret, timestep):
    key=base64.b32decode(secret+"="*((-len(secret))%8),casefold=True)
    digest=hmac.new(key,struct.pack(">Q",timestep),hashlib.sha1).digest()
    offset=digest[-1]&15
    return str((struct.unpack(">I",digest[offset:offset+4])[0]&0x7fffffff)%1000000).zfill(6)

class TotpStore:
    def __init__(self,db,clock=None):
        self.db=db
        self.clock=clock or time.time
        db.execute("CREATE TABLE IF NOT EXISTS totp (user_id INTEGER PRIMARY KEY, secret TEXT NOT NULL, last_step INTEGER NOT NULL DEFAULT -1, FOREIGN KEY(user_id) REFERENCES users(id))")
        db.commit()
    def enabled(self,uid):
        return self.db.execute("SELECT 1 FROM totp WHERE user_id=?",(uid,)).fetchone() is not None
    def setup(self,uid):
        if self.enabled(uid):raise ValueError("already enrolled")
        secret=make_secret()
        with self.db:
            self.db.execute("INSERT INTO totp(user_id,secret) VALUES(?,?)",(uid,secret))
        return secret
    def verify(self,uid,provided):
        if not isinstance(provided,str) or len(provided)!=6 or not provided.isascii() or not provided.isdigit():return False
        row=self.db.execute("SELECT secret,last_step FROM totp WHERE user_id=?",(uid,)).fetchone()
        if row is None:return False
        now=int(self.clock()//30)
        for step in (now-1,now,now+1):
            if step>row[1] and hmac.compare_digest(code(row[0],step),provided):
                with self.db:
                    self.db.execute("UPDATE totp SET last_step=? WHERE user_id=? AND last_step<?",(step,uid,step))
                    if self.db.execute("SELECT changes()").fetchone()[0]==1:return True
        return False
