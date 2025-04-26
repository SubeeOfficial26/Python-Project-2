import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Load images
player_img = pygame.Surface((50, 40))
player_img.fill((0, 255, 0))

enemy_img = pygame.Surface((30, 30))
enemy_img.fill((255, 0, 0))

bullet_img = pygame.Surface((10, 20))
bullet_img.fill((255, 255, 0))

powerup_img = pygame.Surface((20, 20))
powerup_img.fill((0, 255, 255))

player_mini_img = pygame.transform.scale(player_img, (25, 20))

# Load font
font_name = pygame.font.match_font('arial')

# Draw text
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Draw shield bar
def draw_shield_bar(surface, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, (0, 255, 0), fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Draw lives
def draw_lives(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = SCREEN_WIDTH / 2
            self.rect.bottom = SCREEN_HEIGHT - 10

        if self.power >= 2 and pygame.time.get_ticks() - self.power_timer > 5000:
            self.power -= 1
            self.power_timer = pygame.time.get_ticks()

        self.speedx = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -5   # Move left (correct)
        if keys[pygame.K_RIGHT]:
            self.speedx = 5    # Move right (correct)
        self.rect.x += self.speedx

        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not self.hidden:
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT + 200)

    def powerup(self):
        self.power += 1
        self.power_timer = pygame.time.get_ticks()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Powerup class
class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['shield', 'power'])
        self.image = powerup_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame > 3:
                self.kill()

# Show Game Over screen
def show_game_over():
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    draw_text(screen, "Thank you for playing!", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    pygame.display.flip()
    pygame.time.delay(3000)

# Main game loop
def main_game():
    global all_sprites, bullets, enemies, powerups

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for _ in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    running = True
    game_over = False

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        if not game_over:
            all_sprites.update()

            # Bullet hits enemy
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += 10
                explosion = Explosion(hit.rect.center, 30)
                all_sprites.add(explosion)
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
                if random.random() > 0.5:
                    powerup = Powerup()
                    all_sprites.add(powerup)
                    powerups.add(powerup)

            # Enemy hits player
            hits = pygame.sprite.spritecollide(player, enemies, True)
            for hit in hits:
                player.shield -= 20
                explosion = Explosion(hit.rect.center, 10)
                all_sprites.add(explosion)
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)
                if player.shield <= 0:
                    player.lives -= 1
                    player.shield = 100
                    player.hide()
                    if player.lives == 0:
                        game_over = True

            # Player gets powerup
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.shield += 20
                    if player.shield > 100:
                        player.shield = 100
                if hit.type == 'power':
                    player.powerup()

        # Draw everything
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, SCREEN_WIDTH / 2, 10)
        draw_shield_bar(screen, 5, 5, player.shield)
        draw_lives(screen, SCREEN_WIDTH - 100, 5, player.lives, player_mini_img)

        pygame.display.flip()

        if game_over:
            show_game_over()
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game()
