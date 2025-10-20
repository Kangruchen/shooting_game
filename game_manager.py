"""
Game Manager - Handles game states, scoring, and game logic
"""

import pygame
import random
import time
from entities import Player, Enemy, Bullet

class GameManager:
    """Manages game state and logic"""
    
    # Game states
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.state = self.MENU
        self.score = 0
        self.high_score = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Player
        self.player = None
        
        # Enemy spawn timer
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 90  # frames
        
        # Game time
        self.game_start_time = 0
        self.game_time = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        
    def reset_game(self):
        """Reset game for new playthrough"""
        self.all_sprites.empty()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        
        self.player = Player(self.screen_width // 2, self.screen_height // 2, 
                            self.screen_width, self.screen_height)
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.enemy_spawn_timer = 0
        self.game_start_time = time.time()
        self.game_time = 0
        self.state = self.PLAYING
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if self.state == self.MENU:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
            elif self.state == self.GAME_OVER:
                if event.key == pygame.K_SPACE:
                    self.state = self.MENU
    
    def spawn_enemy(self):
        """Spawn a new enemy from random edge of screen"""
        edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
        
        if edge == 0:  # Top
            x = random.randint(0, self.screen_width)
            y = -40
        elif edge == 1:  # Right
            x = self.screen_width + 40
            y = random.randint(0, self.screen_height)
        elif edge == 2:  # Bottom
            x = random.randint(0, self.screen_width)
            y = self.screen_height + 40
        else:  # Left
            x = -40
            y = random.randint(0, self.screen_height)
        
        enemy = Enemy(x, y, self.screen_width, self.screen_height)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
    
    def update(self):
        """Update game logic based on current state"""
        if self.state == self.PLAYING:
            # Update game time
            self.game_time = time.time() - self.game_start_time
            
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            
            # Player shooting (continuous with arrow keys)
            bullets = self.player.shoot(keys)
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
            
            # Spawn enemies
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_delay:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # Update enemies and handle enemy shooting
            for enemy in self.enemies:
                enemy.update(self.player.rect.center)
                
                # Enemy shoots toward player
                if enemy.should_shoot():
                    bullet = enemy.shoot(self.player.rect.center)
                    if bullet:
                        self.enemy_bullets.add(bullet)
                        self.all_sprites.add(bullet)
            
            # Update bullets
            for bullet in self.player_bullets:
                bullet.update(self.screen_width, self.screen_height)
            for bullet in self.enemy_bullets:
                bullet.update(self.screen_width, self.screen_height)
            
            # Check player bullet-enemy collisions
            for bullet in self.player_bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                if hit_enemies:
                    bullet.kill()
                    for enemy in hit_enemies:
                        if enemy.take_damage(10):
                            self.score += 10
            
            # Check enemy bullet-player collisions
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_bullets:
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    if self.score > self.high_score:
                        self.high_score = self.score
            
            # Check player-enemy collisions
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if hit_enemies:
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    if self.score > self.high_score:
                        self.high_score = self.score
    
    def draw(self):
        """Draw game based on current state"""
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == self.MENU:
            self.draw_menu()
        elif self.state == self.PLAYING:
            self.draw_playing()
        elif self.state == self.GAME_OVER:
            self.draw_game_over()
    
    def draw_menu(self):
        """Draw menu screen"""
        title = self.large_font.render("ShootingGame", True, (255, 255, 255))
        start_text = self.font.render("Press SPACE to Start", True, (255, 255, 255))
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 255, 0))
        
        # Controls instructions
        controls_title = self.font.render("Controls:", True, (200, 200, 200))
        controls1 = self.font.render("WASD - Move", True, (150, 150, 150))
        controls2 = self.font.render("Arrow Keys - Shoot", True, (150, 150, 150))
        controls3 = self.font.render("Lives: 3 hearts", True, (150, 150, 150))
        
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))
        self.screen.blit(start_text, (self.screen_width // 2 - start_text.get_width() // 2, 250))
        self.screen.blit(high_score_text, (self.screen_width // 2 - high_score_text.get_width() // 2, 300))
        
        self.screen.blit(controls_title, (self.screen_width // 2 - controls_title.get_width() // 2, 370))
        self.screen.blit(controls1, (self.screen_width // 2 - controls1.get_width() // 2, 410))
        self.screen.blit(controls2, (self.screen_width // 2 - controls2.get_width() // 2, 445))
        self.screen.blit(controls3, (self.screen_width // 2 - controls3.get_width() // 2, 480))
    
    def draw_playing(self):
        """Draw playing screen"""
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw UI - Score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw UI - Health (Hearts)
        heart_x = 10
        heart_y = 50
        for i in range(self.player.health):
            heart_text = self.font.render("♥", True, (255, 0, 0))
            self.screen.blit(heart_text, (heart_x + i * 40, heart_y))
        
        # Draw UI - Game Time
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(time_text, (self.screen_width - 200, 10))
    
    def draw_game_over(self):
        """Draw game over screen"""
        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press SPACE to Continue", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, 200))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, 400))
