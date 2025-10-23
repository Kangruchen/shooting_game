# 音频文件说明

## 如何添加音频文件

游戏现在已经集成了音频系统，但需要您提供实际的音频文件。

### 📁 文件夹结构

请创建以下文件夹结构：

```
shooting_game/
└── assets/
    └── sounds/
        ├── background_music.mp3    # 背景音乐
        ├── shoot.wav               # 玩家射击音效
        ├── enemy_shoot.wav         # 敌人射击音效
        ├── hit.wav                 # 击中敌人音效
        ├── game_over.wav           # 游戏结束音效
        └── menu_select.wav         # 菜单选择音效
```

### 🎵 如何创建/获取音频文件

#### 选项 1: 使用免费音效网站
- **Freesound** (https://freesound.org/) - 需要注册，大量免费音效
- **OpenGameArt** (https://opengameart.org/) - 游戏专用音效和音乐
- **Zapsplat** (https://www.zapsplat.com/) - 免费音效库
- **Incompetech** (https://incompetech.com/) - 免费背景音乐（Kevin MacLeod）

#### 选项 2: 使用音效生成工具
- **Bfxr** (https://www.bfxr.net/) - 在线生成复古游戏音效
- **ChipTone** (https://sfbgames.itch.io/chiptone) - 8位音效生成器
- **Audacity** (https://www.audacityteam.org/) - 免费音频编辑软件

### 🎮 推荐的音效类型

1. **background_music.mp3** 
   - 类型：循环背景音乐
   - 风格：电子、合成器、复古8位
   - 时长：1-3分钟（可循环）
   - 关键词搜索："space shooter music", "arcade game music"

2. **shoot.wav**
   - 类型：短促的射击音
   - 时长：0.1-0.3秒
   - 关键词："laser shot", "pew", "shoot"

3. **enemy_shoot.wav**
   - 类型：稍低沉的射击音
   - 时长：0.1-0.3秒
   - 关键词："enemy laser", "alien shoot"

4. **hit.wav**
   - 类型：撞击或爆炸音
   - 时长：0.2-0.5秒
   - 关键词："explosion", "impact", "hit"

5. **game_over.wav**
   - 类型：失败/死亡音效
   - 时长：1-2秒
   - 关键词："game over", "death", "fail"

6. **menu_select.wav**
   - 类型：按钮点击音
   - 时长：0.1-0.2秒
   - 关键词："button click", "menu select", "beep"

### 🔧 快速开始（使用占位符音频）

如果您想快速测试音频系统，可以使用 Audacity 或在线工具创建简单的音调：

```python
# 或者暂时禁用音频，游戏仍然可以正常运行
# 音频管理器已经内置了错误处理，如果找不到文件会自动跳过
```

### 📝 文件格式建议

- **背景音乐**：MP3 或 OGG 格式（体积小）
- **音效**：WAV 格式（低延迟，适合游戏）
- **采样率**：22050 Hz 或 44100 Hz
- **比特率**：音乐 128-192 kbps，音效 16-bit

### ⚙️ 自定义音量

在 `game_manager.py` 中，您可以调整音量：

```python
# 在 GameManager.__init__ 中
self.audio.set_music_volume(0.5)  # 0.0 到 1.0
self.audio.set_sfx_volume(0.7)    # 0.0 到 1.0
```

### 🎯 测试音频

1. 创建 `assets/sounds/` 文件夹
2. 添加任意音频文件（按上述命名）
3. 运行游戏
4. 如果文件不存在，游戏会显示警告但继续运行

**注意**：即使没有音频文件，游戏也能正常运行！音频系统会自动处理缺失的文件。
