import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class W:
    def write(self,x): pass
    async def drain(self): pass

class AuditRegression(unittest.IsolatedAsyncioTestCase):
    async def test_incomplete_login_not_success(self):
        s=LobbyServer()
        for key in ("a","b"):
            s.clients[key]={"name":None,"room":None,"user_id":None,"writer":W()}
        async def send(k,a,**kw):return await s.dispatch(k,{"action":a,**kw})
        await send("a","register",name="Tester",password="example-long-password")
        await send("a","pin_setup",pin="123456")
        uid=s.clients["a"]["user_id"]
        await send("a","logout")
        pending=await send("b","login",name="Tester",password="example-long-password")
        self.assertTrue(pending["pin_required"])
        self.assertNotIn("login_success",[e["event"] for e in s.audit.recent(uid)])
        for _ in range(3):await send("b","pin_verify",pin="000000")
        events=[e["event"] for e in s.audit.recent(uid)]
        self.assertEqual(events.count("factor_failed"),3)
if __name__=="__main__":unittest.main()
