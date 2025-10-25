# ShootingGame

A simple 2D shooting game built with Python and Pygame.

## Features

- Player-controlled spaceship with retro visual style
- 8-directional WASD movement and arrow key shooting
- **Three enemy types** with distinct behaviors:
  - **Circle Enemy**: Slow, basic enemy
  - **Triangle Enemy**: Fast and aggressive
  - **Square Tank**: Large, high HP, shoots high-damage bullets
- Enemy AI that tracks and shoots at player
- **Hit effects** - Enemies flash white when damaged for clear visual feedback
- **7-stage difficulty system** with progressive challenge
- **Energy bar power-up system** - collect energy by defeating enemies
- **Triple-shot power-up** with 3x fire rate and 3x score
- Health pack drops for HP recovery
- **Invincibility frames** after taking damage (0.5s with visual flash)
- Collision detection with bullet damage system
- Score tracking with floating score popups
- 3-heart health system
- Game time display
- Dynamic starfield background
- Game states (Menu, Playing, Game Over)
- **Background music and sound effects support**
- **Fully configurable** via JSON config file

## Requirements

- Python 3.7 or higher
- Pygame 2.5.0 or higher

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python game.py
```

2. **重要提示**: 如果使用中文输入法遇到按键无响应，请切换到**英文输入法**再玩游戏。

3. Controls:
   - **WASD**: Move the player (8 directions with diagonals)
   - **Arrow Keys**: Shoot in 8 directions (including diagonal)
   - **SPACE** (during game): Activate power-up when energy bar is full
   - **SPACE** (in menu): Start game
   - **ESC**: Return to menu / Quit

4. Objective:
   - Destroy enemies by shooting them
   - Collect energy by defeating enemies
   - Activate power-up (SPACE) when energy bar is full for:
     * Triple-shot attack
     * 3x fire rate
     * 3x score multiplier
     * 5x health pack drop rate
   - Collect green health packs to restore HP
   - Survive through 7 difficulty stages
   - Avoid enemy bullets (especially orange high-damage bullets from Square Tanks!)
   - You have 3 lives (hearts)
   - Survive as long as possible and get the highest score!

## Game Mechanics

### Player
- Cyan spaceship with retro style
- WASD movement in all directions
- Arrow key shooting in 8 directions
- 3 hearts (HP)
- **0.5 second invincibility** after taking damage (flashing effect)
- Can activate power-up when energy bar is full

### Enemies

Three types with unique characteristics:

1. **Circle Enemy** (Basic)
   - HP: 30
   - Speed: Slow (1.0)
   - Bullets: Normal damage (1 HP)
   - Score: 10 points
   - Energy: 2.5%
   - **Hit Effect**: 6-frame white flash

2. **Triangle Enemy** (Fast)
   - HP: 20
   - Speed: Fast (3.0)
   - Bullets: Normal damage, high fire rate
   - Score: 20 points
   - Energy: 5%
   - **Hit Effect**: 6-frame white flash

3. **Square Tank** (Boss-like)
   - HP: 100
   - Speed: Slow (1.0)
   - Size: Large (80x80)
   - Bullets: **HIGH DAMAGE (2 HP)** - Larger, orange-yellow with bright glow
   - Score: 50 points
   - Energy: 10%
   - High health pack drop rate
   - **Hit Effect**: 8-frame white flash (longer due to size)

### Power-Up System
- Fill energy bar by defeating enemies
- Press **SPACE** to activate when full
- Duration: 10 seconds
- Effects:
  - Triple-shot attack (3 bullets)
  - 3x fire rate
  - 3x score (gold text)
  - 5x health pack drop rate

### Difficulty System
- **7 progressive stages** (Stage 1 → Stage 7: HELL)
- Each stage lasts 20 seconds
- Increasing spawn rates
- More dangerous enemies in later stages
- Stage 1: No Square Tanks (80% Circle, 20% Triangle)
- Stage 7: 40% Square Tanks, 40% Triangle, 20% Circle
- Visual warning when difficulty increases

### Health Packs
- Green cross pickups
- Restore 1 HP
- Last 10 seconds before disappearing
- Drop from defeated enemies
- Drop rate increases during power-up mode

## Adding Audio

The game supports background music and sound effects! See [AUDIO_GUIDE.md](AUDIO_GUIDE.md) for detailed instructions on how to add audio files.

**Quick start:**
1. Create `assets/sounds/` folder (already created)
2. Add these files:
   - `background_music.mp3` - Background music
   - `shoot.wav` - Player shoot sound
   - `enemy_shoot.wav` - Enemy shoot sound
   - `hit.wav` - Hit enemy sound
   - `game_over.wav` - Game over sound
   - `menu_select.wav` - Menu selection sound
   - `powerup.wav` - Power-up activation sound
   - `health_pickup.wav` - Health pack pickup sound
   - `warning.wav` - Difficulty increase warning

**Note:** Game runs fine without audio files!

## Configuration

All game parameters can be customized via `config.json`. See documentation:
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Complete configuration reference
- [DIFFICULTY_STAGES.md](DIFFICULTY_STAGES.md) - Detailed difficulty system guide

**Quick configuration examples:**

### Adjust difficulty stages
Edit `config.json` → `difficulty.stages` array:
```json
{
    "level": 0,
    "spawn_delay": 90,        // Spawn interval (frames)
    "circle_weight": 0.8,     // Circle enemy spawn rate
    "triangle_weight": 0.2,   // Triangle enemy spawn rate
    "square_weight": 0.0      // Square enemy spawn rate
}
```

### Balance enemy types
Edit individual enemy configurations in `config.json`:
```json
"enemy_square": {
    "health": 100,
    "bullet_damage": 2,    // Change to 3 for even harder bullets
    "spawn_weight": 0.15
}
```

## Project Structure

```
shooting_game/
├── game.py                  # Main game loop
├── entities.py              # Player, Enemy, and Bullet classes
├── game_manager.py          # Game state management and logic
├── audio_manager.py         # Audio system for music and sound effects
├── config_loader.py         # Configuration file loader (singleton)
├── config.json              # Game configuration (difficulty, enemies, etc.)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── AUDIO_GUIDE.md           # Guide for adding audio files
├── CONFIG_GUIDE.md          # Complete configuration reference
├── DIFFICULTY_STAGES.md     # Difficulty system documentation
├── IME_COMPATIBILITY.md     # Chinese IME compatibility notes
├── test_bullet_visual.py    # Visual test for bullet effects
├── test_hit_effect.py       # Test enemy hit effects
├── test_game.py             # Basic game test
├── test_spawn.py            # Enemy spawn probability test
└── assets/
    └── sounds/              # Place audio files here
```

## Testing

The project includes several test scripts:

- `test_game.py` - Basic game functionality test
- `test_spawn.py` - Verify enemy spawn distribution
- `test_bullet_visual.py` - Compare bullet visual effects
- `test_hit_effect.py` - See enemy hit flash effects (auto-triggers every 2s, or press SPACE)

Run tests:
```bash
python test_bullet_visual.py  # See high-damage bullet effects
python test_hit_effect.py     # See enemy hit flash effects
python test_spawn.py           # Verify spawn rates
```

## License

This project is open source and available for educational purposes.
