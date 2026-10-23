"""Pure RetroVerse-owned lobby policy; deliberately not RetroArch netplay.

Loopback prototype only. Friends grants come from ephemeral per-room invite tokens,
NOT authenticated accounts or a persistent friends graph.
"""
import secrets

KINDS = ("public", "friends", "creator")
ROLES = ("player", "spectator")

def new_room(name, owner, kind="public"):
    if kind not in KINDS:
        raise ValueError("unknown lobby type")
    return {"name":name, "kind":kind, "owner":owner, "members":{owner},
            "spectators":set(), "invites":set()}

def new_invite(room, token):
    if token != room["owner"]:
        raise PermissionError("only host can invite")
    invite = secrets.token_urlsafe(18)
    room["invites"].add(invite)
    return invite

def join_room(room, token, role="player", invite=None, max_players=8, max_spectators=8):
    if role not in ROLES:
        raise ValueError("invalid role")
    if role == "spectator" and room["kind"] == "creator":
        raise PermissionError("creator lobby is not spectatable by default")
    # Access is enforced for both roles, including spectators.
    is_member = token in room["members"] or token in room["spectators"]
    if room["kind"] != "public" and not is_member:
        if not isinstance(invite,str) or invite not in room["invites"]:
            raise PermissionError("invite required")
    target = room["members"] if role == "player" else room["spectators"]
    if token not in target and len(target) >= (max_players if role == "player" else max_spectators):
        raise OverflowError("lobby full")
    room["members"].discard(token)
    room["spectators"].discard(token)
    target.add(token)
    if not is_member and room["kind"] != "public":
        room["invites"].discard(invite)  # one-time room capability
    return role

def leave_room(room, token):
    room["members"].discard(token)
    room["spectators"].discard(token)
    return not room["members"] and not room["spectators"]

def can_manage(room, token):
    return token == room["owner"]

def visible(room, token):
    return room["kind"] == "public" or token in room["members"] or token in room["spectators"]
