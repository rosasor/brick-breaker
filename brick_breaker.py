import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_SIZE = 10
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 8
BALL_SPEED = 5
INITIAL_LIVES = 3
POWERUP_SPEED = 3
POWERUP_SIZE = 20
POWERUP_CHANCE = 0.2  # 20% chance for power-up to spawn

# Power-up chances (percentages)
POWERUP_CHANCES = {
    'extend': 0.15,    # 15% chance
    'shrink': 0.20,    # 20% chance
    'speed_up': 0.10,  # 10% chance
    'extra_life': 0.05,  # 5% chance
    'multi_ball': 0.08  # 8% chance
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 128, 0)
BRICK_COLORS = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]

# Brick types
BRICK_TYPES = {
    'normal': {'hits': 1, 'color': WHITE, 'points': 10},
    'tough': {'hits': 2, 'color': ORANGE, 'points': 20},
    'super': {'hits': 3, 'color': RED, 'points': 30}
}

# Level definitions
LEVELS = {
    'Classic': {
        'description': 'Traditional rows of bricks',
        'pattern': lambda: create_classic_pattern()
    },
    'Pyramid': {
        'description': 'Triangular formation',
        'pattern': lambda: create_pyramid_pattern()
    },
    'Diamond': {
        'description': 'Diamond shaped pattern',
        'pattern': lambda: create_diamond_pattern()
    },
    'Fortress': {
        'description': 'Strong bricks surrounded by weak ones',
        'pattern': lambda: create_fortress_pattern()
    }
}

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        # Choose power-up type based on weighted probabilities
        power_up_type = random.choices(
            list(POWERUP_CHANCES.keys()),
            weights=list(POWERUP_CHANCES.values())
        )[0]
        self.type = power_up_type
        self.speed = POWERUP_SPEED
        
        # Set color based on power-up type
        self.color = {
            'extend': BLUE,
            'shrink': RED,
            'speed_up': YELLOW,
            'extra_life': GREEN,
            'multi_ball': PURPLE
        }[self.type]
    
    def move(self):
        self.rect.y += self.speed
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - 40
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.power_up_timer = 0

    def apply_power_up(self, power_up_type):
        if power_up_type == 'extend':
            self.width = min(200, self.width * 1.5)
        elif power_up_type == 'shrink':
            self.width = max(50, self.width * 0.75)
        elif power_up_type == 'speed_up':
            self.speed = min(16, self.speed * 1.5)
        self.power_up_timer = 600  # 10 seconds at 60 FPS
    
    def update(self):
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer == 0:
                # Reset paddle to normal
                self.width = PADDLE_WIDTH
                self.speed = 8
        self.rect.width = self.width

    def move(self, direction):
        self.x += direction * self.speed
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.width))
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

class Ball:
    def __init__(self, paddle):
        self.radius = BALL_SIZE // 2
        self.x = 0  # Initialize x and y to default values
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.in_play = False
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.reset(paddle)

    def reset(self, paddle):
        if paddle:  # Only use paddle position if paddle is provided
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - self.radius
            self.in_play = False
            self.dx = random.choice([-1, 1]) * BALL_SPEED
            self.dy = -BALL_SPEED
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                              self.radius * 2, self.radius * 2)

    def clone(self):
        new_ball = Ball(None)  # Create new ball without paddle
        new_ball.x = self.x    # Copy position from existing ball
        new_ball.y = self.y
        new_ball.dx = self.dx * random.choice([0.8, 1, 1.2])  # Slightly different speeds
        new_ball.dy = self.dy * random.choice([0.8, 1, 1.2])
        new_ball.rect = pygame.Rect(new_ball.x - self.radius, new_ball.y - self.radius,
                                  self.radius * 2, self.radius * 2)
        new_ball.in_play = True
        return new_ball

    def move(self):
        if not self.in_play:
            return

        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

        # Wall collisions
        if self.x <= self.radius or self.x >= WINDOW_WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius:
            self.dy *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

class Brick:
    def __init__(self, x, y, brick_type='normal'):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.type = brick_type
        self.hits_left = BRICK_TYPES[brick_type]['hits']
        self.points = BRICK_TYPES[brick_type]['points']
        self.update_color()
    
    def hit(self):
        self.hits_left -= 1
        self.update_color()
        return self.hits_left <= 0, self.points
    
    def update_color(self):
        if self.type == 'normal':
            self.color = BRICK_TYPES['normal']['color']
        else:
            # Gradient from red to orange to yellow based on hits left
            if self.hits_left == 3:
                self.color = RED
            elif self.hits_left == 2:
                self.color = ORANGE
            else:
                self.color = YELLOW

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw hit points indicator if more than 1 hit required
        if self.hits_left > 1:
            font = pygame.font.Font(None, 24)
            text = font.render(str(self.hits_left), True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

def create_classic_pattern():
    bricks = []
    for row in range(BRICK_ROWS):
        y = row * (BRICK_HEIGHT + 5) + 50
        for col in range(BRICK_COLS):
            x = col * (BRICK_WIDTH + 2) + (WINDOW_WIDTH - (BRICK_COLS * (BRICK_WIDTH + 2) - 2)) // 2
            brick_type = 'normal'
            if row < 2:  # Top two rows are tougher
                brick_type = 'tough' if row == 0 else 'normal'
            bricks.append(Brick(x, y, brick_type))
    return bricks

def create_pyramid_pattern():
    bricks = []
    max_cols = BRICK_COLS
    for row in range(BRICK_ROWS):
        cols = max_cols - row * 2
        if cols <= 0:
            break
        y = row * (BRICK_HEIGHT + 5) + 50
        start_x = (WINDOW_WIDTH - (cols * (BRICK_WIDTH + 2) - 2)) // 2
        for col in range(cols):
            x = start_x + col * (BRICK_WIDTH + 2)
            brick_type = 'super' if row == 0 else 'tough' if row == 1 else 'normal'
            bricks.append(Brick(x, y, brick_type))
    return bricks

def create_diamond_pattern():
    bricks = []
    max_rows = 7
    max_cols = 7
    center_row = max_rows // 2
    center_col = max_cols // 2
    
    for row in range(max_rows):
        y = row * (BRICK_HEIGHT + 5) + 50
        for col in range(max_cols):
            # Calculate distance from center
            row_dist = abs(row - center_row)
            col_dist = abs(col - center_col)
            if row_dist + col_dist <= center_row:  # Diamond shape
                x = (WINDOW_WIDTH - max_cols * (BRICK_WIDTH + 2)) // 2 + col * (BRICK_WIDTH + 2)
                # Tougher bricks near the center
                dist_from_center = row_dist + col_dist
                if dist_from_center == 0:
                    brick_type = 'super'
                elif dist_from_center == 1:
                    brick_type = 'tough'
                else:
                    brick_type = 'normal'
                bricks.append(Brick(x, y, brick_type))
    return bricks

def create_fortress_pattern():
    bricks = []
    rows = 6
    cols = 8
    for row in range(rows):
        y = row * (BRICK_HEIGHT + 5) + 50
        for col in range(cols):
            x = col * (BRICK_WIDTH + 2) + (WINDOW_WIDTH - (cols * (BRICK_WIDTH + 2) - 2)) // 2
            # Create fortress pattern with tough bricks in the middle
            if 1 <= row <= 4 and 2 <= col <= 5:
                brick_type = 'super' if (row in [2, 3] and col in [3, 4]) else 'tough'
            else:
                brick_type = 'normal'
            bricks.append(Brick(x, y, brick_type))
    return bricks

def show_start_screen():
    play_button = Button(WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 25, 100, 50, "PLAY", GREEN)
    
    while True:
        screen.fill(BLACK)
        
        # Draw title
        font = pygame.font.Font(None, 74)
        title = font.render("BRICK BREAKER", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        screen.blit(title, title_rect)
        
        # Draw play button
        play_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    return True

def show_game_over_screen(score):
    retry_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50, "Play Again", GREEN)
    
    while True:
        screen.fill(BLACK)
        
        # Draw Game Over
        font = pygame.font.Font(None, 74)
        title = font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        screen.blit(title, title_rect)
        
        # Draw final score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        screen.blit(score_text, score_rect)
        
        # Draw retry button
        retry_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.is_clicked(event.pos):
                    return True

def show_win_screen(score):
    continue_button = Button(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 25, 200, 50, "Play Again", GREEN)
    
    while True:
        screen.fill(BLACK)
        
        # Draw Win message
        font = pygame.font.Font(None, 74)
        title = font.render("YOU WIN!", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//4))
        screen.blit(title, title_rect)
        
        # Draw final score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Score: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        screen.blit(score_text, score_rect)
        
        # Draw continue button
        continue_button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.is_clicked(event.pos):
                    return True

def check_collision(ball, rect):
    if ball.rect.colliderect(rect):
        # Find the collision side
        if abs(ball.rect.bottom - rect.top) < 10 and ball.dy > 0:
            ball.dy *= -1
        elif abs(ball.rect.top - rect.bottom) < 10 and ball.dy < 0:
            ball.dy *= -1
        elif abs(ball.rect.right - rect.left) < 10 and ball.dx > 0:
            ball.dx *= -1
        elif abs(ball.rect.left - rect.right) < 10 and ball.dx < 0:
            ball.dx *= -1
        return True
    return False

def show_level_select_screen():
    buttons = []
    y_start = WINDOW_HEIGHT // 4
    for i, (level_name, level_info) in enumerate(LEVELS.items()):
        button = Button(
            WINDOW_WIDTH//2 - 150,
            y_start + i * 80,
            300,
            60,
            level_name,
            GREEN
        )
        buttons.append((button, level_name))
    
    while True:
        screen.fill(BLACK)
        
        # Draw title
        font = pygame.font.Font(None, 74)
        title = font.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        screen.blit(title, title_rect)
        
        # Draw buttons and descriptions
        desc_font = pygame.font.Font(None, 24)
        for button, level_name in buttons:
            button.draw(screen)
            desc = desc_font.render(LEVELS[level_name]['description'], True, WHITE)
            desc_rect = desc.get_rect(
                midtop=(button.rect.centerx, button.rect.bottom + 5)
            )
            screen.blit(desc, desc_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button, level_name in buttons:
                    if button.is_clicked(event.pos):
                        return level_name

def main():
    while True:
        # Start with the start screen
        if not show_start_screen():
            break
        
        # Show level select screen
        selected_level = show_level_select_screen()
        
        # Initialize game objects
        paddle = Paddle()
        ball = Ball(paddle)
        balls = [ball]  # List to hold multiple balls
        bricks = LEVELS[selected_level]['pattern']()
        power_ups = []
        score = 0
        lives = INITIAL_LIVES
        game_font = pygame.font.Font(None, 36)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not any(ball.in_play for ball in balls):
                    for ball in balls:
                        ball.in_play = True
            
            # Move paddle
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                paddle.move(-1)
            if keys[pygame.K_RIGHT]:
                paddle.move(1)
            
            # Update paddle power-ups
            paddle.update()
            
            # Update all balls
            for ball in balls[:]:
                if not ball.in_play:
                    ball.x = paddle.x + paddle.width // 2
                    ball.y = paddle.y - ball.radius
                else:
                    ball.move()
                
                # Check paddle collision for each ball
                if check_collision(ball, paddle.rect):
                    relative_intersect_x = (paddle.x + paddle.width/2) - ball.x
                    normalized_intersect = relative_intersect_x / (paddle.width/2)
                    bounce_angle = normalized_intersect * 60
                    ball.dx = -BALL_SPEED * pygame.math.Vector2.from_polar((1, bounce_angle))[0]
                    ball.dy = -abs(ball.dy)
                
                # Check brick collisions for each ball
                for brick in bricks[:]:
                    if check_collision(ball, brick.rect):
                        destroyed, points = brick.hit()
                        if destroyed:
                            bricks.remove(brick)
                            score += points
                            # Chance to spawn power-up
                            if random.random() < sum(POWERUP_CHANCES.values()):
                                power_ups.append(PowerUp(brick.rect.centerx, brick.rect.centery))
                
                # Ball out of bounds
                if ball.y > WINDOW_HEIGHT:
                    balls.remove(ball)
                    if len(balls) == 0:
                        lives -= 1
                        if lives <= 0:
                            if show_game_over_screen(score):
                                break
                            else:
                                running = False
                        new_ball = Ball(paddle)
                        balls.append(new_ball)
            
            # Update and check power-ups
            for power_up in power_ups[:]:
                power_up.move()
                if power_up.rect.colliderect(paddle.rect):
                    if power_up.type == 'extra_life':
                        lives += 1
                    elif power_up.type == 'multi_ball':
                        # Create two new balls
                        new_balls = []
                        for _ in range(2):
                            for existing_ball in balls:
                                if existing_ball.in_play:
                                    new_balls.append(existing_ball.clone())
                        balls.extend(new_balls[:2])  # Add up to 2 new balls
                    else:
                        paddle.apply_power_up(power_up.type)
                    power_ups.remove(power_up)
                elif power_up.rect.top > WINDOW_HEIGHT:
                    power_ups.remove(power_up)
            
            # Check win condition
            if len(bricks) == 0:
                if show_win_screen(score):
                    break
                else:
                    running = False
            
            # Draw everything
            screen.fill(BLACK)
            paddle.draw(screen)
            for ball in balls:
                ball.draw(screen)
            for brick in bricks:
                brick.draw(screen)
            for power_up in power_ups:
                power_up.draw(screen)
            
            # Draw score and lives
            score_text = game_font.render(f"Score: {score}", True, WHITE)
            lives_text = game_font.render(f"Lives: {lives}", True, WHITE)
            balls_text = game_font.render(f"Balls: {len(balls)}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (WINDOW_WIDTH - 100, 10))
            screen.blit(balls_text, (WINDOW_WIDTH - 100, 40))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    main() 