import pygame
import sys
from entities import SquareEnemy, Player
from config_loader import config

# Initialize pygame
pygame.init()

# Get screen dimensions from config
screen_width = 800
screen_height = 600

# Create screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Square Enemy Test")

# Create a player for reference
player = Player(screen_width // 2, screen_height // 2, screen_width, screen_height)

# Create a square enemy at the top
square = SquareEnemy(screen_width // 2, -50, screen_width, screen_height)

print(f"方块敌人信息:")
print(f"  位置: ({square.rect.x}, {square.rect.y})")
print(f"  中心: ({square.rect.centerx}, {square.rect.centery})")
print(f"  大小: {square.rect.width}x{square.rect.height}")
print(f"  速度: {square.speed}")
print(f"  血量: {square.health}")
print(f"  类型: {square.enemy_type}")

# Create sprite groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(square)

# Simple game loop
clock = pygame.time.Clock()
running = True
frame = 0

while running and frame < 600:  # Run for 10 seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update square enemy
    square.update((player.rect.centerx, player.rect.centery))
    
    # Draw
    screen.fill((20, 20, 40))
    all_sprites.draw(screen)
    
    # Draw debug info
    font = pygame.font.Font(None, 24)
    info_text = [
        f"Frame: {frame}",
        f"Square Pos: ({square.rect.x}, {square.rect.y})",
        f"Square Center: ({square.rect.centerx}, {square.rect.centery})",
        f"On Screen: {square.rect.y < screen_height and square.rect.bottom > 0}"
    ]
    
    for i, text in enumerate(info_text):
        rendered = font.render(text, True, (255, 255, 255))
        screen.blit(rendered, (10, 10 + i * 25))
    
    pygame.display.flip()
    clock.tick(60)
    frame += 1
    
    if frame % 60 == 0:
        print(f"  秒 {frame//60}: 位置=({square.rect.x}, {square.rect.y})")

print(f"\n最终位置: ({square.rect.x}, {square.rect.y})")
pygame.quit()
