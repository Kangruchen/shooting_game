# ShootingGame

A retro-style 2D space shooting game built with Python and Pygame, featuring advanced visual effects, dynamic difficulty system, and energy-based power-ups.

##  Core Features

- **Three Unique Enemy Types**: Circle (basic), Triangle (fast), and Square Tank (boss-like)
- **Energy-Based Power-Up System**: Collect energy from defeated enemies to activate triple-shot mode
- **7-Stage Progressive Difficulty**: From Easy to HELL, with increasing spawn rates and enemy variety
- **Advanced Visual Effects**: Particle explosions, screen shake, multi-layer nebula background, twinkling stars
- **Combat Enhancements**: Invincibility frames, hit feedback, health packs, low-health warning
- **Retro Aesthetics**: Classic arcade-style graphics with modern visual polish

##  Quick Start

### Requirements

- Python 3.7+
- Pygame 2.5.0+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/shooting_game.git
cd shooting_game

# Install dependencies
pip install -r requirements.txt

# Run the game
python game.py
```

##  How to Play

### Controls

| Key | Action |
|-----|--------|
| **WASD** | Move in 8 directions |
| **Arrow Keys** | Shoot in 8 directions |
| **SPACE** (in game) | Activate power-up when energy is full |
| **SPACE** (in menu) | Start game |
| **ESC** | Return to menu / Quit |

### Gameplay Guide

1. **Destroy Enemies**: Shoot enemies to earn points and energy
2. **Collect Energy**: Fill the energy bar by defeating enemies
3. **Activate Power-Up**: Press SPACE when energy bar is full for triple-shot, 3x fire rate, 3x score multiplier, 5x health pack drop rate, and auto-collect nearby health packs
4. **Collect Health Packs**: Green crosses restore 1 HP
5. **Watch for Warnings**: Red arrows indicate off-screen enemies
6. **Survive**: Progress through 7 difficulty stages and achieve high scores

### Survival Tips

-  **Avoid Orange Bullets**: Square Tank bullets deal 2 damage
-  **Low Health Alert**: Screen edges pulse red when at 1 HP
-  **Invincibility Frames**: 0.5s protection after taking damage (flashing effect)

##  Enemy Types

| Enemy | HP | Speed | Damage | Score | Special |
|-------|-----|-------|--------|-------|---------|
| **Circle**  | 30 | Slow | 1 | 10 pts | Basic enemy with steady fire |
| **Triangle**  | 20 | Fast | 1 | 20 pts | Aggressive with high fire rate |
| **Square Tank**  | 100 | Slow | **2** | 50 pts | Large, devastating orange bullets |

### Visual Feedback

- **Red particles**: Circle enemy explosions
- **Purple particles**: Triangle enemy explosions
- **Orange particles**: Square Tank explosions
- **White flash**: Enemy hit feedback

##  Difficulty Progression

The game features 7 progressive stages, each lasting 20 seconds:

1. **Stage 1 - Easy**: Only Circle enemies
2. **Stage 2 - Normal**: 85% Circles, 15% Triangles
3. **Stage 3 - Getting Hard**: 70% Circles, 30% Triangles
4. **Stage 4 - Hard**: First Square Tanks appear (10%)
5. **Stage 5 - Very Hard**: 20% Square Tanks, faster spawns
6. **Stage 6 - Extreme**: High enemy variety, rapid spawns
7. **Stage 7 - HELL**: All enemies deal 2 damage, maximum spawn rate

##  Configuration

All game parameters are customizable via `config.json`:

- Player stats (speed, health, fire rate)
- Enemy attributes (HP, damage, spawn weights)
- Difficulty progression (spawn delays, stage durations)
- Visual effects (particles, screen shake intensity)
- Power-up parameters (duration, multipliers)

**Example**: Adjust enemy difficulty

```json
"enemy_square": {
    "health": 100,
    "bullet_damage": 2,
    "spawn_weight": 0.15
}
```

##  Audio Setup (Optional)

The game supports background music and sound effects. The game runs perfectly without audio files.

### Adding Audio Files

1. Create folder: `assets/sounds/`
2. Add audio files with these names:

| File | Description | Format |
|------|-------------|--------|
| `background_music.mp3` | Looping background music | MP3 |
| `shoot.wav` | Player shoot sound | WAV |
| `enemy_shoot.wav` | Enemy shoot sound | WAV |
| `hit.wav` | Enemy hit/explosion sound | WAV |
| `game_over.wav` | Game over sound | WAV |
| `menu_select.wav` | Menu selection sound | WAV |
| `powerup.wav` | Power-up activation sound | WAV |
| `health_pickup.wav` | Health pack pickup sound | WAV |
| `warning.wav` | Difficulty increase warning | WAV |

###  Audio Credits

> **Music & Sound Effects Sources**
> - Background Music: Created by Suno AI 
> - Sound Effects: Free assets from pixabay.com

##  Project Structure

```
shooting_game/
 game.py              # Main game loop and entry point
 entities.py          # Player, Enemy, Bullet, Particle classes
 game_manager.py      # Game state management and rendering
 audio_manager.py     # Audio system (music and SFX)
 config_loader.py     # Configuration loader (singleton)
 config.json          # Game configuration file
 requirements.txt     # Python dependencies
 README.md            # This file
 assets/
     sounds/          # Audio files (optional)
```

##  Technical Details

### Key Systems

- **Visual Effects Pipeline**:
  1. Multi-layer nebula background (parallax scrolling)
  2. Twinkling starfield (150 animated stars)
  3. Game entities (sprites with depth sorting)
  4. Particle effects (physics-based explosions)
  5. UI overlays (health, energy, score, warnings)
  6. Low health vignette (edge-based gradient)

- **Combat System**:
  - Invincibility frames (0.5s after damage)
  - Hit feedback (white flash effects)
  - Screen shake on impacts
  - Color-coded particle explosions

- **Power-Up Mechanics**:
  - Energy collection from defeated enemies
  - Triple-shot with enhanced fire rate
  - Score multiplier (3x)
  - Auto-collect nearby health packs

##  Contributing

Contributions are welcome! Feel free to:
- Report bugs via GitHub Issues
- Suggest new features
- Submit pull requests
- Improve documentation

##  License

This project is open source and available for educational purposes.

##  Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic arcade space shooters
- Retro visual design with modern particle effects

---

**Enjoy the game and aim for the high score! **
