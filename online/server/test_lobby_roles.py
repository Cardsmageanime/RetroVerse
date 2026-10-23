"""Tests for RetroVerse's own lobby permissions (not RetroArch)."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lobby_policy import new_room,join_room,visible

spec=importlib.util.spec_from_file_location("lobby_server",Path(__file__).with_name("lobby_server.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class Writer:
    def __init__(self):self.messages=[]
    def write(self,b):self.messages.append(b.decode())
    async def drain(self):pass

class LobbyRoleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=mod.LobbyServer()
        for token in ("host","guest","watcher"):
            self.s.clients[token]={"name":token,"room":None,"writer":Writer()}
    async def test_friends_invite_and_private_visibility(self):
        created=await self.s.dispatch("host",{"action":"create","name":"Friends game","kind":"friends"})
        rid=created["room"]
        self.assertEqual((await self.s.dispatch("guest",{"action":"list"}))["rooms"],[])
        denied=await self.s.dispatch("guest",{"action":"join","room":rid})
        self.assertEqual(denied["error"],"access_denied")
        token=(await self.s.dispatch("host",{"action":"invite"}))["invite"]
        self.assertFalse((await self.s.dispatch("guest",{"action":"invite"}))["ok"])
        self.assertTrue((await self.s.dispatch("guest",{"action":"join","room":rid,"invite":token}))["ok"])
        self.assertEqual((await self.s.dispatch("watcher",{"action":"join","room":rid,"invite":token}))["error"],"access_denied")
        self.assertEqual(len((await self.s.dispatch("guest",{"action":"list"}))["rooms"]),1)
    async def test_public_spectator_read_only(self):
        rid=(await self.s.dispatch("host",{"action":"create","name":"Public match"}))["room"]
        self.assertEqual((await self.s.dispatch("watcher",{"action":"join","room":rid,"role":"spectator"}))["role"],"spectator")
        self.assertEqual((await self.s.dispatch("watcher",{"action":"chat","text":"test"}))["error"],"spectator_read_only")
        await self.s.dispatch("host",{"action":"chat","text":"hello"})
        self.assertIn('"event":"chat"',self.s.clients["watcher"]["writer"].messages[0])
        await self.s.dispatch("host",{"action":"leave"})
        self.assertIsNone(self.s.clients["watcher"]["room"])
    async def test_creator_rejects_uninvited_guests_and_spectators(self):
        rid=(await self.s.dispatch("host",{"action":"create","name":"Host","kind":"creator"}))["room"]
        self.assertEqual((await self.s.dispatch("watcher",{"action":"join","room":rid,"role":"spectator"}))["error"],"access_denied")
        self.assertEqual((await self.s.dispatch("guest",{"action":"join","room":rid}))["error"],"access_denied")

if __name__=="__main__":unittest.main()
