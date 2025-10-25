import random
from config_loader import config

circle_weight = config.get('enemy_circle', 'spawn_weight')
triangle_weight = config.get('enemy_triangle', 'spawn_weight')
square_weight = config.get('enemy_square', 'spawn_weight')

print(f"权重配置:")
print(f"  圆形: {circle_weight}")
print(f"  三角: {triangle_weight}")
print(f"  方块: {square_weight}")
print(f"  总和: {circle_weight + triangle_weight + square_weight}")
print()

counts = {'circle': 0, 'triangle': 0, 'square': 0}

for _ in range(1000):
    enemy_roll = random.random()
    
    if enemy_roll < circle_weight:
        counts['circle'] += 1
    elif enemy_roll < circle_weight + triangle_weight:
        counts['triangle'] += 1
    else:
        counts['square'] += 1

print(f"测试1000次生成:")
print(f"  圆形: {counts['circle']} ({counts['circle']/10:.1f}%)")
print(f"  三角: {counts['triangle']} ({counts['triangle']/10:.1f}%)")
print(f"  方块: {counts['square']} ({counts['square']/10:.1f}%)")
