"""Distinct mutual social and inner-circle friendships."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class Writer:
    def write(self, data): pass
    async def drain(self): pass

class TwoListsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for token in ("a","b"):
            self.s.clients[token]={"name":None,"room":None,"writer":Writer(),"user_id":None}
        await self.call("a","register",name="Alice",password="alice-strong-password")
        await self.call("b","register",name="Bob",password="bobby-strong-password")
    async def call(self,token,action,**fields):
        return await self.s.dispatch(token,{"action":action,**fields})
    async def test_public_friendship_is_mutual_but_not_private(self):
        self.assertTrue((await self.call("a","public_friend_request",name="Bob"))["ok"])
        self.assertEqual((await self.call("b","public_friend_requests"))["requests"],["Alice"])
        self.assertEqual((await self.call("a","public_friends"))["friends"],[])
        self.assertTrue((await self.call("b","public_friend_accept",name="Alice"))["ok"])
        self.assertEqual((await self.call("a","public_friends"))["friends"],["Bob"])
        self.assertEqual((await self.call("b","public_friends"))["friends"],["Alice"])
        self.assertEqual((await self.call("a","friends"))["friends"],[])
        room=(await self.call("a","create",name="Private",kind="friends"))["room"]
        self.assertEqual((await self.call("a","friend_invite",name="Bob"))["error"],"not_friends")
        self.assertEqual((await self.call("b","join",room=room))["error"],"access_denied")
    async def test_code_rotation_revokes_old_code_without_removing_friends(self):
        old=(await self.call("b","friend_code"))["code"]
        self.assertEqual((await self.call("b","friend_code_rotate",password="wrong"))["error"],"reauth_required")
        self.assertEqual((await self.call("b","friend_code"))["code"],old)
        new=(await self.call("b","friend_code_rotate",password="bobby-strong-password"))["code"]
        self.assertNotEqual(old,new)
        self.assertEqual((await self.call("a","friend_request",code=old))["error"],"invalid_friend")
        self.assertTrue((await self.call("a","friend_request",code=new))["ok"])
        self.assertTrue((await self.call("b","friend_accept",name="Alice"))["ok"])
        self.assertTrue((await self.call("b","friend_code_rotate",password="bobby-strong-password"))["ok"])
        self.assertEqual((await self.call("a","friends"))["friends"],["Bob"])
        self.assertTrue((await self.call("a","friend_remove",name="Bob"))["ok"])
        self.assertEqual((await self.call("a","friends"))["friends"],[])
        self.assertEqual((await self.call("b","friends"))["friends"],[])
    async def test_private_removal_evicts_member_from_live_room(self):
        code=(await self.call("b","friend_code"))["code"]
        await self.call("a","friend_request",code=code)
        await self.call("b","friend_accept",name="Alice")
        rid=(await self.call("a","create",name="Inner Circle",kind="friends"))["room"]
        invitation=(await self.call("a","friend_invite",name="Bob"))["invite"]
        self.assertTrue((await self.call("b","join",room=rid,invite=invitation))["ok"])
        self.assertIn("b",self.s.rooms[rid]["members"])
        self.assertTrue((await self.call("a","friend_remove",name="Bob"))["ok"])
        self.assertNotIn("b",self.s.rooms[rid]["members"])
        self.assertIsNone(self.s.clients["b"]["room"])
        self.assertEqual((await self.call("b","chat",text="No longer invited"))["error"],"not_in_room")

    async def test_friend_removal_revokes_unspent_invite_even_when_guest_removes_host(self):
        code=(await self.call("b","friend_code"))["code"]
        await self.call("a","friend_request",code=code)
        await self.call("b","friend_accept",name="Alice")
        rid=(await self.call("a","create",name="Inner Circle",kind="friends"))["room"]
        invitation=(await self.call("a","friend_invite",name="Bob"))["invite"]
        self.assertIn(invitation,self.s.rooms[rid]["invites"])
        await self.call("b","friend_remove",name="Alice")
        self.assertNotIn(invitation,self.s.rooms[rid]["invites"])
        self.assertEqual((await self.call("b","join",room=rid,invite=invitation))["error"],"access_denied")

    async def test_public_removal_is_mutual_and_separate(self):
        await self.call("a","public_friend_request",name="Bob")
        await self.call("b","public_friend_accept",name="Alice")
        await self.call("a","public_friend_remove",name="Bob")
        self.assertEqual((await self.call("a","public_friends"))["friends"],[])
        self.assertEqual((await self.call("b","public_friends"))["friends"],[])
if __name__=="__main__":unittest.main()
