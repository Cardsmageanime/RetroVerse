"""Local detection rules over allowlisted account audit events.

Alerts are derived from existing audit entries, never raw credentials. They
are informational only, not proof of compromise or an external notification.
"""
class SecurityAlerts:
    def __init__(self, db, clock=None):
        import time
        self.db=db
        self.clock=clock or time.time

    def recent(self, user_id, window=900):
        if type(user_id) is not int or user_id<=0:
            raise ValueError("invalid account")
        cutoff=int(self.clock())-window
        rows=self.db.execute(
            "SELECT event, at_utc FROM security_audit WHERE user_id=? AND at_utc>=? ORDER BY seq DESC",
            (user_id,cutoff)).fetchall()
        kinds=[event for event,_ in rows]
        alerts=[]
        if kinds.count("login_failed")>=3 or "login_throttled" in kinds:
            alerts.append({"kind":"repeated_login_failures","severity":"warning"})
        if kinds.count("factor_failed")>=3 or "factor_throttled" in kinds:
            alerts.append({"kind":"repeated_factor_failures","severity":"warning"})
        if "recovery_rotated" in kinds:
            alerts.append({"kind":"recovery_codes_changed","severity":"notice"})
        if "totp_enabled" in kinds or "pin_enabled" in kinds:
            alerts.append({"kind":"authentication_settings_changed","severity":"notice"})
        return alerts
