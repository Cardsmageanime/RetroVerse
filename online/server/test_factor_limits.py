"""Shared factor retry limits must survive fresh client connections."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer
from login_limits import AttemptLimiter

class Writer:
    def write(self, data): pass
    async def drain(self): pass

class FactorLimitTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        self.now=[10.]
        self.s.factor_limits=AttemptLimiter(limit=2,window=60,clock=lambda:self.now[0])
        for key in ("a","b","c"):
            self.s.clients[key]={"name":None,"room":None,"writer":Writer(),"user_id":None}
    async def cmd(self,key,action,**kwargs):
        return await self.s.dispatch(key,{"action":action,**kwargs})
    async def test_pin_failures_across_connections(self):
        await self.cmd("a","register",name="PlayerOne",password="strong-test-password")
        await self.cmd("a","pin_setup",pin="123456")
        await self.cmd("a","logout")
        await self.cmd("b","login",name="PlayerOne",password="strong-test-password")
        self.assertEqual((await self.cmd("b","pin_verify",pin="000000"))["error"],"pin_invalid")
        await self.cmd("c","login",name="PlayerOne",password="strong-test-password")
        self.assertEqual((await self.cmd("c","pin_verify",pin="000000"))["error"],"pin_invalid")
        self.assertEqual((await self.cmd("b","pin_verify",pin="123456"))["error"],"factor_throttled")
        self.assertEqual((await self.cmd("c","pin_verify",pin="123456"))["error"],"factor_throttled")
        self.now[0]=71.
        self.assertTrue((await self.cmd("c","pin_verify",pin="123456"))["authenticated"])
    async def test_other_account_not_blocked(self):
        await self.cmd("a","register",name="PlayerOne",password="strong-test-password")
        await self.cmd("a","pin_setup",pin="123456")
        await self.cmd("a","logout")
        await self.cmd("b","login",name="PlayerOne",password="strong-test-password")
        for _ in range(2):
            await self.cmd("b","pin_verify",pin="000000")
        self.assertTrue((await self.cmd("c","register",name="PlayerTwo",password="different-test-password"))["authenticated"])
if __name__=="__main__":
    unittest.main()
