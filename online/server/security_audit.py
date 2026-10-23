"""Minimal local security audit trail: allowlisted event types only.

Never stores passwords, PINs, TOTP secrets, recovery codes, session tokens,
IP addresses or raw request contents. This is not production audit logging.
"""
import time

EVENTS=frozenset({
    "login_failed", "login_throttled", "login_success",
    "register_success", "logout", "pin_enabled", "totp_enabled",
    "factor_failed", "factor_throttled", "factor_success",
    "recovery_rotated"
})

class SecurityAudit:
    def __init__(self, db, clock=None, retention=500):
        self.db=db
        self.clock=clock or time.time
        self.retention=retention
        db.execute("""CREATE TABLE IF NOT EXISTS security_audit (
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          at_utc INTEGER NOT NULL,
          event TEXT NOT NULL,
          user_id INTEGER
        )""")
        db.commit()

    def record(self, event, user_id=None):
        if event not in EVENTS:
            raise ValueError("unapproved audit event")
        if user_id is not None and (type(user_id) is not int or user_id <= 0):
            raise ValueError("invalid audit account id")
        with self.db:
            self.db.execute("INSERT INTO security_audit(at_utc,event,user_id) VALUES(?,?,?)",
                            (int(self.clock()),event,user_id))
            self.db.execute("DELETE FROM security_audit WHERE seq NOT IN (SELECT seq FROM security_audit ORDER BY seq DESC LIMIT ?)",(self.retention,))

    def recent(self,user_id,limit=30):
        if type(user_id) is not int or user_id<=0 or type(limit) is not int or not 1<=limit<=100:
            raise ValueError("invalid query")
        return [{"at_utc":row[0],"event":row[1]} for row in self.db.execute(
            "SELECT at_utc,event FROM security_audit WHERE user_id=? ORDER BY seq DESC LIMIT ?",(user_id,limit))]
