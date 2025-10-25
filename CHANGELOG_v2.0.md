# 更新日志 - v2.0

## 新增功能

### 1. 高伤害子弹视觉增强 ✨

方块敌人的子弹现在更加显眼，突出其高伤害特性：

**视觉特效**:
- 尺寸增大：从12x12像素增至18x18像素（50%更大）
- 多层光晕：橙色、黄色渐变的多层光晕效果
- 明亮核心：白热的中心，极易识别
- 颜色方案：橙黄色系，与普通红色子弹明显区别

**技术实现**:
- Bullet类构造函数新增`damage`参数
- 根据damage值自动选择渲染样式
- draw_bullet方法支持三种子弹类型：
  1. 玩家子弹（青色）
  2. 敌人普通子弹（红色，伤害1）
  3. 敌人高伤害子弹（橙黄色，伤害2+）

**测试**:
运行 `python test_bullet_visual.py` 查看三种子弹的视觉对比。

---

### 2. 七阶段难度系统 🎮

完全重构的难度系统，提供更细致的游戏体验：

**系统特点**:
- **7个独立阶段**，每个阶段20秒
- 每个阶段有**独立的刷新频率**
- 每个阶段有**独立的敌人权重**
- 阶段切换时显示阶段名称（如"Stage 4 - Hard"）

**阶段概览**:

| 阶段 | 时长 | 刷新间隔 | 圆形 | 三角 | 方块 | 特点 |
|-----|------|---------|------|------|------|------|
| Stage 1 - Easy | 0-20s | 90帧 | 80% | 20% | 0% | 入门，无方块 |
| Stage 2 - Normal | 20-40s | 75帧 | 70% | 25% | 5% | 方块登场 |
| Stage 3 - Getting Hard | 40-60s | 60帧 | 60% | 30% | 10% | 加速 |
| Stage 4 - Hard | 60-80s | 50帧 | 50% | 30% | 20% | 困难 |
| Stage 5 - Very Hard | 80-100s | 40帧 | 40% | 35% | 25% | 很难 |
| Stage 6 - Extreme | 100-120s | 35帧 | 30% | 40% | 30% | 极限 |
| Stage 7 - HELL | 120s+ | 30帧 | 20% | 40% | 40% | 地狱 |

**配置结构**:

```json
"difficulty": {
    "level_up_interval_seconds": 20,
    "max_level": 6,
    "stages": [
        {
            "level": 0,
            "name": "Stage 1 - Easy",
            "spawn_delay": 90,
            "circle_weight": 0.8,
            "triangle_weight": 0.2,
            "square_weight": 0.0
        },
        // ... 更多阶段
    ]
}
```

**代码变更**:
- `game_manager.py`：
  - 新增`max_difficulty_level`属性
  - 重构`update()`中的难度升级逻辑
  - 从stages数组动态读取配置
  - 更新难度警告显示阶段名称
- `spawn_enemy()`：从当前阶段读取权重
- 移除旧的线性难度系统（`spawn_delay_decrease`等）

---

## 配置改进

### config.json 更新

**新增配置项**:
```json
"difficulty": {
    "max_level": 6,
    "stages": [...]  // 7个阶段的详细配置
}
```

**移除配置项**:
```json
// 以下配置已被stages系统取代
"initial_spawn_delay": 90,
"min_spawn_delay": 30,
"spawn_delay_decrease": 10
```

**敌人配置**:
- 移除 `spawn_weight` 从各敌人配置（现在由stages控制）
- 保留敌人基础属性（health, speed, bullet_damage等）

---

## 文档更新

### 新增文档

1. **DIFFICULTY_STAGES.md** 📘
   - 详细的阶段系统说明
   - 每个阶段的配置详解
   - 自定义配置教程
   - 游戏平衡建议
   - 技术实现说明

### 更新文档

1. **CONFIG_GUIDE.md** 📝
   - 更新难度配置部分
   - 添加7阶段系统说明
   - 更新调试建议（针对阶段系统）
   - 添加阶段配置概览表

2. **README.md** 📖
   - 更新Feature列表（三种敌人、7阶段系统）
   - 扩展游戏机制说明
   - 详细的敌人特性表
   - 添加高伤害子弹说明
   - 更新配置章节
   - 添加测试脚本说明

---

## 测试工具

### test_bullet_visual.py 🔍
新增可视化测试脚本，展示三种子弹的视觉效果对比：
- 玩家子弹（青色，12x12）
- 敌人普通子弹（红色，12x12，伤害1）
- 方块高伤害子弹（橙黄色，18x18，伤害2）

运行：
```bash
python test_bullet_visual.py
```

---

## 技术细节

### Bullet类重构

**构造函数**:
```python
def __init__(self, x, y, speed_x, speed_y, color=(255, 255, 0), 
             is_enemy=False, damage=1):
```
- 新增 `damage` 参数（默认1）
- 根据damage自动调整尺寸（damage>1时为18x18）

**draw_bullet方法**:
```python
def draw_bullet(self, color, is_enemy, damage=1):
```
- 新增 `damage` 参数
- 三种渲染路径：
  1. `damage > 1`: 大型高伤害子弹
  2. `is_enemy=True`: 普通敌人子弹
  3. `is_enemy=False`: 玩家子弹

### SquareEnemy更新

**射击方法**:
```python
bullet = Bullet(self.rect.centerx, self.rect.centery, dx, dy, 
              (255, 150, 0), is_enemy=True, damage=self.damage)
```
- 使用新的damage参数
- 自动继承self.damage（默认2）

### GameManager更新

**初始化**:
```python
stages = config.get('difficulty', 'stages')
self.base_spawn_delay = stages[0]['spawn_delay']
self.max_difficulty_level = config.get('difficulty', 'max_level')
```

**难度升级**:
```python
if self.difficulty_level < self.max_difficulty_level:
    self.difficulty_level += 1
    new_stage = stages[self.difficulty_level]
    self.enemy_spawn_delay = new_stage['spawn_delay']
```

**敌人生成**:
```python
current_stage = stages[min(self.difficulty_level, len(stages) - 1)]
circle_weight = current_stage['circle_weight']
triangle_weight = current_stage['triangle_weight']
square_weight = current_stage['square_weight']
```

---

## 游戏平衡调整

### 方块敌人子弹
- **更显眼**: 50%更大，更亮的颜色
- **更危险**: 2点伤害（玩家只有3血）
- **更可预测**: 明显的视觉提示，玩家有时间反应

### 难度曲线
- **渐进式**: 前40秒适应期，方块坦克出现率低
- **中期挑战**: 60-100秒，方块坦克成为常见威胁
- **极限测试**: 100秒后，40%方块坦克 + 40%三角敌人

### 阶段设计哲学
1. **Stage 1-2**: 学习游戏机制，熟悉敌人类型
2. **Stage 3-4**: 测试基础技能，需要合理使用强化
3. **Stage 5-6**: 高难度挑战，需要精确走位
4. **Stage 7**: 终极考验，只有最熟练的玩家能长期生存

---

## 向后兼容性

### 配置迁移
旧配置文件将无法直接使用，因为：
- 移除了 `initial_spawn_delay`, `min_spawn_delay`, `spawn_delay_decrease`
- 移除了各敌人的 `spawn_weight`

**迁移方案**:
1. 使用新的 `config.json` 模板
2. 或手动添加 `stages` 数组和 `max_level`

### 代码兼容性
- 所有旧的游戏逻辑保持不变
- Bullet类向后兼容（damage默认为1）
- 敌人类保持不变
- 玩家类保持不变

---

## 已知问题

无重大问题。

---

## 未来改进建议

1. **更多子弹类型**:
   - 穿透子弹（damage=1，可穿透多个敌人）
   - 爆炸子弹（AOE伤害）
   - 追踪子弹

2. **更多敌人类型**:
   - 飞行敌人（Z字形移动）
   - 分裂敌人（死亡后分裂成小敌人）
   - Boss敌人（特定阶段出现）

3. **难度自适应**:
   - 根据玩家表现动态调整难度
   - 死亡后降低难度

4. **视觉增强**:
   - 粒子效果（爆炸、火花）
   - 屏幕震动
   - 更多光效

5. **成就系统**:
   - 生存时间成就
   - 击杀数成就
   - 完美闪避成就

---

## 开发者备注

### 调试功能
在 `game_manager.py` 的 `update()` 方法中，曾添加调试输出（现已移除）：
```python
# 每3秒输出敌人统计
print(f"[DEBUG] 敌人统计: 圆形={circle_count}, 三角={triangle_count}, 方块={square_count}")

# 难度提升时输出阶段信息
print(f"[难度提升] {new_stage['name']} - 刷新间隔={new_stage['spawn_delay']}帧")
```

如需调试，可以取消注释这些行。

### 性能考虑
- 阶段系统对性能无影响（只是每20秒读取一次配置）
- 高伤害子弹略大，但不会显著影响性能
- 最多同时存在的子弹数量受spawn_delay限制

### 测试覆盖
- ✅ 子弹视觉效果：test_bullet_visual.py
- ✅ 敌人生成概率：test_spawn.py
- ✅ 基础游戏功能：test_game.py
- ⚠️ 待补充：阶段切换测试、高伤害子弹碰撞测试

---

## 致谢

感谢玩家反馈，本次更新主要基于以下建议：
- "方块敌人的子弹应该更显眼" ✅ 已实现
- "需要更细致的难度调整" ✅ 已实现

---

**版本**: v2.0  
**更新日期**: 2025-10-25  
**下一版本计划**: Boss敌人、粒子效果、成就系统
