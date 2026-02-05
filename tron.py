# ...existing code...
import os
import pygame
import sys

# ---------------- CONFIG ----------------
CELL_SIZE = 10
GRID_WIDTH = 90
GRID_HEIGHT = 70
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 15

# Colors
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
RED = (255, 70, 70)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_RED = (255, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

pygame.init()
pygame.font.init()  # ensure font module is initialized
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("TRON")
clock = pygame.time.Clock()

# Fonts - prefer Arial, fall back to default if not found
font_path = pygame.font.match_font("arial")
small_font = pygame.font.Font(font_path, 30)

# ---------------- LOAD TRON LOGO ----------------
# Try loading a local 'tron.png' next to this script; fallback to a simple surface if missing.
try:
    logo_path = os.path.join(os.path.dirname(__file__), "tron.png")
except NameError:
    # Fallback if __file__ is not defined (interactive environments)
    logo_path = "tron.png"

try:
    tron_logo = pygame.image.load(logo_path).convert_alpha()
    tron_logo = pygame.transform.scale(tron_logo, (WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
except Exception:
    tron_logo = pygame.Surface((WINDOW_WIDTH//2, WINDOW_HEIGHT//4), pygame.SRCALPHA)
    tron_logo.fill((0, 0, 0, 0))
    title = small_font.render("TRON", True, NEON_BLUE)
    tron_logo.blit(title, (tron_logo.get_width()//2 - title.get_width()//2, tron_logo.get_height()//2 - title.get_height()//2))

# ---------------- UTILITY FUNCTIONS ----------------
def add(pos, d):
    return (pos[0] + d[0], pos[1] + d[1])

def in_bounds(pos):
    return 0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT

def distance_to_wall(pos):
    return min(pos[0], pos[1], GRID_WIDTH - pos[0] - 1, GRID_HEIGHT - pos[1] - 1)

# ---------------- BIKE CLASS ----------------
class Bike:
    def __init__(self, pos, direction, color):
        self.pos = pos
        self.direction = direction
        self.trail = {pos}
        self.color = color
        self.alive = True

    def move(self):
        self.pos = add(self.pos, self.direction)
        self.trail.add(self.pos)

    def draw(self):
        for t in self.trail:
            pygame.draw.rect(screen, self.color, (t[0]*CELL_SIZE, t[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

# ---------------- HARD AI ----------------
def ai_choose_direction(ai, opponent):
    best_score = -999999
    best_dir = ai.direction

    for d in DIRECTIONS:
        if d == (-ai.direction[0], -ai.direction[1]):
            continue
        next_pos = add(ai.pos, d)
        if not in_bounds(next_pos):
            continue
        if next_pos in ai.trail or next_pos in opponent.trail:
            continue

        score = 0
        if d == ai.direction: score += 8
        wall_dist = distance_to_wall(next_pos)
        score += wall_dist * 3

        # Look ahead
        open_space = 0
        temp = next_pos
        for _ in range(8):
            temp = add(temp, d)
            if not in_bounds(temp) or temp in ai.trail or temp in opponent.trail:
                break
            open_space += 1
        score += open_space * 4
        if wall_dist <= 1: score -= 50

        if score > best_score:
            best_score = score
            best_dir = d

    return best_dir

# ---------------- SCREENS ----------------
def draw_start_screen():
    screen.fill(BLACK)
    screen.blit(tron_logo, (WINDOW_WIDTH//2 - tron_logo.get_width()//2, WINDOW_HEIGHT//6))
    title = small_font.render("Press 1: Single-player (WASD blue, arrows red AI)", True, NEON_BLUE)
    title2 = small_font.render("Press 2: Local 2-player (WASD = Blue, Arrows = Red)", True, NEON_RED)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//2 - 30))
    screen.blit(title2, (WINDOW_WIDTH//2 - title2.get_width()//2, WINDOW_HEIGHT//2 + 10))
    pygame.display.flip()

def draw_victory_screen():
    screen.fill(BLACK)
    text = small_font.render("BLUE WINS!", True, NEON_BLUE)
    prompt = small_font.render("Press any key to play again (1=single, 2=2-player)", True, NEON_RED)
    screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//3))
    screen.blit(prompt, (WINDOW_WIDTH//2 - prompt.get_width()//2, WINDOW_HEIGHT//2))
    pygame.display.flip()

def draw_loss_screen():
    screen.fill(BLACK)
    text = small_font.render("RED WINS!", True, NEON_RED)
    prompt = small_font.render("Press any key to play again (1=single, 2=2-player)", True, NEON_BLUE)
    screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//3))
    screen.blit(prompt, (WINDOW_WIDTH//2 - prompt.get_width()//2, WINDOW_HEIGHT//2))
    pygame.display.flip()

def wait_for_key(mode_select=False):
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if mode_select:
                    if event.key == pygame.K_1:
                        return False
                    elif event.key == pygame.K_2:
                        return True
                return None

# ---------------- GAME FUNCTION ----------------
def play_game(two_player=False):
    # Blue is left, Red is right
    blue = Bike((10, GRID_HEIGHT//2), RIGHT, BLUE)
    red = Bike((GRID_WIDTH-10, GRID_HEIGHT//2), LEFT, RED)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Two-player: Blue uses WASD, Red uses arrows
                if two_player:
                    # Blue controls (WASD)
                    if event.key == pygame.K_w and blue.direction != DOWN:
                        blue.direction = UP
                    elif event.key == pygame.K_s and blue.direction != UP:
                        blue.direction = DOWN
                    elif event.key == pygame.K_a and blue.direction != RIGHT:
                        blue.direction = LEFT
                    elif event.key == pygame.K_d and blue.direction != LEFT:
                        blue.direction = RIGHT

                    # Red controls (Arrows)
                    if event.key == pygame.K_UP and red.direction != DOWN:
                        red.direction = UP
                    elif event.key == pygame.K_DOWN and red.direction != UP:
                        red.direction = DOWN
                    elif event.key == pygame.K_LEFT and red.direction != RIGHT:
                        red.direction = LEFT
                    elif event.key == pygame.K_RIGHT and red.direction != LEFT:
                        red.direction = RIGHT
                else:
                    # Single-player: Blue controlled by WASD, Red is AI
                    if event.key == pygame.K_w and blue.direction != DOWN:
                        blue.direction = UP
                    elif event.key == pygame.K_s and blue.direction != UP:
                        blue.direction = DOWN
                    elif event.key == pygame.K_a and blue.direction != RIGHT:
                        blue.direction = LEFT
                    elif event.key == pygame.K_d and blue.direction != LEFT:
                        blue.direction = RIGHT

        # ---------------- COLLISION CHECK ----------------
        blue_next = add(blue.pos, blue.direction)
        if two_player:
            red_next = add(red.pos, red.direction)
        else:
            # predict AI next
            red_next = add(red.pos, ai_choose_direction(red, blue))

        if (not in_bounds(blue_next)) or (blue_next in blue.trail) or (blue_next in red.trail):
            blue.alive = False
        if (not in_bounds(red_next)) or (red_next in red.trail) or (red_next in blue.trail):
            red.alive = False

        if not blue.alive or not red.alive:
            # True if blue won (red dead, blue alive). tie or blue dead => not win
            return blue.alive and not red.alive

        # ---------------- MOVE ----------------
        blue.move()
        if two_player:
            red.move()
        else:
            red.direction = ai_choose_direction(red, blue)
            red.move()

        # ---------------- DRAW ----------------
        screen.fill(BLACK)
        blue.draw()
        red.draw()
        pygame.display.flip()

# ---------------- MAIN LOOP ----------------
while True:
    draw_start_screen()
    two_player_mode = wait_for_key(mode_select=True)
    player_won = play_game(two_player_mode)
    if player_won:
        draw_victory_screen()
    else:
        draw_loss_screen()
    wait_for_key()
# ...existing code...