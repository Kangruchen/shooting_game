# 游戏配置指南 (Game Configuration Guide)

## 配置文件说明

游戏的所有参数都存储在 `config.json` 文件中，可以通过修改此文件来调整游戏难度和体验。

## 配置项详解

### 玩家配置 (`player`)

```json
"player": {
    "max_health": 3,                      // 初始/默认最大血量
    "max_health_limit": 5,                // 血量上限（捡血包后的最大值）
    "speed": 5,                           // 移动速度
    "shoot_cooldown": 10,                 // 射击冷却时间(帧)
    "bullet_speed": 7,                    // 子弹速度
    "invincibility_duration_frames": 30   // 受伤后无敌时间(帧) - 30帧=0.5秒
}
```

**血量系统说明**:
- `max_health`: 游戏开始时的血量（默认3）
- `max_health_limit`: 血量绝对上限（默认5）
- 捡血包只会恢复到 `max_health_limit`，不会超过
- 可以通过调整这两个值来控制游戏难度

**无敌机制说明**:
- 玩家受伤后会进入无敌状态，期间不会再次受伤
- 无敌期间玩家会闪烁显示（视觉反馈）
- 默认30帧 = 0.5秒（60 FPS）
- 可以调整以改变游戏难度

### 圆形敌人配置 (`enemy_circle`)

```json
"enemy_circle": {
    "health": 30,                      // 血量
    "speed": 1,                        // 移动速度
    "shoot_cooldown_min": 120,         // 最小射击冷却(帧)
    "shoot_cooldown_max": 240,         // 最大射击冷却(帧)
    "bullet_speed": 3,                 // 子弹速度
    "bullet_damage": 1,                // 子弹伤害
    "collision_damage": 1,             // 碰撞伤害
    "points": 10,                      // 击杀得分
    "spawn_weight": 0.6,               // 刷新权重(0-1)
    "health_pack_drop_chance": 0.05,   // 血包掉落概率(5%)
    "energy_charge": 0.025             // 击杀充能(2.5%)
}
```

### 三角敌人配置 (`enemy_triangle`)

```json
"enemy_triangle": {
    "health": 20,                      // 血量
    "speed": 3,                        // 移动速度(更快)
    "shoot_cooldown_min": 30,          // 最小射击冷却(帧)
    "shoot_cooldown_max": 60,          // 最大射击冷却(帧)
    "bullet_speed": 4,                 // 子弹速度
    "bullet_damage": 1,                // 子弹伤害
    "collision_damage": 1,             // 碰撞伤害
    "points": 20,                      // 击杀得分
    "spawn_weight": 0.25,              // 刷新权重(0-1)
    "health_pack_drop_chance": 0.1,    // 血包掉落概率(10%)
    "energy_charge": 0.05              // 击杀充能(5%)
}
```

### 方块敌人配置 (`enemy_square`)

```json
"enemy_square": {
    "health": 100,                     // 血量（大型坦克）
    "speed": 1.0,                      // 移动速度（慢）
    "shoot_cooldown_min": 180,         // 最小射击冷却(帧)
    "shoot_cooldown_max": 300,         // 最大射击冷却(帧)
    "bullet_speed": 3,                 // 子弹速度
    "bullet_damage": 2,                // 子弹伤害（2滴血）
    "collision_damage": 2,             // 碰撞伤害（2滴血）
    "points": 50,                      // 击杀得分（高价值目标）
    "spawn_weight": 0.15,              // 刷新权重(0-1)
    "health_pack_drop_chance": 0.2,    // 血包掉落概率(20%)
    "energy_charge": 0.1               // 击杀充能(10%)
}
```

**敌人类型对比**:

| 类型 | 血量 | 速度 | 射速 | 子弹伤害 | 碰撞伤害 | 得分 | 刷新率 | 特点 |
|-----|------|------|------|---------|---------|------|--------|------|
| **圆形** | 30 | 1.0 | 慢 | 1 | 1 | 10 | 60% | 基础敌人 |
| **三角** | 20 | 3.0 | 快 | 1 | 1 | 20 | 25% | 快速袭击 |
| **方块** | 100 | 1.0 | 很慢 | **2** | **2** | 50 | 15% | 大型坦克 |

**注意**: Stage 7 (HELL) 时所有敌人的伤害都会提升至2（见难度阶段配置）

### 血包配置 (`health_pack`)

```json
"health_pack": {
    "heal_amount": 1,          // 恢复血量
    "drift_speed": 0.5,        // 下落速度
    "lifetime_seconds": 10,    // 存在时间(秒)
    "pulse_interval": 30       // 脉冲动画间隔(帧)
}
```

### 强化系统配置 (`powerup`)

```json
"powerup": {
    "duration_seconds": 10,                // 强化持续时间(秒)
    "fire_rate_multiplier": 3,             // 射速倍率
    "triple_shot": true,                   // 是否三连发
    "health_drop_rate_multiplier": 3,      // 血包掉率倍率
    "score_multiplier": 3,                 // 分数倍率
    "initial_energy": 0.0                  // 初始能量(0.0-1.0，用于测试)
}
```

**注意**: 
- `initial_energy` 设置为 1.0 可以直接测试强化状态
- 正常游戏请设置为 0.0
- `health_drop_rate_multiplier`: 强化时血包掉落概率的倍数（从5倍改为3倍以增加难度）
- `score_multiplier`: 强化时击杀得分的倍数

**强化状态额外效果**:
- 射速提升为3倍（三连发）
- 血包掉落概率变为3倍（例如5%变为15%）
- 击杀得分变为3倍（金色大字带描边显示）
- 持续10秒

### 难度阶段配置 (`difficulty`)

**新版阶段系统** (v2.0):

```json
"difficulty": {
    "level_up_interval_seconds": 20,   // 每个阶段持续时间(秒)
    "max_level": 6,                    // 最高等级(0-6共7阶段)
    "stages": [...]                    // 阶段配置数组
}
```

游戏现在使用**独立的7阶段系统**，每个阶段有自己的刷新频率和敌人权重。

#### 阶段配置示例

```json
{
    "level": 3,                             // 阶段等级(0-6)
    "name": "Stage 4 - Hard",               // 阶段名称
    "spawn_delay": 50,                      // 敌人刷新间隔(帧)
    "circle_weight": 0.5,                   // 圆形敌人权重(0-1)
    "triangle_weight": 0.3,                 // 三角敌人权重(0-1)
    "square_weight": 0.2                    // 方块敌人权重(0-1)
}

// Stage 7 特殊配置（地狱难度）
{
    "level": 6,
    "name": "Stage 7 - HELL",
    "spawn_delay": 30,
    "circle_weight": 0.4,
    "triangle_weight": 0.3,
    "square_weight": 0.3,
    "all_enemies_damage": 2,                // 所有敌人子弹伤害改为2
    "all_enemies_collision_damage": 2       // 所有敌人碰撞伤害改为2
}
```

**重要**: 
- 三个权重之和必须等于 1.0
- `spawn_delay` 越小，刷新越快（60帧=1秒）
- Stage 7 可以设置 `all_enemies_damage` 和 `all_enemies_collision_damage` 来覆盖所有敌人的伤害
- 详细的阶段配置说明请查看 `DIFFICULTY_STAGES.md`

#### 7个难度阶段概览

| 阶段 | 时间 | 刷新间隔 | 圆形 | 三角 | 方块 | 特点 |
|-----|------|---------|------|------|------|------|
| Stage 1 | 0-20s | 90帧 | 100% | 0% | 0% | 入门，仅圆形 |
| Stage 2 | 20-40s | 75帧 | 85% | 15% | 0% | 三角登场 |
| Stage 3 | 40-60s | 60帧 | 70% | 30% | 0% | 三角增多 |
| Stage 4 | 60-80s | 50帧 | 70% | 20% | 10% | 方块登场 |
| Stage 5 | 80-100s | 40帧 | 60% | 20% | 20% | 方块增多 |
| Stage 6 | 100-120s | 35帧 | 50% | 30% | 20% | 极限 |
| Stage 7 | 120s+ | 30帧 | 40% | 30% | 30% | **地狱（所有敌人2伤）** |

### 游戏配置 (`game`)

```json
"game": {
    "screen_width": 800,           // 屏幕宽度
    "screen_height": 600,          // 屏幕高度
    "fps": 60,                     // 帧率
    "background_color": [20, 20, 40],  // 背景颜色[R,G,B]
    "star_count": 100              // 星星数量
}
```

## 调试建议

### 降低难度
- 增加 `player.max_health` (例如改为5)
- 减少 `enemy_circle.speed` 和 `enemy_triangle.speed`
- 增加 `health_pack_drop_chance`
- 增加 `difficulty.level_up_interval_seconds` (延长每阶段时间)
- 在 `stages` 中增加 `spawn_delay` 值（降低刷新速度）
- 减少各阶段的 `square_weight`（减少高伤害敌人）

### 提高难度
- 减少 `player.max_health`
- 增加敌人速度和射击频率
- 减少 `health_pack_drop_chance`
- 减少 `difficulty.level_up_interval_seconds` (更快进入高难度)
- 在 `stages` 中减少 `spawn_delay` 值（提高刷新速度）
- 增加各阶段的 `square_weight`（更多高伤害敌人）
- 增加 `enemy_square.bullet_damage` (例如改为3)

### 测试特定功能
- 血包掉落: 将 `health_pack_drop_chance` 改为 1.0 (100%)
- 敌人平衡: 调整 `spawn_weight` 比例
- 难度曲线: 修改 `spawn_delay_decrease` 和间隔
- **强化测试**: 将 `powerup.initial_energy` 设置为 1.0 (满能量开局)

## 注意事项

1. **帧数计算**: 射击冷却和刷新延迟以帧为单位，60帧 = 1秒
2. **权重总和**: `enemy_circle.spawn_weight` + `enemy_triangle.spawn_weight` 应该等于 1.0
3. **速度平衡**: 确保玩家速度 > 敌人平均速度，保持可玩性
4. **配置加载**: 修改配置后需要重新启动游戏

## 示例配置

### 简单模式
```json
"player": { "max_health": 5, "speed": 6 }
"difficulty": { "level_up_interval_seconds": 30 }
```

### 困难模式
```json
"player": { "max_health": 1, "speed": 4 }
"enemy_triangle": { "spawn_weight": 0.5 }
"difficulty": { "level_up_interval_seconds": 10 }
```

### 测试模式
```json
"health_pack_drop_chance": 1.0
"player": { "max_health": 999 }
"powerup": { "initial_energy": 1.0 }
```

**快速测试强化系统**:
- 设置 `"initial_energy": 1.0` - 游戏开始时能量已满
- 设置 `"initial_energy": 0.5` - 游戏开始时能量50%
- 设置 `"energy_charge": 0.5` - 每个敌人充能50%（快速测试）
