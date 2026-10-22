"""Authoritative two-player RetroVerse Pong prototype.

Deterministic fixed-step mechanics. Experimental proof of networked gameplay,
NOT emulator netplay or production Internet matchmaking.
"""
from dataclasses import dataclass, field

WIDTH, HEIGHT = 800, 450
PADDLE_H, PADDLE_W = 80, 14
BALL_SIZE = 12
TICK_RATE = 30

@dataclass
class Match:
    paddles: list[float] = field(default_factory=lambda: [HEIGHT / 2, HEIGHT / 2])
    directions: list[int] = field(default_factory=lambda: [0, 0])
    scores: list[int] = field(default_factory=lambda: [0, 0])
    ball_x: float = WIDTH / 2
    ball_y: float = HEIGHT / 2
    vx: float = 6
    vy: float = 3
    tick: int = 0

    def input(self, player: int, direction: int):
        if player not in (0, 1) or direction not in (-1, 0, 1):
            raise ValueError("invalid player or direction")
        self.directions[player] = direction

    def step(self):
        self.tick += 1
        for i in (0, 1):
            self.paddles[i] = max(PADDLE_H / 2, min(HEIGHT - PADDLE_H / 2,
                self.paddles[i] + self.directions[i] * 9))
        self.ball_x += self.vx
        self.ball_y += self.vy
        if self.ball_y <= BALL_SIZE / 2:
            self.ball_y = BALL_SIZE / 2
            self.vy = abs(self.vy)
        elif self.ball_y >= HEIGHT - BALL_SIZE / 2:
            self.ball_y = HEIGHT - BALL_SIZE / 2
            self.vy = -abs(self.vy)
        for i, x in ((0, 38), (1, WIDTH - 38)):
            approaching = self.vx < 0 if i == 0 else self.vx > 0
            contact = (x - PADDLE_W / 2 - BALL_SIZE / 2 <= self.ball_x <= x + PADDLE_W / 2 + BALL_SIZE / 2)
            if approaching and contact and abs(self.ball_y - self.paddles[i]) <= PADDLE_H / 2 + BALL_SIZE / 2:
                self.ball_x = x + (PADDLE_W + BALL_SIZE) / 2 * (1 if i == 0 else -1)
                self.vx = abs(self.vx) if i == 0 else -abs(self.vx)
                self.vy = max(-5, min(5, (self.ball_y - self.paddles[i]) / 10))
        if self.ball_x < -BALL_SIZE:
            self.scores[1] += 1
            self.reset_ball(1)
        elif self.ball_x > WIDTH + BALL_SIZE:
            self.scores[0] += 1
            self.reset_ball(-1)

    def reset_ball(self, direction):
        self.ball_x, self.ball_y = WIDTH / 2, HEIGHT / 2
        self.vx, self.vy = 6 * direction, 3

    def state(self):
        return {"type": "state", "tick": self.tick, "paddles": self.paddles[:],
                "ball": [round(self.ball_x, 2), round(self.ball_y, 2)],
                "scores": self.scores[:]}
