"""Unit tests for the RetroVerse Online lobby protocol (no network needed)."""
import asyncio
from pathlib import Path
import importlib.util
import unittest

spec=importlib.util.spec_from_file_location("lobby_server",Path(__file__).with_name("lobby_server.py"))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class Writer:
    def __init__(self):self.messages=[]
    def write(self,p):self.messages.append(p.decode("utf-8"))
    async def drain(self):pass

class LobbyTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s=mod.LobbyServer()
        for t in ("a","b"):
            self.s.clients[t]={"name":None,"room":None,"writer":Writer()}
    async def test_room_lifecycle(self):
        self.assertTrue((await self.s.dispatch("a",{"action":"hello","name":"Player1"}))["ok"])
        self.assertTrue((await self.s.dispatch("b",{"action":"hello","name":"Player2"}))["ok"])
        result=await self.s.dispatch("a",{"action":"create","name":"Game Night"})
        rid=result["room"]
        self.assertEqual(len((await self.s.dispatch("b",{"action":"list"}))["rooms"]),1)
        self.assertTrue((await self.s.dispatch("b",{"action":"join","room":rid}))["ok"])
        self.assertTrue((await self.s.dispatch("a",{"action":"chat","text":"hello"}))["ok"])
        self.assertIn('"event":"chat"',self.s.clients["b"]["writer"].messages[0])
        await self.s.dispatch("a",{"action":"leave"})
        await self.s.dispatch("b",{"action":"leave"})
        self.assertEqual(self.s.rooms,{})
    async def test_reject_bad_data_and_unauthorized(self):
        self.assertEqual((await self.s.dispatch("a",{"action":"create","name":"x"}))["error"],"hello_required")
        self.assertFalse((await self.s.dispatch("a",{"action":"hello","name":"!"}))["ok"])
        await self.s.dispatch("a",{"action":"hello","name":"Player1"})
        self.assertEqual((await self.s.dispatch("a",{"action":"chat","text":"hi"}))["error"],"not_in_room")
        self.assertFalse((await self.s.dispatch("a",{"action":"create","name":"\n"}))["ok"])

if __name__=="__main__":unittest.main()
