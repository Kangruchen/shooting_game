# ShootingGame

A simple 2D shooting game built with Python and Pygame.

## Features

- Player-controlled spaceship
- 8-directional movement and shooting
- Enemy spawning from all screen edges
- Enemy AI that tracks and shoots at player
- Collision detection
- Score tracking
- 3-heart health system
- Game time display
- Game states (Menu, Playing, Game Over)
- **Background music and sound effects support**

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
   - **WASD**: Move the player
   - **Arrow Keys**: Shoot in 8 directions (including diagonal)
   - **SPACE** (in menu): Start game

4. Objective:
   - Destroy enemies by shooting them
   - Avoid enemy bullets and collisions
   - You have 3 lives (hearts)
   - Survive as long as possible and get the highest score!

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

**Note:** Game runs fine without audio files!

## Game Mechanics

- **Player**: Green rectangle that can move in all directions (WASD)
- **Shooting**: Use arrow keys to shoot in 8 directions
- **Enemies**: Red rectangles that spawn from screen edges and chase the player
- **Enemy Bullets**: Enemies shoot red bullets toward the player
- **Player Bullets**: Yellow projectiles fired by the player
- **Scoring**: +10 points for each enemy destroyed
- **Health**: Player has 3 hearts, loses 1 per hit
- **Game Time**: Displayed in MM:SS format
- **Game Over**: When player loses all hearts

## Project Structure

```
shooting_game/
├── game.py              # Main game loop
├── entities.py          # Player, Enemy, and Bullet classes
├── game_manager.py      # Game state management and logic
├── audio_manager.py     # Audio system for music and sound effects
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── AUDIO_GUIDE.md      # Guide for adding audio files
└── assets/
    └── sounds/         # Place audio files here
```

## Future Enhancements

- Add sound effects and background music
- Implement power-ups
- Add different enemy types
- Include boss battles
- Add particle effects
- Implement difficulty levels

## License

This project is open source and available for educational purposes.
