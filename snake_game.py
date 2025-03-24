import pygame
import pygame.gfxdraw
import sys
import random
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
GRID_SIZE = 25  # Adjusted for better proportion in 1000x1000
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Monochromatic Colors
BACKGROUND_COLOR = (0, 0, 0)      # Black
SNAKE_COLOR = (255, 255, 255)     # White
FOOD_COLOR = (128, 128, 128)      # Grey
TEXT_COLOR = (255, 255, 255)      # White

# Game settings
FPS = 60
INITIAL_SPEED = 8

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 42)
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
        new_head = (
            (head[0] + self.direction[0]) % GRID_WIDTH,   # Wrap around horizontally
            (head[1] + self.direction[1]) % GRID_HEIGHT   # Wrap around vertically
        )

        # Only check for self collision
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

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw connecting lines first (behind circles)
        for i, segment in enumerate(self.snake[:-1]):  # Stop at second-to-last segment
            color_intensity = max(0.3, 1 - i / len(self.snake))
            segment_color = tuple(int(c * color_intensity) for c in SNAKE_COLOR)
            
            current_x = segment[0] * GRID_SIZE + GRID_SIZE // 2
            current_y = segment[1] * GRID_SIZE + GRID_SIZE // 2
            next_segment = self.snake[i + 1]
            next_x = next_segment[0] * GRID_SIZE + GRID_SIZE // 2
            next_y = next_segment[1] * GRID_SIZE + GRID_SIZE // 2
            
            # Handle screen wrap-around
            dx = current_x - next_x
            dy = current_y - next_y
            
            if abs(dx) > WINDOW_WIDTH // 2:
                if dx > 0:
                    next_x += WINDOW_WIDTH
                else:
                    next_x -= WINDOW_WIDTH
            if abs(dy) > WINDOW_HEIGHT // 2:
                if dy > 0:
                    next_y += WINDOW_HEIGHT
                else:
                    next_y -= WINDOW_HEIGHT
            
            # Draw thick connecting line
            pygame.draw.line(self.screen, segment_color, 
                           (current_x, current_y), 
                           (next_x, next_y), 
                           int(GRID_SIZE * 0.8))  # Slightly thinner than the circles

        # Draw snake segments as smooth circles
        for i, segment in enumerate(self.snake):
            color_intensity = max(0.3, 1 - i / len(self.snake))
            segment_color = tuple(int(c * color_intensity) for c in SNAKE_COLOR)
            
            center_x = segment[0] * GRID_SIZE + GRID_SIZE // 2
            center_y = segment[1] * GRID_SIZE + GRID_SIZE // 2
            radius = int(GRID_SIZE * 0.45)  # Slightly smaller radius for smoother appearance
            
            # Draw circle with antialiasing for smoother edges
            pygame.gfxdraw.aacircle(self.screen, center_x, center_y, radius, segment_color)
            pygame.gfxdraw.filled_circle(self.screen, center_x, center_y, radius, segment_color)

        # Draw food with smooth pulsing animation
        food_pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        food_radius = int((GRID_SIZE * 0.4) * (0.8 + food_pulse * 0.2))
        food_center = (self.food[0] * GRID_SIZE + GRID_SIZE // 2,
                      self.food[1] * GRID_SIZE + GRID_SIZE // 2)
        
        # Draw food with antialiasing
        pygame.gfxdraw.aacircle(self.screen, 
                               int(food_center[0]), 
                               int(food_center[1]), 
                               food_radius, 
                               FOOD_COLOR)
        pygame.gfxdraw.filled_circle(self.screen, 
                                   int(food_center[0]), 
                                   int(food_center[1]), 
                                   food_radius, 
                                   FOOD_COLOR)

        # Draw score with slight transparency for better integration
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        score_surface = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10), pygame.SRCALPHA)
        self.screen.blit(score_text, (20, 20))

        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, TEXT_COLOR)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)

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