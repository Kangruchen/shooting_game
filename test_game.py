import pygame
import sys
from game_manager import GameManager
from config_loader import config

# Initialize pygame
pygame.init()

# Get screen dimensions from config
screen_width = config.get('game', 'screen_width')
screen_height = config.get('game', 'screen_height')

# Create screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("ShootingGame - Enemy Test")

# Create game manager
game_manager = GameManager(screen, screen_width, screen_height)

# Start game
game_manager.state = game_manager.PLAYING
game_manager.reset_game()

# Force spawn 3 enemies immediately
print("手动生成3个敌人...")
for i in range(3):
    game_manager.spawn_enemy()
    
print(f"敌人数量: {len(game_manager.enemies)}")
for i, enemy in enumerate(game_manager.enemies):
    print(f"  敌人 {i+1}: 类型={enemy.enemy_type if hasattr(enemy, 'enemy_type') else '未知'}, 位置=({enemy.rect.x}, {enemy.rect.y}), 大小={enemy.rect.width}x{enemy.rect.height}")

# Simple game loop to show enemies
clock = pygame.time.Clock()
running = True
frame_count = 0

while running and frame_count < 300:  # Run for 5 seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    game_manager.update()
    
    # Draw
    screen.fill((20, 20, 40))
    game_manager.all_sprites.draw(screen)
    
    # Draw debug info
    font = pygame.font.Font(None, 24)
    text = font.render(f"Enemies: {len(game_manager.enemies)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)
    frame_count += 1

print(f"\n最终敌人数量: {len(game_manager.enemies)}")
pygame.quit()
