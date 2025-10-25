"""
测试敌人受击特效
展示三种敌人被击中时的闪白效果
"""

import pygame
import sys
sys.path.insert(0, '.')

from entities import Enemy, TriangleEnemy, SquareEnemy

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("敌人受击特效测试")
clock = pygame.time.Clock()

# 创建三种敌人
circle_enemy = Enemy(150, 200, 800, 400)
triangle_enemy = TriangleEnemy(400, 200, 800, 400)
square_enemy = SquareEnemy(650, 200, 800, 400)

enemies = [
    {"enemy": circle_enemy, "label": "圆形敌人", "x": 150},
    {"enemy": triangle_enemy, "label": "三角敌人", "x": 400},
    {"enemy": square_enemy, "label": "方块坦克", "x": 650}
]

# 字体
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)
info_font = pygame.font.Font(None, 20)

# 提示计时器
hit_timer = 0
auto_hit_timer = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 手动触发所有敌人的受击特效
                for enemy_info in enemies:
                    enemy = enemy_info["enemy"]
                    enemy.take_damage(1)
                    # 恢复血量以便继续测试
                    enemy.health += 1
                hit_timer = 30  # 显示提示0.5秒
    
    # 自动触发特效（每2秒）
    auto_hit_timer += 1
    if auto_hit_timer >= 120:
        auto_hit_timer = 0
        for enemy_info in enemies:
            enemy = enemy_info["enemy"]
            enemy.take_damage(1)
            enemy.health += 1
        hit_timer = 30
    
    # 更新敌人（处理闪光效果）
    player_pos = (400, 200)  # 假的玩家位置
    for enemy_info in enemies:
        enemy = enemy_info["enemy"]
        # 不调用update移动，只更新闪光
        if enemy.hit_flash > 0:
            enemy.hit_flash -= 1
            if hasattr(enemy, 'draw_circle_enemy'):
                enemy.draw_circle_enemy()
            elif hasattr(enemy, 'draw_triangle_enemy'):
                enemy.draw_triangle_enemy()
            elif hasattr(enemy, 'draw_square_enemy'):
                enemy.draw_square_enemy()
    
    # 绘制
    screen.fill((20, 20, 40))
    
    # 标题
    title = title_font.render("敌人受击特效演示", True, (255, 255, 255))
    screen.blit(title, (250, 30))
    
    # 绘制敌人和标签
    for enemy_info in enemies:
        enemy = enemy_info["enemy"]
        label = enemy_info["label"]
        x = enemy_info["x"]
        
        # 绘制敌人
        screen.blit(enemy.image, enemy.rect)
        
        # 绘制标签
        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, 300))
        screen.blit(text, text_rect)
        
        # 绘制血量
        hp_text = info_font.render(f"HP: {enemy.health}", True, (0, 255, 0))
        hp_rect = hp_text.get_rect(center=(x, 330))
        screen.blit(hp_text, hp_rect)
    
    # 提示信息
    if hit_timer > 0:
        hit_timer -= 1
        hit_text = font.render("★ 受击特效触发！", True, (255, 255, 0))
        hit_rect = hit_text.get_rect(center=(400, 100))
        screen.blit(hit_text, hit_rect)
    
    # 说明文字
    instructions = [
        "按 SPACE 手动触发受击特效",
        "或等待2秒自动触发",
        "敌人被击中时会闪白色",
        "圆形/三角: 6帧闪光, 方块: 8帧闪光"
    ]
    
    y_offset = 360
    for text in instructions:
        rendered = info_font.render(text, True, (200, 200, 200))
        screen.blit(rendered, (220, y_offset))
        y_offset += 22
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("测试完成！")
