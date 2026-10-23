"""Regression checks for account login throttling."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from login_limits import AttemptLimiter
from lobby_server import LobbyServer

class FakeWriter:
    def write(self,payload):pass
    async def drain(self):pass

class LimitsTests(unittest.TestCase):
    def test_lockout_and_expiry(self):
        now=[100.]
        limits=AttemptLimiter(limit=3,window=60,clock=lambda:now[0])
        for _ in range(3):
            self.assertFalse(limits.blocked("Alice"))
            self.assertTrue(limits.failure("Alice"))
        self.assertTrue(limits.blocked("ALICE"))
        now[0]=161.
        self.assertFalse(limits.blocked("alice"))
    def test_success_resets_failures(self):
        limits=AttemptLimiter(limit=2)
        limits.failure("Alice")
        limits.success("alice")
        self.assertFalse(limits.blocked("ALICE"))
    def test_bounded_memory(self):
        limits=AttemptLimiter(limit=2,capacity=2)
        limits.failure("alice")
        limits.failure("bob")
        self.assertTrue(limits.saturated())
        self.assertFalse(limits.failure("carol"))

class IntegratedTests(unittest.IsolatedAsyncioTestCase):
    async def test_failed_login_throttled_then_recovers(self):
        s=LobbyServer()
        for t in ("a","b"):
            s.clients[t]={"name":None,"room":None,"writer":FakeWriter(),"user_id":None}
        async def cmd(t,action,**kwargs):
            return await s.dispatch(t,{"action":action,**kwargs})
        registered=await cmd("a","register",name="Alice",password="long-test-password")
        self.assertTrue(registered["authenticated"])
        await cmd("a","logout")
        now=[100.]
        s.login_limits=AttemptLimiter(limit=2,window=60,clock=lambda:now[0])
        for _ in range(2):
            self.assertEqual((await cmd("b","login",name="Alice",password="wrong"))["error"],"invalid_credentials")
        self.assertEqual((await cmd("b","login",name="Alice",password="long-test-password"))["error"],"login_throttled")
        now[0]=161.
        self.assertTrue((await cmd("b","login",name="Alice",password="long-test-password"))["authenticated"])
if __name__=="__main__":unittest.main()
