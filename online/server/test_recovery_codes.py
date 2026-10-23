"""Recovery-code integration checks for RetroVerse's local account prototype."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer
from totp_auth import code

class Writer:
    def write(self, value): pass
    async def drain(self): pass

class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for key in ("a","b"):
            self.s.clients[key]={"name":None,"room":None,"writer":Writer(),"user_id":None}
        self.t=[1800000000]
        self.s.totp.clock=lambda:self.t[0]

    async def send(self,key,action,**kwargs):
        return await self.s.dispatch(key,{"action":action,**kwargs})

    async def enroll(self):
        await self.send("a","register",name="RecoveryUser",password="example-password-long")
        secret=(await self.send("a","totp_setup"))["secret"]
        response=await self.send("a","totp_confirm",code=code(secret,self.t[0]//30))
        self.assertTrue(response["totp_enabled"])

    async def test_recovery_single_use_and_password_gate(self):
        await self.enroll()
        denied=await self.send("a","recovery_create",password="bad-password")
        self.assertEqual(denied["error"],"reauth_required")
        codes=(await self.send("a","recovery_create",password="example-password-long"))["codes"]
        self.assertEqual(len(codes),8)
        self.assertEqual(len(set(codes)),8)
        await self.send("a","logout")
        first=await self.send("b","login",name="RecoveryUser",password="example-password-long")
        self.assertTrue(first["totp_required"])
        self.assertEqual((await self.send("b","friends"))["error"],"login_required")
        ok=await self.send("b","recovery_verify",code=codes[0])
        self.assertTrue(ok["authenticated"])
        await self.send("b","logout")
        await self.send("b","login",name="RecoveryUser",password="example-password-long")
        self.assertEqual((await self.send("b","recovery_verify",code=codes[0]))["error"],"recovery_invalid")
        self.assertTrue((await self.send("b","recovery_verify",code=codes[1]))["authenticated"])

    async def test_unenrolled_recovery_not_available(self):
        await self.send("a","register",name="RecoveryUser",password="example-password-long")
        self.assertEqual((await self.send("a","recovery_create",password="example-password-long"))["error"],"totp_required")

if __name__=="__main__":
    unittest.main()
