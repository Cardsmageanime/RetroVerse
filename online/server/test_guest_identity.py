"""Guest identities must not impersonate registered account names."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class W:
    def write(self,data): pass
    async def drain(self): pass

class GuestIdentityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for token in ("member","guest"):
            self.s.clients[token]={"name":None,"room":None,"writer":W(),"user_id":None}
    async def test_registered_name_is_reserved_case_insensitively(self):
        created=await self.s.dispatch("member",{"action":"register","name":"RetroPlayer","password":"example-strong-password"})
        self.assertTrue(created["authenticated"])
        result=await self.s.dispatch("guest",{"action":"hello","name":"retroplayer"})
        self.assertEqual(result["error"],"name_reserved")
        self.assertIsNone(self.s.clients["guest"]["name"])
        result=await self.s.dispatch("guest",{"action":"hello","name":"UnregisteredGuest"})
        self.assertTrue(result["ok"])
    async def test_guest_name_is_not_account_identity(self):
        result=await self.s.dispatch("guest",{"action":"hello","name":"Visitor"})
        self.assertTrue(result["ok"])
        self.assertIsNone(self.s.sessions.user("guest"))
        self.assertEqual((await self.s.dispatch("guest",{"action":"friends"}))["error"],"login_required")
if __name__=="__main__": unittest.main()
