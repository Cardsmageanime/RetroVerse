import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class Writer:
    def write(self,data): pass
    async def drain(self): pass

class PinTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.server=LobbyServer()
        for token in ("a","b"):
            self.server.clients[token]={"name":None,"room":None,"writer":Writer(),"user_id":None}
    async def send(self,token,action,**kwargs):
        return await self.server.dispatch(token,{"action":action,**kwargs})
    async def test_login_requires_pin_when_enabled(self):
        self.assertTrue((await self.send("a","register",name="TestPlayer",password="long-example-password"))["authenticated"])
        self.assertTrue((await self.send("a","pin_setup",pin="123456"))["ok"])
        await self.send("a","logout")
        login=await self.send("b","login",name="TestPlayer",password="long-example-password")
        self.assertTrue(login["pin_required"])
        self.assertFalse(login["authenticated"])
        self.assertEqual((await self.send("b","friends"))["error"],"login_required")
        self.assertEqual((await self.send("b","hello",name="Guest"))["error"],"already_authenticated")
        self.assertEqual((await self.send("b","pin_verify",pin="000000"))["error"],"pin_invalid")
        good=await self.send("b","pin_verify",pin="123456")
        self.assertTrue(good["authenticated"])
        self.assertTrue((await self.send("b","session_status"))["authenticated"])
    async def test_pin_attempt_limit(self):
        await self.send("a","register",name="DemoPlayer",password="another-example-password")
        await self.send("a","pin_setup",pin="987654")
        await self.send("a","logout")
        await self.send("b","login",name="DemoPlayer",password="another-example-password")
        for _ in range(2):
            self.assertEqual((await self.send("b","pin_verify",pin="111111"))["error"],"pin_invalid")
        self.assertEqual((await self.send("b","pin_verify",pin="111111"))["error"],"pin_attempts_exhausted")
        self.assertEqual((await self.send("b","pin_verify",pin="987654"))["error"],"pin_not_pending")
    async def test_pin_setup_validation(self):
        await self.send("a","register",name="PlayerOne",password="another-example-password")
        self.assertEqual((await self.send("a","pin_setup",pin="12"))["error"],"pin_setup_rejected")
        self.assertEqual((await self.send("a","pin_setup",pin="１２３４５６"))["error"],"pin_setup_rejected")

if __name__=="__main__": unittest.main()
