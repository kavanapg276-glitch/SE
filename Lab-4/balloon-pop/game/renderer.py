"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (200, 230, 245)
COLOR_TEXT = (30, 30, 30)


def draw_scene(surface, balloons):
    surface.fill(COLOR_BG)
    for b in balloons:
        pygame.draw.circle(surface, b.color, (int(b.x), int(b.y)), b.radius)
        pygame.draw.line(surface, (120, 120, 120), (b.x, b.y + b.radius), (b.x, b.y + b.radius + 12), 2)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (180, 40, 40))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)


def draw_game_over(surface, font, reason, score):
    """Dim the screen and show why the round ended, the final score,
    and how to restart."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))

    lines = [
        ("GAME OVER", (255, 255, 255)),
        (reason, (255, 120, 120)),
        (f"Final Score: {score}", (255, 210, 0)),
        ("Press R to play again", (255, 255, 255)),
    ]
    center_x = surface.get_width() // 2
    start_y = surface.get_height() // 2 - 60
    for i, (text, color) in enumerate(lines):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(center_x, start_y + i * 40))
        surface.blit(surf, rect)