#!/usr/bin/env python3
"""RetroVerse Online prototype: LAN-only asyncio JSON-lines lobby server.

NOT gameplay netcode, an Internet service, accounts, authentication, or an
encrypted transport. Defaults to loopback; do not expose to public networks.
"""
import argparse
import asyncio
import json
import secrets

MAX_LINE = 4096
MAX_ROOMS = 32
MAX_MEMBERS = 8

class LobbyServer:
    def __init__(self):
        self.rooms = {}
        self.clients = {}

    async def handle(self, reader, writer):
        token = secrets.token_hex(8)
        self.clients[token] = {"name": None, "room": None, "writer": writer}
        try:
            while True:
                try:
                    raw = await reader.readline()
                except ValueError:
                    break
                if not raw:
                    break
                if len(raw) > MAX_LINE or not raw.endswith(b"\n"):
                    await self.send(writer, {"ok": False, "error": "line_too_long"})
                    break
                try:
                    msg = json.loads(raw.decode("utf-8"))
                    if not isinstance(msg, dict):
                        raise ValueError("invalid object")
                    result = await self.dispatch(token, msg)
                except (UnicodeError, ValueError, TypeError, KeyError) as exc:
                    result = {"ok": False, "error": "invalid_request"}
                await self.send(writer, result)
        finally:
            self.leave(token)
            self.clients.pop(token, None)
            writer.close()
            await writer.wait_closed()

    async def send(self, writer, payload):
        writer.write((json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8"))
        await writer.drain()

    def leave(self, token):
        previous = self.clients[token]["room"]
        if previous and previous in self.rooms:
            members = self.rooms[previous]["members"]
            members.discard(token)
            if not members:
                del self.rooms[previous]
        self.clients[token]["room"] = None

    async def dispatch(self, token, msg):
        action = msg.get("action")
        client = self.clients[token]
        if action == "hello":
            name = msg.get("name")
            if not isinstance(name, str) or not 1 <= len(name) <= 24 or not name.replace("_", "").isalnum():
                return {"ok": False, "error": "invalid_name"}
            client["name"] = name
            return {"ok": True, "name": name, "protocol": 1}
        if action == "list":
            return {"ok": True, "rooms": [{"id": key, "name": value["name"], "players": len(value["members"]), "max_players": MAX_MEMBERS} for key, value in sorted(self.rooms.items())]}
        if client["name"] is None:
            return {"ok": False, "error": "hello_required"}
        if action == "create":
            name = msg.get("name")
            if not isinstance(name, str) or not 1 <= len(name) <= 40 or any(ord(c) < 32 for c in name):
                return {"ok": False, "error": "invalid_room"}
            if len(self.rooms) >= MAX_ROOMS:
                return {"ok": False, "error": "room_limit"}
            self.leave(token)
            room_id = secrets.token_hex(4)
            self.rooms[room_id] = {"name": name, "members": {token}}
            client["room"] = room_id
            return {"ok": True, "room": room_id}
        if action == "join":
            room_id = msg.get("room")
            if not isinstance(room_id, str) or room_id not in self.rooms:
                return {"ok": False, "error": "room_not_found"}
            if len(self.rooms[room_id]["members"]) >= MAX_MEMBERS and token not in self.rooms[room_id]["members"]:
                return {"ok": False, "error": "room_full"}
            if client["room"] != room_id:
                self.leave(token)
                self.rooms[room_id]["members"].add(token)
                client["room"] = room_id
            return {"ok": True, "room": room_id}
        if action == "leave":
            self.leave(token)
            return {"ok": True}
        if action == "chat":
            text = msg.get("text")
            if not client["room"]:
                return {"ok": False, "error": "not_in_room"}
            if not isinstance(text, str) or not 1 <= len(text) <= 240 or any(ord(c) < 32 for c in text):
                return {"ok": False, "error": "invalid_message"}
            room = self.rooms[client["room"]]
            event = {"event": "chat", "room": client["room"], "from": client["name"], "text": text}
            for member in list(room["members"]):
                if member != token and member in self.clients:
                    try:
                        await self.send(self.clients[member]["writer"], event)
                    except (ConnectionError, OSError):
                        pass
            return {"ok": True, "delivered": max(len(room["members"]) - 1, 0)}
        return {"ok": False, "error": "unknown_action"}

async def serve(host, port):
    lobby = LobbyServer()
    server = await asyncio.start_server(lobby.handle, host, port, limit=MAX_LINE + 1)
    async with server:
        await server.serve_forever()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("Public interfaces disabled in prototype; loopback only.")
    if not 1024 <= args.port <= 65535:
        parser.error("Port must be between 1024 and 65535")
    asyncio.run(serve(args.host, args.port))

if __name__ == "__main__":
    main()
