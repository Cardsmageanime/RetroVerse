"""Friend-code enrollment and friends-room boundaries."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class W:
    def write(self,x):pass
    async def drain(self):pass

class FriendCodeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for k in ("alice","bob","guest"):
            self.s.clients[k]={"name":None,"room":None,"user_id":None,"writer":W()}
    async def call(self,k,action,**kw):
        return await self.s.dispatch(k,{"action":action,**kw})
    async def test_code_acceptance_and_room_isolation(self):
        await self.call("alice","register",name="Alice",password="example-alice-password")
        await self.call("bob","register",name="Bob",password="example-bob-password")
        code=(await self.call("bob","friend_code"))["code"]
        self.assertEqual(len(code),16)
        self.assertEqual((await self.call("alice","friend_request",name="Bob"))["error"],"invalid_friend")
        self.assertTrue((await self.call("alice","friend_request",code=code))["ok"])
        self.assertEqual((await self.call("bob","friend_requests"))["requests"],["Alice"])
        self.assertTrue((await self.call("bob","friend_accept",name="Alice"))["ok"])
        room=(await self.call("alice","create",name="Friends",kind="friends"))["room"]
        self.assertEqual((await self.call("alice","invite"))["error"],"friend_invite_required")
        self.assertEqual((await self.call("guest","hello",name="Visitor"))["ok"],True)
        self.assertEqual((await self.call("guest","join",room=room))["error"],"access_denied")
        self.assertEqual((await self.call("bob","join",room=room))["error"],"access_denied")
        invite=(await self.call("alice","friend_invite",name="Bob"))["invite"]
        self.assertEqual((await self.call("guest","join",room=room,invite=invite))["error"],"access_denied")
        self.assertEqual((await self.call("bob","join",room=room,invite=invite))["role"],"player")
        self.assertTrue((await self.call("bob","chat",text="Hi friend"))["ok"])
    async def test_guest_cannot_create_friends_room(self):
        await self.call("guest","hello",name="Visitor")
        result=await self.call("guest","create",name="No friends",kind="friends")
        self.assertEqual(result["error"],"login_required")
if __name__=="__main__":unittest.main()
