#!/usr/bin/env python3
"""Loopback-only two-player WebSocket Pong demonstration; pip install websockets."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pong_engine import Match, TICK_RATE

try:
    from websockets.asyncio.server import serve
except ImportError as exc:
    raise SystemExit("Install dependency: python -m pip install 'websockets>=14,<17'") from exc

class Room:
    def __init__(self):
        self.sockets = []
        self.match = Match()
        self.task = None

    async def broadcast(self, message):
        payload = json.dumps(message)
        for socket in list(self.sockets):
            try:
                await socket.send(payload)
            except Exception:
                pass

    async def loop(self):
        try:
            while len(self.sockets) == 2:
                self.match.step()
                await self.broadcast(self.match.state())
                await asyncio.sleep(1 / TICK_RATE)
        except asyncio.CancelledError:
            pass

room = Room()

async def handler(ws):
    # Bound to loopback only. Single shared room; two player slots.
    if len(room.sockets) >= 2:
        await ws.send(json.dumps({"type": "error", "message": "Room full (two players)"}))
        await ws.close()
        return
    player = len(room.sockets)
    room.sockets.append(ws)
    await ws.send(json.dumps({"type": "welcome", "player": player, "rate": TICK_RATE}))
    await room.broadcast({"type": "players", "count": len(room.sockets)})
    if len(room.sockets) == 2:
        room.match = Match()
        room.task = asyncio.create_task(room.loop())
    try:
        async for payload in ws:
            if len(payload) > 256:
                await ws.close(code=1009, reason="Message too long")
                break
            try:
                data = json.loads(payload)
                direction = data["direction"]
                if data.get("type") != "input" or type(direction) is not int:
                    continue
                room.match.input(player, direction)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
    finally:
        if ws in room.sockets:
            room.sockets.remove(ws)
        if room.task is not None:
            room.task.cancel()
            room.task = None
        # Existing player's role remains 0; reset session on any leave.
        for remaining in list(room.sockets):
            await remaining.send(json.dumps({"type": "reset", "reason": "Peer disconnected; reconnect both players"}))
            await remaining.close(code=1000, reason="Match ended")
        room.sockets.clear()
        room.match = Match()

async def main(host, port):
    async with serve(handler, host, port, max_size=256, origins=None):
        print(f"RetroVerse gameplay demo ws://{host}:{port} (loopback only)")
        await asyncio.Future()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "::1"])
    p.add_argument("--port", type=int, default=8767)
    args = p.parse_args()
    asyncio.run(main(args.host, args.port))
