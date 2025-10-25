"""
测试高伤害子弹视觉效果
显示普通子弹和高伤害子弹的对比
"""

import pygame
from entities import Bullet

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("子弹视觉效果对比")
clock = pygame.time.Clock()

# 创建不同的子弹
bullets = [
    # 玩家子弹（普通）
    {"bullet": Bullet(150, 200, 0, 0, is_enemy=False, damage=1), "label": "玩家子弹 (伤害1)"},
    # 敌人普通子弹
    {"bullet": Bullet(300, 200, 0, 0, is_enemy=True, damage=1), "label": "敌人普通子弹 (伤害1)"},
    # 方块敌人高伤害子弹
    {"bullet": Bullet(450, 200, 0, 0, is_enemy=True, damage=2), "label": "方块高伤害子弹 (伤害2)"},
]

# 字体
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 填充背景
    screen.fill((20, 20, 40))
    
    # 标题
    title = title_font.render("子弹视觉效果对比", True, (255, 255, 255))
    screen.blit(title, (150, 30))
    
    # 绘制子弹和标签
    for bullet_info in bullets:
        bullet = bullet_info["bullet"]
        label = bullet_info["label"]
        
        # 绘制子弹
        screen.blit(bullet.image, bullet.rect)
        
        # 绘制标签
        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(bullet.rect.centerx, bullet.rect.centery + 60))
        screen.blit(text, text_rect)
        
        # 绘制尺寸信息
        size_text = font.render(f"尺寸: {bullet.image.get_width()}x{bullet.image.get_height()}", 
                               True, (150, 150, 150))
        size_rect = size_text.get_rect(center=(bullet.rect.centerx, bullet.rect.centery + 85))
        screen.blit(size_text, size_rect)
    
    # 说明文字
    info_font = pygame.font.Font(None, 20)
    info_texts = [
        "方块敌人的子弹更大、更亮、更显眼",
        "橙黄色多层光晕，白热核心",
        "伤害是普通子弹的2倍",
        "按 ESC 或关闭窗口退出"
    ]
    
    y_offset = 280
    for text in info_texts:
        rendered = info_font.render(text, True, (200, 200, 200))
        screen.blit(rendered, (50, y_offset))
        y_offset += 25
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("测试完成！")
