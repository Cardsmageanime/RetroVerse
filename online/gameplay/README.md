# RetroVerse — Live Gameplay Prototype

This is the project's **first actual synchronized multiplayer gameplay prototype**, not emulator netplay. The prototype uses a Python **authoritative 30 Hz game server** and a browser-based two-player Pong game. Each player sends direction inputs; the server simulates the ball, paddles, collisions, and scoring, then broadcasts the same state to both clients.

## Try it on your development PC

1. Install Python 3.10+.
2. Install the WebSocket library:
   ```powershell
   py -m pip install "websockets>=14,<17"
   ```
3. Run the server from the repository root:
   ```powershell
   py online/gameplay/pong_server.py
   ```
4. Open `online/gameplay/index.html` in **two browser windows** on that PC, and click **Connect to Game** in each. Each window occupies one player slot.
5. Use arrow keys or W/S. The server controls collision and scoring.

Stop the server with Ctrl+C. To test more than one computer, a separate authenticated and encrypted deployment design is needed; this prototype intentionally binds to loopback (`127.0.0.1`) only.

Run offline engine checks:
```powershell
py -m unittest discover -s online/gameplay -p "test_*.py" -v
```

## What it does and does not prove

This tests the actual multiplayer software path: controller input from browser to server, fixed-timestep simulation on the server, and broadcast world state back to two browser clients. It currently implements **Pong**, not SNES/PS1/PS2 gameplay, RetroArch netplay, rollback, internet multiplayer, chat integration, or dedicated user accounts. No claims of low-latency Internet play, security, hardware GameBox success or emulator compatibility are made.

Do not expose this test server to the Internet: it has no authentication, encryption, moderation, or abuse prevention. Future work should add browser-to-service integrations for the RetroVerse lobby, WebSocket session management, game selection, security, and an emulator-compatible networking model.
