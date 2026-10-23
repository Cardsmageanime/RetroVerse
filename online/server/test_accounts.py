"""Local account persistence and authenticated friend invitation tests."""
import tempfile
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from accounts import Accounts
from lobby_server import LobbyServer

class W:
    def write(self,data):pass
    async def drain(self):pass

class AccountTests(unittest.TestCase):
    def test_persistence_and_passwords(self):
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/"accounts.sqlite")
            a=Accounts(path)
            alice=a.register("Alice","very-secure-passphrase")
            bob=a.register("Bob","different-long-passphrase")
            self.assertIsNone(a.authenticate("Alice","bad_password"))
            self.assertEqual(a.authenticate("Alice","very-secure-passphrase"),alice)
            a.request_friend(alice,bob)
            a.accept_friend(bob,alice)
            a.db.close()
            b=Accounts(path)
            self.assertTrue(b.are_friends(alice,bob))
            self.assertEqual(b.friends(alice),["Bob"])
            with self.assertRaises(ValueError):b.register("alice","another-valid-password")
            b.db.close()

class IntegratedTests(unittest.IsolatedAsyncioTestCase):
    async def test_authenticated_friend_invite(self):
        s=LobbyServer()
        for token in ("a","b","c"):
            s.clients[token]={"name":None,"room":None,"writer":W(),"user_id":None}
        async def dispatch(token,action,**kwargs):
            return await s.dispatch(token,{"action":action,**kwargs})
        self.assertEqual((await dispatch("a","friends"))["error"],"login_required")
        await dispatch("a","register",name="Alice",password="alice-long-passphrase")
        await dispatch("b","register",name="Bob",password="bob-long-passphrase")
        await dispatch("c","register",name="Carol",password="carol-long-passphrase")
        self.assertTrue((await dispatch("a","friend_request",name="Bob"))["ok"])
        self.assertTrue((await dispatch("b","friend_accept",name="Alice"))["ok"])
        room=(await dispatch("a","create",name="Friends",kind="friends"))["room"]
        self.assertEqual((await dispatch("a","friend_invite",name="Carol"))["error"],"not_friends")
        ticket=await dispatch("a","friend_invite",name="Bob")
        self.assertTrue(ticket["ok"])
        self.assertEqual((await dispatch("c","join",room=room,invite=ticket["invite"]))["error"],"access_denied")
        self.assertEqual((await dispatch("b","join",room=room,invite=ticket["invite"]))["role"],"player")
        self.assertEqual((await dispatch("c","join",room=room,invite=ticket["invite"]))["error"],"access_denied")
        self.assertEqual((await dispatch("b","friends"))["friends"],["Alice"])

if __name__=="__main__":unittest.main()
