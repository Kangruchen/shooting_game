# 游戏配置指南 (Game Configuration Guide)

## 配置文件说明

游戏的所有参数都存储在 `config.json` 文件中，可以通过修改此文件来调整游戏难度和体验。

## 配置项详解

### 玩家配置 (`player`)

```json
"player": {
    "max_health": 3,                      // 最大血量
    "speed": 5,                           // 移动速度
    "shoot_cooldown": 10,                 // 射击冷却时间(帧)
    "bullet_speed": 7,                    // 子弹速度
    "invincibility_duration_frames": 30   // 受伤后无敌时间(帧) - 30帧=0.5秒
}
```

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
    "points": 10,                      // 击杀得分
    "spawn_weight": 0.75,              // 刷新权重(0-1)
    "health_pack_drop_chance": 0.05    // 血包掉落概率(5%)
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
    "points": 20,                      // 击杀得分
    "spawn_weight": 0.25,              // 刷新权重(0-1)
    "health_pack_drop_chance": 0.1     // 血包掉落概率(10%)
}
```

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
    "duration_seconds": 5,         // 强化持续时间(秒)
    "fire_rate_multiplier": 3,     // 射速倍率
    "triple_shot": true,           // 是否三连发
    "initial_energy": 0.0          // 初始能量(0.0-1.0，用于测试)
}
```

**注意**: 
- `initial_energy` 设置为 1.0 可以直接测试强化状态
- 正常游戏请设置为 0.0
- 圆形敌人充能 2.5%，三角敌人充能 5%

### 难度配置 (`difficulty`)

```json
"difficulty": {
    "level_up_interval_seconds": 20,   // 难度提升间隔(秒)
    "initial_spawn_delay": 90,         // 初始刷新延迟(帧)
    "min_spawn_delay": 30,             // 最小刷新延迟(帧)
    "spawn_delay_decrease": 10         // 每次难度提升减少的延迟(帧)
}
```

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
- 增加 `difficulty.level_up_interval_seconds`

### 提高难度
- 减少 `player.max_health`
- 增加敌人速度和射击频率
- 减少 `health_pack_drop_chance`
- 减少 `difficulty.level_up_interval_seconds`

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
