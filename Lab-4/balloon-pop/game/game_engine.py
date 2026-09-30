"""
GameEngine: owns all balloons, spawns new ones, and handles clicks.

Version 4: three balloon types, a lives system, and a 30-second timed
round. The round ends when time runs out OR lives reach zero. Press R
after the round ends to start a new one.
"""

import random

import pygame

from game.balloon import Balloon, BALLOON_TYPES
from game.click_detection import check_pop
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 45
STARTING_LIVES = 3
ROUND_SECONDS = 30


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        """Start a fresh round: score, lives, timer, and balloons all reset."""
        self.balloons = []
        self.frames_until_spawn = 0
        self.score = 0
        self.lives = STARTING_LIVES
        self.time_left = float(ROUND_SECONDS)
        self.round_start = pygame.time.get_ticks()
        self.game_over = False
        self.end_reason = ""

    def _end_round(self, reason):
        self.game_over = True
        self.end_reason = reason

    def _choose_kind(self):
        kinds = list(BALLOON_TYPES.keys())
        weights = [BALLOON_TYPES[k]["weight"] for k in kinds]
        return random.choices(kinds, weights=weights, k=1)[0]

    def _spawn_balloon(self):
        radius = random.randint(16, 44)
        x = random.randint(radius + 10, WIDTH - radius - 10)
        speed = random.uniform(1.5, 3.0)
        kind = self._choose_kind()
        self.balloons.append(
            Balloon(x=x, y=-radius, radius=radius, speed=speed, kind=kind)
        )

    def handle_click(self, pos):
        # No clicks are accepted once the round has ended.
        if self.game_over:
            return

        popped = check_pop(self.balloons, pos)
        if popped is not None:
            self.balloons.remove(popped)
            self.score += popped.points
            # Popping a balloon never changes self.lives.

    def handle_key(self, key):
        # Press R after the round ends to start a new one.
        if self.game_over and key == pygame.K_r:
            self.reset()

    def update(self):
        # Frozen once the round has ended: no spawning, no movement.
        if self.game_over:
            return

        # Countdown timer (real time, so it is accurate even if FPS dips).
        elapsed = (pygame.time.get_ticks() - self.round_start) / 1000
        self.time_left = max(0.0, ROUND_SECONDS - elapsed)
        if self.time_left <= 0:
            self._end_round("Time's up!")
            return

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_balloon()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for b in self.balloons:
            b.update()

        # Balloons that reached the bottom unpopped cost a life.
        missed = [b for b in self.balloons if b.is_past_bottom(HEIGHT)]
        if missed:
            self.lives -= len(missed)
            self.balloons = [b for b in self.balloons if b not in missed]

        if self.lives <= 0:
            self.lives = 0
            self._end_round("Out of lives!")

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.balloons)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Time: {int(self.time_left + 0.999)}", (WIDTH // 2 - 50, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (WIDTH - 130, 10))

        if self.game_over:
            renderer.draw_game_over(surface, font, self.end_reason, self.score)