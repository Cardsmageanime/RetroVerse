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

## Controller support and two-player sessions

The Pong browser test now loads `two_player_input.js` to support standard browser Gamepad API controllers and keyboard input. Connect a PlayStation, Xbox, Switch-compatible, or generic controller **recognized by the browser**, then choose it from the controller selector on that browser client. The actual mapping depends on browser/driver support; no claim is made that every controller model is fully compatible. Standard D-pad up/down and left-stick Y are recognized with a deadzone.

**Player 1 versus Player 2:** the WebSocket server assigns one network player slot to each connected browser tab. A controller chosen in a tab sends input **only through that tab's connection**; one client's controller does not control the remote player. For testing on one PC, open two browser windows and select separate controllers (or use a controller in one window and keyboard input in the other). **Note:** browsers may expose both controllers to both windows; explicitly choose the correct device index in each window. Keyboard events go to the focused window.

Run controller regression checks:
```sh
node online/gameplay/test_two_player_input.cjs
```

Limitations: this is **Pong gamepad input**, not RetroArch core controller remapping; the Netplay launcher delegates gameplay input to RetroArch's own controller configuration. There is no built-in controller button-mapping editor yet. Two separate computers and real controller hardware still require hands-on testing.
