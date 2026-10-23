import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer
from totp_auth import code

class W:
    def write(self, data):pass
    async def drain(self):pass

class Tests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for key in ("a","b"):
            self.s.clients[key]={"name":None,"room":None,"writer":W(),"user_id":None}
        self.s.totp.clock=lambda:1800000000
    async def call(self,key,action,**kwargs):
        return await self.s.dispatch(key,{"action":action,**kwargs})
    async def test_totp_blocks_access_until_challenge(self):
        await self.call("a","register",name="ExampleUser",password="long-example-password")
        secret=(await self.call("a","totp_setup"))["secret"]
        await self.call("a","logout")
        result=await self.call("b","login",name="ExampleUser",password="long-example-password")
        self.assertTrue(result["totp_required"])
        self.assertEqual((await self.call("b","friends"))["error"],"login_required")
        self.assertEqual((await self.call("b","totp_verify",code="000000"))["error"],"totp_invalid")
        correct=code(secret,1800000000//30)
        self.assertTrue((await self.call("b","totp_verify",code=correct))["authenticated"])
        self.assertEqual((await self.call("b","totp_verify",code=correct))["error"],"totp_not_pending")
    async def test_totp_then_pin(self):
        await self.call("a","register",name="ExampleUser",password="long-example-password")
        await self.call("a","pin_setup",pin="123456")
        secret=(await self.call("a","totp_setup"))["secret"]
        await self.call("a","logout")
        await self.call("b","login",name="ExampleUser",password="long-example-password")
        result=await self.call("b","totp_verify",code=code(secret,1800000000//30))
        self.assertTrue(result["pin_required"])
        self.assertFalse((await self.call("b","session_status"))["authenticated"])
        self.assertTrue((await self.call("b","pin_verify",pin="123456"))["authenticated"])
if __name__=="__main__":unittest.main()
