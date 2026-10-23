import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer
from security_audit import SecurityAudit
from accounts import Accounts

class Writer:
    def write(self,data):pass
    async def drain(self):pass

class AuditTests(unittest.TestCase):
    def test_allowed_events_only_and_retention(self):
        a=Accounts()
        audit=SecurityAudit(a.db,clock=lambda:1000,retention=2)
        for event in ("login_failed","login_success","logout"):
            audit.record(event,1)
        self.assertEqual([r["event"] for r in audit.recent(1)],["logout","login_success"])
        with self.assertRaises(ValueError):audit.record("password=secret",1)
    def test_history_is_account_scoped(self):
        a=Accounts()
        audit=SecurityAudit(a.db)
        audit.record("login_failed",1)
        audit.record("login_success",2)
        self.assertEqual(len(audit.recent(1)),1)
        self.assertEqual(audit.recent(1)[0]["event"],"login_failed")

class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_login_and_private_history(self):
        s=LobbyServer()
        for key in ("a","b"):
            s.clients[key]={"name":None,"room":None,"writer":Writer(),"user_id":None}
        async def send(key,action,**args):
            return await s.dispatch(key,{"action":action,**args})
        self.assertEqual((await send("b","security_history"))["error"],"login_required")
        await send("a","register",name="AuditPlayer",password="long-demo-password")
        await send("a","logout")
        await send("b","login",name="AuditPlayer",password="wrong")
        await send("b","login",name="AuditPlayer",password="long-demo-password")
        events=(await send("b","security_history"))["events"]
        names=[e["event"] for e in events]
        self.assertIn("login_failed",names)
        self.assertIn("login_success",names)
        self.assertFalse(any("password" in repr(e) for e in events))
if __name__=="__main__":unittest.main()
