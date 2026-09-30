"""
Balloon: falls from the top of the screen. The player must pop it
before it reaches the bottom. Balloons vary in size - this matters for
how click detection should work.

Balloons also come in different types (normal, bonus, penalty), each
with its own color, point value, and spawn probability.
"""

import pygame

# Each balloon type: color, points awarded when popped, spawn weight.
# A higher weight means the type spawns more often.
BALLOON_TYPES = {
    "normal":  {"color": (220, 50, 50),  "points": 10,  "weight": 70},  # red
    "bonus":   {"color": (255, 200, 0),  "points": 30,  "weight": 15},  # gold
    "penalty": {"color": (50, 50, 50),   "points": -20, "weight": 15},  # dark gray
}


class Balloon:
    def __init__(self, x, y, radius, speed, kind="normal"):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.kind = kind
        self.color = BALLOON_TYPES[kind]["color"]
        self.points = BALLOON_TYPES[kind]["points"]

    def update(self):
        self.y += self.speed

    def is_past_bottom(self, height):
        return self.y - self.radius > height

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )