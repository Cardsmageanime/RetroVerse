import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from accounts import Accounts
from security_audit import SecurityAudit
from security_alerts import SecurityAlerts
from lobby_server import LobbyServer

class W:
    def write(self,p):pass
    async def drain(self):pass

class Acknowledgements(unittest.TestCase):
    def test_acknowledge_and_reopen(self):
        a=Accounts()
        t=[1000]
        audit=SecurityAudit(a.db,clock=lambda:t[0])
        alerts=SecurityAlerts(a.db,clock=lambda:t[0])
        audit.record("recovery_rotated",1)
        self.assertFalse(alerts.recent(1)[0]["acknowledged"])
        self.assertTrue(alerts.acknowledge(1,"recovery_codes_changed"))
        self.assertTrue(alerts.recent(1)[0]["acknowledged"])
        audit.record("recovery_rotated",1)
        self.assertFalse(alerts.recent(1)[0]["acknowledged"])
        self.assertFalse(alerts.acknowledge(1,"unknown_kind"))
        self.assertFalse(alerts.acknowledge(2,"recovery_codes_changed"))

class Access(unittest.IsolatedAsyncioTestCase):
    async def test_authenticated_account_only(self):
        s=LobbyServer()
        for k in ("a","b"):
            s.clients[k]={"name":None,"room":None,"writer":W(),"user_id":None}
        s.audit.clock=lambda:1000
        s.alerts.clock=lambda:1000
        self.assertEqual((await s.dispatch("b",{"action":"security_alert_ack","kind":"recovery_codes_changed"}))["error"],"login_required")
        await s.dispatch("a",{"action":"register","name":"Alice","password":"long-example-password"})
        uid=s.clients["a"]["user_id"]
        s.audit.record("recovery_rotated",uid)
        self.assertTrue((await s.dispatch("a",{"action":"security_alert_ack","kind":"recovery_codes_changed"}))["acknowledged"])
        response=await s.dispatch("a",{"action":"security_alerts"})
        self.assertTrue(response["alerts"][0]["acknowledged"])
        self.assertEqual((await s.dispatch("b",{"action":"security_alert_ack","kind":"recovery_codes_changed"}))["error"],"login_required")
if __name__=="__main__":unittest.main()
