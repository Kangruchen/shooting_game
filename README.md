# ShootingGame

A simple 2D shooting game built with Python and Pygame.

## Features

- Player-controlled spaceship
- Enemy spawning system
- Shooting mechanics
- Collision detection
- Score tracking
- Game states (Menu, Playing, Game Over)
- Health system

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

2. Controls:
   - **WASD** or **Arrow Keys**: Move the player
   - **SPACE**: Shoot bullets
   - **SPACE** (in menu): Start game

3. Objective:
   - Destroy enemies by shooting them
   - Avoid collisions with enemies
   - Survive as long as possible and get the highest score!

## Game Mechanics

- **Player**: Green rectangle that can move in all directions
- **Enemies**: Red rectangles that move down the screen
- **Bullets**: Yellow projectiles fired by the player
- **Scoring**: +10 points for each enemy destroyed
- **Health**: Player starts with 100 health, loses 20 per enemy collision
- **Game Over**: When player health reaches 0

## Project Structure

```
shooting_game/
├── game.py              # Main game loop
├── entities.py          # Player, Enemy, and Bullet classes
├── game_manager.py      # Game state management and logic
├── requirements.txt     # Python dependencies
└── README.md           # This file
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
