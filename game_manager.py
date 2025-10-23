"""
Game Manager - Handles game states, scoring, and game logic
"""

import pygame
import random
import time
from entities import Player, Enemy, Bullet
from audio_manager import AudioManager

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
        
        # Audio manager
        self.audio = AudioManager()
        # Don't play music in __init__, wait until game starts
        
        # Create starfield background
        self.stars = self.create_starfield()
        
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
        
        # Restart background music from the beginning
        self.audio.restart_music()
    
    def create_starfield(self):
        """Create a starfield background"""
        stars = []
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            speed = random.uniform(0.1, 0.5)
            stars.append({'x': x, 'y': y, 'size': size, 'brightness': brightness, 'speed': speed})
        return stars
    
    def update_starfield(self):
        """Update starfield animation"""
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.screen_height:
                star['y'] = 0
                star['x'] = random.randint(0, self.screen_width)
    
    def draw_starfield(self):
        """Draw animated starfield"""
        for star in self.stars:
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])
        
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if self.state == self.MENU:
                if event.key == pygame.K_SPACE:
                    self.audio.play_sound('menu_select')
                    self.reset_game()
            elif self.state == self.GAME_OVER:
                if event.key == pygame.K_SPACE:
                    self.audio.play_sound('menu_select')
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
        # Update starfield in all states
        self.update_starfield()
        
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
                self.audio.play_sound('shoot')  # Play shoot sound
            
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
                        self.audio.play_sound('enemy_shoot')  # Play enemy shoot sound
            
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
                            self.audio.play_sound('hit')  # Play hit sound
            
            # Check enemy bullet-player collisions
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_bullets:
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    self.audio.stop_music()  # Stop music when game over
                    self.audio.play_sound('game_over')  # Play game over sound
                    if self.score > self.high_score:
                        self.high_score = self.score
            
            # Check player-enemy collisions
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if hit_enemies:
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    self.audio.stop_music()  # Stop music when game over
                    self.audio.play_sound('game_over')  # Play game over sound
                    if self.score > self.high_score:
                        self.high_score = self.score
    
    def draw(self):
        """Draw game based on current state"""
        # Draw dark space background
        self.screen.fill((5, 5, 15))  # Dark blue-black space
        
        # Draw animated starfield
        self.draw_starfield()
        
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
        
        # Draw UI - Health (Hearts as shapes instead of text)
        heart_x = 10
        heart_y = 50
        heart_size = 20
        for i in range(self.player.health):
            # Draw simple heart shape using polygons
            x = heart_x + i * 35
            y = heart_y
            
            # Draw a simple heart using circles and triangle
            # Left circle
            pygame.draw.circle(self.screen, (255, 0, 0), (x + 8, y + 8), 8)
            # Right circle
            pygame.draw.circle(self.screen, (255, 0, 0), (x + 20, y + 8), 8)
            # Bottom triangle
            pygame.draw.polygon(self.screen, (255, 0, 0), [
                (x + 2, y + 10),
                (x + 26, y + 10),
                (x + 14, y + 28)
            ])
        
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
