"""Local detection rules over allowlisted account audit events.

Alerts are derived from existing audit entries, never raw credentials. They
are informational only, not proof of compromise or an external notification.
"""
class SecurityAlerts:
    def __init__(self, db, clock=None):
        import time
        self.db=db
        self.clock=clock or time.time
        db.execute("""CREATE TABLE IF NOT EXISTS alert_ack (
            user_id INTEGER NOT NULL, kind TEXT NOT NULL,
            acknowledged_at INTEGER NOT NULL, audit_seq INTEGER NOT NULL,
            PRIMARY KEY(user_id,kind))""")
        db.commit()

    def recent(self, user_id, window=900):
        if type(user_id) is not int or user_id<=0:
            raise ValueError("invalid account")
        cutoff=int(self.clock())-window
        rows=self.db.execute(
            "SELECT event, at_utc, seq FROM security_audit WHERE user_id=? AND at_utc>=? ORDER BY seq DESC",
            (user_id,cutoff)).fetchall()
        kinds=[event for event,_,_ in rows]
        alerts=[]
        if kinds.count("login_failed")>=3 or "login_throttled" in kinds:
            alerts.append({"kind":"repeated_login_failures","severity":"warning"})
        if kinds.count("factor_failed")>=3 or "factor_throttled" in kinds:
            alerts.append({"kind":"repeated_factor_failures","severity":"warning"})
        if "recovery_rotated" in kinds:
            alerts.append({"kind":"recovery_codes_changed","severity":"notice"})
        if "totp_enabled" in kinds or "pin_enabled" in kinds:
            alerts.append({"kind":"authentication_settings_changed","severity":"notice"})
        groups={
            "repeated_login_failures":("login_failed","login_throttled"),
            "repeated_factor_failures":("factor_failed","factor_throttled"),
            "recovery_codes_changed":("recovery_rotated",),
            "authentication_settings_changed":("pin_enabled","totp_enabled")}
        for alert in alerts:
            last=max((seq for event,_,seq in rows if event in groups[alert["kind"]]),default=0)
            ack=self.db.execute("SELECT audit_seq FROM alert_ack WHERE user_id=? AND kind=?",(user_id,alert["kind"])).fetchone()
            alert["acknowledged"]=ack is not None and ack[0]>=last
        return alerts

    def acknowledge(self,user_id,kind):
        current={item["kind"] for item in self.recent(user_id)}
        if not isinstance(kind,str) or kind not in current:return False
        groups={
            "repeated_login_failures":("login_failed","login_throttled"),
            "repeated_factor_failures":("factor_failed","factor_throttled"),
            "recovery_codes_changed":("recovery_rotated",),
            "authentication_settings_changed":("pin_enabled","totp_enabled")}
        events=groups[kind]
        placeholders=",".join("?" for _ in events)
        cutoff=int(self.clock())-900
        result=self.db.execute("SELECT MAX(seq) FROM security_audit WHERE user_id=? AND at_utc>=? AND event IN ("+placeholders+")",(user_id,cutoff,*events)).fetchone()
        if result[0] is None:return False
        with self.db:
            self.db.execute("INSERT INTO alert_ack(user_id,kind,acknowledged_at,audit_seq) VALUES(?,?,?,?) ON CONFLICT(user_id,kind) DO UPDATE SET acknowledged_at=excluded.acknowledged_at,audit_seq=excluded.audit_seq",(user_id,kind,int(self.clock()),result[0]))
        return True
