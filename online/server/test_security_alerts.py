import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from accounts import Accounts
from security_audit import SecurityAudit
from security_alerts import SecurityAlerts
from lobby_server import LobbyServer

class Writer:
    def write(self, data):pass
    async def drain(self):pass

class Rules(unittest.TestCase):
    def test_thresholds_and_account_isolation(self):
        a=Accounts()
        audit=SecurityAudit(a.db,clock=lambda:1000)
        alerts=SecurityAlerts(a.db,clock=lambda:1000)
        for _ in range(3):audit.record("login_failed",1)
        audit.record("factor_throttled",2)
        self.assertEqual([x["kind"] for x in alerts.recent(1)],["repeated_login_failures"])
        self.assertEqual([x["kind"] for x in alerts.recent(2)],["repeated_factor_failures"])
        self.assertEqual(alerts.recent(3),[])
    def test_alerts_expire(self):
        clock=[1000]
        a=Accounts()
        audit=SecurityAudit(a.db,clock=lambda:clock[0])
        alerts=SecurityAlerts(a.db,clock=lambda:clock[0])
        audit.record("recovery_rotated",1)
        self.assertEqual(alerts.recent(1)[0]["kind"],"recovery_codes_changed")
        clock[0]=2000
        self.assertEqual(alerts.recent(1),[])

class EndToEnd(unittest.IsolatedAsyncioTestCase):
    async def test_only_logged_in_user_can_read_alerts(self):
        s=LobbyServer()
        for k in ("a","b"):s.clients[k]={"name":None,"room":None,"user_id":None,"writer":Writer()}
        self.assertEqual((await s.dispatch("b",{"action":"security_alerts"}))["error"],"login_required")
        await s.dispatch("a",{"action":"register","name":"AuditUser","password":"very-long-passphrase"})
        uid=s.clients["a"]["user_id"]
        s.audit.clock=lambda:1000
        s.alerts.clock=lambda:1000
        for _ in range(3):s.audit.record("login_failed",uid)
        result=await s.dispatch("a",{"action":"security_alerts"})
        self.assertEqual(result["alerts"][0]["kind"],"repeated_login_failures")

if __name__=="__main__":unittest.main()
