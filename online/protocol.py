"""Small, offline-only validator for RetroVerse lobby message envelopes.

This is NOT a deployed server, authentication system or online matchmaking.
"""
import json
import re

MAX_BYTES = 4096
VALID_TYPES = frozenset({"heartbeat", "join_room", "leave_room", "chat", "spectate"})
ROOM_ID = re.compile(r"^[a-zA-Z0-9_-]{3,48}$")
CHAT_MAX_CHARS = 500

class InvalidMessage(ValueError):
    pass

def parse_message(raw: bytes) -> dict:
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise InvalidMessage("Invalid message size or type")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise InvalidMessage("Invalid JSON") from exc
    if not isinstance(data, dict) or set(data) - {"v", "type", "room", "text"}:
        raise InvalidMessage("Unexpected envelope fields")
    if type(data.get("v")) is not int or data["v"] != 1:
        raise InvalidMessage("Unsupported protocol version")
    typ = data.get("type")
    if not isinstance(typ, str) or typ not in VALID_TYPES:
        raise InvalidMessage("Unknown message type")
    if typ in {"join_room", "leave_room", "chat", "spectate"}:
        room = data.get("room")
        if not isinstance(room, str) or not ROOM_ID.fullmatch(room):
            raise InvalidMessage("Invalid room identifier")
    elif "room" in data:
        raise InvalidMessage("Unexpected room identifier")
    if typ == "chat":
        text = data.get("text")
        if not isinstance(text, str) or not 1 <= len(text) <= CHAT_MAX_CHARS or any(ord(c) < 32 and c not in "\t\n" for c in text):
            raise InvalidMessage("Invalid chat text")
    elif "text" in data:
        raise InvalidMessage("Unexpected text")
    return data
