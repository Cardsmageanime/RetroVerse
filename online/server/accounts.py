"""Local-only RetroVerse identity prototype with SQLite persistence.

Do not expose on the Internet. Passwords are PBKDF2-HMAC-SHA256 salted hashes,
not plaintext. Transport authentication, MFA, throttling and recovery are future work.
"""
import hashlib
import hmac
import re
import secrets
import sqlite3

NAME = re.compile(r"^[A-Za-z0-9_]{3,24}$")
ITERATIONS = 250_000

class Accounts:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE, salt BLOB NOT NULL, password_hash BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS friend_codes(user_id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));
          CREATE TABLE IF NOT EXISTS friends(user_id INTEGER NOT NULL, friend_id INTEGER NOT NULL, PRIMARY KEY(user_id,friend_id), FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(friend_id) REFERENCES users(id));
          CREATE TABLE IF NOT EXISTS public_friends(user_id INTEGER NOT NULL, friend_id INTEGER NOT NULL, PRIMARY KEY(user_id,friend_id));
          CREATE TABLE IF NOT EXISTS public_requests(sender INTEGER NOT NULL, recipient INTEGER NOT NULL, PRIMARY KEY(sender,recipient));
          CREATE TABLE IF NOT EXISTS requests(sender INTEGER NOT NULL, recipient INTEGER NOT NULL, PRIMARY KEY(sender,recipient), FOREIGN KEY(sender) REFERENCES users(id), FOREIGN KEY(recipient) REFERENCES users(id));
        """)
        self.db.commit()

    def register(self,name,password):
        if not isinstance(name,str) or not NAME.fullmatch(name):
            raise ValueError("username must be 3-24 letters, numbers or underscores")
        if not isinstance(password,str) or not 12 <= len(password) <= 256:
            raise ValueError("password must be 12-256 characters")
        salt=secrets.token_bytes(16)
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,ITERATIONS)
        try:
            with self.db:
                self.db.execute("INSERT INTO users(name,salt,password_hash) VALUES(?,?,?)",(name,salt,digest))
        except sqlite3.IntegrityError as exc:
            raise ValueError("username unavailable") from exc
        uid=self.find(name)
        with self.db:
            self.db.execute("INSERT INTO friend_codes(user_id,code) VALUES(?,?)",(uid,secrets.token_hex(8).upper()))
        return uid

    def friend_code(self,uid):
        row=self.db.execute("SELECT code FROM friend_codes WHERE user_id=?",(uid,)).fetchone()
        if row:return row[0]
        if self.db.execute("SELECT 1 FROM users WHERE id=?",(uid,)).fetchone() is None:
            raise ValueError("unknown user")
        value=secrets.token_hex(8).upper()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO friend_codes(user_id,code) VALUES(?,?)",(uid,value))
        return self.db.execute("SELECT code FROM friend_codes WHERE user_id=?",(uid,)).fetchone()[0]

    def find_by_friend_code(self, value):
        if not isinstance(value,str) or len(value)!=16:return None
        row=self.db.execute("SELECT user_id FROM friend_codes WHERE code=?",(value.upper(),)).fetchone()
        return row[0] if row else None

    def friend_requests(self,uid):
        return [row[0] for row in self.db.execute("SELECT users.name FROM requests JOIN users ON users.id=requests.sender WHERE requests.recipient=? ORDER BY users.name",(uid,))]

    def find(self,name):
        if not isinstance(name,str):return None
        row=self.db.execute("SELECT id FROM users WHERE name=?",(name,)).fetchone()
        return row[0] if row else None

    def authenticate(self,name,password):
        if not isinstance(password,str):return None
        row=self.db.execute("SELECT id,salt,password_hash FROM users WHERE name=?",(name,)).fetchone() if isinstance(name,str) else None
        if row is None:return None
        candidate=hashlib.pbkdf2_hmac("sha256",password.encode(),row[1],ITERATIONS)
        return row[0] if hmac.compare_digest(candidate,row[2]) else None


    def rotate_friend_code(self,uid):
        if self.db.execute("SELECT 1 FROM users WHERE id=?",(uid,)).fetchone() is None:
            raise ValueError("unknown user")
        code=secrets.token_hex(8).upper()
        with self.db:
            self.db.execute("INSERT INTO friend_codes(user_id,code) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET code=excluded.code",(uid,code))
        return code

    def request_public_friend(self,sender,recipient):
        if sender is None or recipient is None or sender==recipient or self.are_public_friends(sender,recipient):
            raise ValueError("invalid public request")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO public_requests(sender,recipient) VALUES(?,?)",(sender,recipient))

    def accept_public_friend(self,recipient,sender):
        with self.db:
            cur=self.db.execute("DELETE FROM public_requests WHERE sender=? AND recipient=?",(sender,recipient))
            if cur.rowcount!=1: raise ValueError("no public request")
            self.db.executemany("INSERT OR IGNORE INTO public_friends(user_id,friend_id) VALUES(?,?)",[(sender,recipient),(recipient,sender)])

    def public_requests(self,uid):
        return [r[0] for r in self.db.execute("SELECT users.name FROM public_requests JOIN users ON users.id=public_requests.sender WHERE recipient=? ORDER BY users.name",(uid,))]

    def public_friends(self,uid):
        return [r[0] for r in self.db.execute("SELECT users.name FROM public_friends JOIN users ON users.id=public_friends.friend_id WHERE user_id=? ORDER BY users.name",(uid,))]

    def are_public_friends(self,a,b):
        if a is None or b is None:return False
        return self.db.execute("SELECT 1 FROM public_friends WHERE user_id=? AND friend_id=?",(a,b)).fetchone() is not None

    def remove_friend(self,uid,target,private=False):
        table="friends" if private else "public_friends"
        with self.db:
            self.db.execute(f"DELETE FROM {table} WHERE (user_id=? AND friend_id=?) OR (user_id=? AND friend_id=?)",(uid,target,target,uid))

    def request_friend(self,sender,recipient):
        if sender == recipient or sender is None or recipient is None:
            raise ValueError("invalid friend target")
        if self.are_friends(sender,recipient):
            raise ValueError("already friends")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO requests(sender,recipient) VALUES(?,?)",(sender,recipient))

    def accept_friend(self,recipient,sender):
        with self.db:
            cursor=self.db.execute("DELETE FROM requests WHERE sender=? AND recipient=?",(sender,recipient))
            if cursor.rowcount != 1:raise ValueError("no pending request")
            self.db.executemany("INSERT OR IGNORE INTO friends(user_id,friend_id) VALUES(?,?)",[(sender,recipient),(recipient,sender)])

    def are_friends(self,a,b):
        if a is None or b is None:return False
        return self.db.execute("SELECT 1 FROM friends WHERE user_id=? AND friend_id=?",(a,b)).fetchone() is not None

    def friends(self,user):
        return [r[0] for r in self.db.execute("SELECT users.name FROM friends JOIN users ON users.id=friends.friend_id WHERE friends.user_id=? ORDER BY users.name",(user,))]
