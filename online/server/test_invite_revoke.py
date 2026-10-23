import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_server import LobbyServer

class Writer:
    def write(self,data):pass
    async def drain(self):pass

class PrivateInvites(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=LobbyServer()
        for t in ("host","guest","outsider"):
            self.s.clients[t]={"name":t,"room":None,"writer":Writer(),"user_id":None}
    async def send(self,t,action,**kw):
        return await self.s.dispatch(t,{"action":action,**kw})
    async def test_host_can_revoke_unused_invite(self):
        room=(await self.send("host","create",name="Private",kind="friends"))["room"]
        ticket=(await self.send("host","invite"))["invite"]
        self.assertEqual((await self.send("guest","invite_revoke",invite=ticket))["error"],"host_only")
        self.assertTrue((await self.send("host","invite_revoke",invite=ticket))["ok"])
        self.assertEqual((await self.send("guest","join",room=room,invite=ticket))["error"],"access_denied")
    async def test_revoke_unknown_and_preserve_other_ticket(self):
        room=(await self.send("host","create",name="Private",kind="friends"))["room"]
        first=(await self.send("host","invite"))["invite"]
        second=(await self.send("host","invite"))["invite"]
        self.assertEqual((await self.send("host","invite_revoke",invite="absent"))["error"],"invite_not_found")
        await self.send("host","invite_revoke",invite=first)
        self.assertTrue((await self.send("guest","join",room=room,invite=second))["ok"])
        self.assertEqual((await self.send("outsider","join",room=room,invite=second))["error"],"access_denied")
if __name__=="__main__":unittest.main()
