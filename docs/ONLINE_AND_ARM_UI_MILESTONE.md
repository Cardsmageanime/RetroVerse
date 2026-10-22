# Online and ARM interface integration (prototype)

## Status and boundaries

The Neon Showcase remains a browser prototype. The new Online service is an **actual running asyncio TCP JSON-lines room/chat prototype**, but is **not real-time game synchronization, rollback netcode, identity authentication, moderation, encryption, or an Internet-ready service**. It defaults to **127.0.0.1:8766** and intentionally refuses external binding. The existing Neon Showcase demo chat is **not yet connected** to this server.

Run server on a development computer:
```sh
python3 online/server/lobby_server.py
```
Protocol: send UTF-8 newline-delimited JSON dictionaries, one per line. First: `{"action":"hello","name":"Player1"}`. Other actions: `list`, `create` with `name`, `join` with `room`, `leave`, `chat` with `text`. Chat recipients receive an event record; caller receives an acknowledgement. Ephemeral in-memory data is lost when the server stops.

Run tests:
```sh
python3 -m unittest online/server/test_lobby_server.py -v
```

## ARM Linux interface

`boot/tools/launch_neon_arm.sh` opens the existing interface in a Chromium kiosk, **only on an already booted Linux machine with a working graphical session**. It detects Chromium and refuses to run without a usable display. It does not install packages or change boot configuration.

```sh
sh boot/tools/launch_neon_arm.sh
```

The kiosk launcher is not yet integrated into the RetroVerse root filesystem or automatically started on the physical Vayava GameBox. The G12A/U212 boot path, DRM/HDMI graphics, controller handling in that session, and successful physical launch remain **unverified**.

## Required next gates

1. Boot a board-compatible Linux image on the GameBox from removable media while preserving internal Android.
2. Validate display, graphics and input on that physical Linux build.
3. Build a dedicated frontend runtime and offline game scanner / RetroArch bridge.
4. Add authentication, transport security, rate limits, room permissions, moderation and server deployment before exposing multiplayer beyond loopback.
5. Implement emulator-compatible game synchronization before describing multiplayer gameplay as working.
