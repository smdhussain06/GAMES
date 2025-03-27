import pygame
import pygame.gfxdraw
import sys
import random
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
BORDER_PADDING = 50
GAME_WIDTH = WINDOW_WIDTH - 2 * BORDER_PADDING
GAME_HEIGHT = WINDOW_HEIGHT - 2 * BORDER_PADDING
GRID_SIZE = 20
GRID_WIDTH = GAME_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors
BACKGROUND_COLOR = (20, 20, 20)
SNAKE_COLOR = (220, 220, 220)  # White Snake Color
FOOD_COLOR = (240, 80, 80)
SCORE_TEXT_COLOR = (240, 240, 240)
SCORE_TITLE_COLOR = (150, 150, 150)  # Grey Score Title
GAME_OVER_TEXT_COLOR = (255, 100, 100)
UI_ELEMENT_COLOR = (80, 80, 80)

# Game settings
FPS = 60
INITIAL_SPEED = 8
SNAKE_ROUNDNESS = 0.4  # Increased roundness

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Snake Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 56)
        self.font_small = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.move_counter = 0
        self.growth_animation = 0

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in self.snake:
                return pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                elif not self.game_over:
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
        return True

    def update(self):
        if self.game_over:
            return

        self.move_counter += 1
        if self.move_counter < FPS // self.speed:
            return

        self.move_counter = 0
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.speed = min(INITIAL_SPEED + self.score // 5, 15)
            self.food = self.spawn_food()
            self.growth_animation = 5
        else:
            self.snake.pop()

    def draw_snake_segment(self, segment, index, snake_length):
        x = BORDER_PADDING + segment[0] * GRID_SIZE
        y = BORDER_PADDING + segment[1] * GRID_SIZE
        segment_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)

        rect_radius = int(GRID_SIZE * SNAKE_ROUNDNESS)

        # Make head and tail rounder
        if index == 0 or index == snake_length - 1:
            rect_radius = int(GRID_SIZE * (SNAKE_ROUNDNESS + 0.1))  #slightly more round for head/tail
        pygame.draw.rect(self.screen, SNAKE_COLOR, segment_rect, border_radius=rect_radius)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        pygame.draw.rect(self.screen, UI_ELEMENT_COLOR, (BORDER_PADDING - 5, BORDER_PADDING - 5, GAME_WIDTH + 10, GAME_HEIGHT + 10), 2, border_radius=10)

        for i, segment in enumerate(self.snake):
            self.draw_snake_segment(segment, i, len(self.snake))

        food_pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        food_radius = int((GRID_SIZE * 0.5) * (0.9 + food_pulse * 0.1))
        food_center_x = BORDER_PADDING + self.food[0] * GRID_SIZE + GRID_SIZE // 2
        food_center_y = BORDER_PADDING + self.food[1] * GRID_SIZE + GRID_SIZE // 2

        pygame.gfxdraw.aacircle(self.screen, int(food_center_x), int(food_center_y), food_radius, FOOD_COLOR)
        pygame.gfxdraw.filled_circle(self.screen, int(food_center_x), int(food_center_y), food_radius, FOOD_COLOR)

        # Draw Score - Modern UI Style, Top Right
        score_title_surface = self.font_small.render("Score:", True, SCORE_TITLE_COLOR)
        score_title_rect = score_title_surface.get_rect(topright=(WINDOW_WIDTH - BORDER_PADDING + 10, BORDER_PADDING - 30))  # Outside border

        score_text_surface = self.font_large.render(f"{self.score}", True, SCORE_TEXT_COLOR)
        score_rect = score_text_surface.get_rect(topright=(WINDOW_WIDTH - BORDER_PADDING + 10, BORDER_PADDING + 10))  # Adjusted Position slightly lower

        self.screen.blit(score_title_surface, score_title_rect)
        self.screen.blit(score_text_surface, score_rect)

        if self.game_over:
            game_over_text = self.font_large.render("Game Over!", True, GAME_OVER_TEXT_COLOR)
            restart_text = self.font_small.render("Press SPACE to Restart", True, SCORE_TEXT_COLOR)

            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 40))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 40))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
    pygame.quit()
    sys.exit()
