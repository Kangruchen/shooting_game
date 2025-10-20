"""
ShootingGame - Main Game File
A 2D shooting game built with Pygame
"""

import pygame
import sys
from entities import Player, Enemy, Bullet
from game_manager import GameManager

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

def main():
    """Main game function"""
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ShootingGame")
    clock = pygame.time.Clock()
    
    # Create game manager
    game_manager = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event)
        
        # Update game state
        game_manager.update()
        
        # Draw everything
        game_manager.draw()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
