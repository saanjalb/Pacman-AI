import pygame
import random
import heapq

pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man AI Chase")

# Colors
BLACK = (0, 0, 0)
BLUE = (30, 30, 150)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 100, 255)

# Fonts
font = pygame.font.SysFont("arial", 22, bold=True)
big_font = pygame.font.SysFont("arial", 40, bold=True)

# Directions
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


# ---- GRID & MAZE ----
def make_maze():
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    # Add borders
    for x in range(COLS):
        grid[0][x] = 1
        grid[ROWS - 1][x] = 1
    for y in range(ROWS):
        grid[y][0] = 1
        grid[y][COLS - 1] = 1

    # Random barriers
    for _ in range(100):
        x, y = random.randint(1, COLS - 2), random.randint(1, ROWS - 2)
        grid[y][x] = 1

    # Keep start and end open
    grid[1][1] = 0
    grid[ROWS - 2][COLS - 2] = 0
    return grid


# ---- A* PATHFINDING ----
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal):
    queue = [(0, start)]
    came_from = {start: None}
    g_score = {start: 0}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break

        for dx, dy in DIRS:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
                tentative_g = g_score[current] + 1
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = tentative_g
                    f_score = tentative_g + heuristic((nx, ny), goal)
                    heapq.heappush(queue, (f_score, (nx, ny)))
                    came_from[(nx, ny)] = current

    # reconstruct path
    if goal not in came_from:
        return []
    path, cur = [], goal
    while cur:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path


# ---- GAME OBJECTS ----
class Pacman:
    def __init__(self, x, y):
        self.pos = [x, y]

    def move(self, dx, dy, grid):
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            self.pos = [nx, ny]


class Ghost:
    def __init__(self, x, y, color):
        self.pos = [x, y]
        self.color = color

    def chase(self, pac_pos, grid):
        path = astar(grid, tuple(self.pos), tuple(pac_pos))
        if len(path) > 1:
            self.pos = list(path[1])


# ---- DRAWING ----
def draw(win, grid, pacman, ghosts, pellets, score, lives, game_over, win_flag):
    win.fill(BLACK)

    # Draw walls
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 1:
                pygame.draw.rect(win, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw pellets
    for (x, y) in pellets:
        pygame.draw.circle(win, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 6)

    # Draw Pacman
    pygame.draw.circle(win, YELLOW, (pacman.pos[0] * CELL_SIZE + CELL_SIZE // 2, pacman.pos[1] * CELL_SIZE + CELL_SIZE // 2), 8)

    # Draw ghosts
    for ghost in ghosts:
        pygame.draw.circle(win, ghost.color, (ghost.pos[0] * CELL_SIZE + CELL_SIZE // 2, ghost.pos[1] * CELL_SIZE + CELL_SIZE // 2), 8)

    # Draw score/lives
    text = font.render(f"Score: {score}   Lives: {lives}", True, WHITE)
    win.blit(text, (10, 10))

    if game_over:
        msg = big_font.render("GAME OVER!", True, RED)
        win.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
    elif win_flag:
        msg = big_font.render("YOU WIN!", True, PINK)
        win.blit(msg, (WIDTH // 2 - 80, HEIGHT // 2 - 20))

    pygame.display.update()


# ---- START SCREEN ----
def start_screen():
    waiting = True
    while waiting:
        WIN.fill(BLACK)
        title = big_font.render("PAC-MAN AI CHASE", True, YELLOW)
        info = font.render("Press ENTER to Start", True, WHITE)
        controls = font.render("Use Arrow Keys to Move", True, PINK)
        WIN.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 80))
        WIN.blit(info, (WIDTH // 2 - 100, HEIGHT // 2))
        WIN.blit(controls, (WIDTH // 2 - 130, HEIGHT // 2 + 40))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    return True


# ---- MAIN LOOP ----
def main():
    if not start_screen():
        return  # Exit if player quits on start screen

    grid = make_maze()
    pacman = Pacman(1, 1)
    ghosts = [Ghost(COLS - 2, ROWS - 2, RED)]

    # Spawn pellets
    open_cells = [(x, y) for x in range(COLS) for y in range(ROWS) if grid[y][x] == 0 and (x, y) not in [(1, 1), (COLS - 2, ROWS - 2)]]
    random.shuffle(open_cells)
    pellets = set(open_cells[:10])

    score = 0
    lives = 3
    game_over = False
    win_flag = False

    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if not game_over and not win_flag:
            if keys[pygame.K_UP]:
                pacman.move(0, -1, grid)
            if keys[pygame.K_DOWN]:
                pacman.move(0, 1, grid)
            if keys[pygame.K_LEFT]:
                pacman.move(-1, 0, grid)
            if keys[pygame.K_RIGHT]:
                pacman.move(1, 0, grid)

        # Eat pellets
        if tuple(pacman.pos) in pellets:
            pellets.remove(tuple(pacman.pos))
            score += 10

        # Ghost chasing
        if not game_over and not win_flag:
            for ghost in ghosts:
                ghost.chase(pacman.pos, grid)
                if ghost.pos == pacman.pos:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    else:
                        pacman = Pacman(1, 1)
                        pygame.time.delay(300)

        # Win condition
        if not pellets:
            win_flag = True

        draw(WIN, grid, pacman, ghosts, pellets, score, lives, game_over, win_flag)

    pygame.quit()


if __name__ == "__main__":
    main()