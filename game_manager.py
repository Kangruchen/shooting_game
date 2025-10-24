"""
Game Manager - Handles game states, scoring, and game logic
"""

import pygame
import random
import time
import math
from entities import Player, Enemy, TriangleEnemy, Bullet, HealthPack, PowerUp
from audio_manager import AudioManager
from config_loader import config

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
        self.health_packs = pygame.sprite.Group()
        
        # Player
        self.player = None
        
        # Energy bar system for power-up
        self.energy = 0.0  # 0.0 to 1.0 (0% to 100%)
        
        # Enemy spawn timer - load from config
        self.enemy_spawn_timer = 0
        self.base_spawn_delay = config.get('difficulty', 'initial_spawn_delay')
        self.enemy_spawn_delay = self.base_spawn_delay
        self.difficulty_timer = 0  # Timer for difficulty increases
        self.difficulty_level = 0  # Track difficulty level
        self.difficulty_flash = 0  # Flash effect counter
        
        # Game time
        self.game_start_time = 0
        self.game_time = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        
        # Audio manager
        self.audio = AudioManager()
        # Don't play music in __init__, wait until game starts
        
        # Create starfield background from config
        self.stars = self.create_starfield()
        
    def reset_game(self):
        """Reset game for new playthrough"""
        self.all_sprites.empty()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.health_packs.empty()
        
        self.player = Player(self.screen_width // 2, self.screen_height // 2, 
                            self.screen_width, self.screen_height)
        self.all_sprites.add(self.player)
        
        self.score = 0
        # Load initial energy from config (for testing)
        self.energy = config.get('powerup', 'initial_energy')
        self.enemy_spawn_timer = 0
        self.difficulty_timer = 0
        self.difficulty_level = 0
        self.difficulty_flash = 0
        self.enemy_spawn_delay = self.base_spawn_delay
        self.game_start_time = time.time()
        self.game_time = 0
        self.state = self.PLAYING
        
        # Restart background music from the beginning
        self.audio.restart_music()
    
    def create_starfield(self):
        """Create a starfield background"""
        stars = []
        star_count = config.get('game', 'star_count')
        for _ in range(star_count):
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
    
    def draw_difficulty_warning(self):
        """Draw flashing warning effect when difficulty increases"""
        # Pulsing effect
        alpha = int(255 * (self.difficulty_flash / 60.0))
        
        # Create a surface for the warning effect
        warning_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw flashing border (thick red outline)
        border_width = 8
        flash_intensity = int(255 * (self.difficulty_flash / 60.0))
        border_color = (255, flash_intensity // 2, 0, alpha)
        
        # Top border
        pygame.draw.rect(warning_surface, border_color, (0, 0, self.screen_width, border_width))
        # Bottom border
        pygame.draw.rect(warning_surface, border_color, (0, self.screen_height - border_width, self.screen_width, border_width))
        # Left border
        pygame.draw.rect(warning_surface, border_color, (0, 0, border_width, self.screen_height))
        # Right border
        pygame.draw.rect(warning_surface, border_color, (self.screen_width - border_width, 0, border_width, self.screen_height))
        
        # Corner highlights (extra bright)
        corner_size = 30
        corner_color = (255, 200, 0, min(255, alpha + 50))
        pygame.draw.rect(warning_surface, corner_color, (0, 0, corner_size, corner_size))
        pygame.draw.rect(warning_surface, corner_color, (self.screen_width - corner_size, 0, corner_size, corner_size))
        pygame.draw.rect(warning_surface, corner_color, (0, self.screen_height - corner_size, corner_size, corner_size))
        pygame.draw.rect(warning_surface, corner_color, (self.screen_width - corner_size, self.screen_height - corner_size, corner_size, corner_size))
        
        self.screen.blit(warning_surface, (0, 0))
        
        # Display "DIFFICULTY INCREASED" text
        if self.difficulty_flash > 30:  # Show text for first half of flash
            warning_font = pygame.font.Font(None, 48)
            text = warning_font.render("DIFFICULTY INCREASED!", True, (255, 200, 0))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            
            # Background for text
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(self.screen, (255, 100, 0), bg_rect, width=3)
            
            self.screen.blit(text, text_rect)
    
    def draw_danger_border(self):
        """Draw persistent danger border that intensifies with difficulty"""
        # Subtle persistent border that gets more intense with difficulty
        intensity = min(100, 20 + self.difficulty_level * 8)
        border_width = 3
        
        # Animated pulse effect
        pulse = int(20 * abs(math.sin(self.game_time * 2)))
        border_alpha = intensity + pulse
        
        # Color shifts from orange to red as difficulty increases
        red = 255
        green = max(0, 100 - self.difficulty_level * 10)
        border_color = (red, green, 0, border_alpha)
        
        # Create border surface
        border_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw borders
        pygame.draw.rect(border_surface, border_color, (0, 0, self.screen_width, border_width))
        pygame.draw.rect(border_surface, border_color, (0, self.screen_height - border_width, self.screen_width, border_width))
        pygame.draw.rect(border_surface, border_color, (0, 0, border_width, self.screen_height))
        pygame.draw.rect(border_surface, border_color, (self.screen_width - border_width, 0, border_width, self.screen_height))
        
        self.screen.blit(border_surface, (0, 0))
        
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
            elif self.state == self.PLAYING:
                # Activate power-up with SPACE when energy is full
                if event.key == pygame.K_SPACE:
                    if self.energy >= 1.0 and not self.player.powered_up:
                        duration = config.get('powerup', 'duration_seconds')
                        self.player.activate_powerup(duration)
                        self.energy = 0.0  # Reset energy after activation
                        # self.audio.play_sound('powerup')
    
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
        
        # Spawn different enemy types based on config probabilities
        circle_weight = config.get('enemy_circle', 'spawn_weight')
        enemy_roll = random.random()
        
        if enemy_roll < circle_weight:
            # Spawn circle enemy (common)
            enemy = Enemy(x, y, self.screen_width, self.screen_height)
        else:
            # Spawn triangle enemy (rare)
            enemy = TriangleEnemy(x, y, self.screen_width, self.screen_height)
        
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
    
    def update(self):
        """Update game logic based on current state"""
        # Update starfield in all states
        self.update_starfield()
        
        if self.state == self.PLAYING:
            # Update game time
            self.game_time = time.time() - self.game_start_time
            
            # Update difficulty flash effect
            if self.difficulty_flash > 0:
                self.difficulty_flash -= 1
            
            # Difficulty increase based on config
            fps = config.get('game', 'fps')
            level_interval = config.get('difficulty', 'level_up_interval_seconds')
            frames_per_level = level_interval * fps
            
            self.difficulty_timer += 1
            if self.difficulty_timer >= frames_per_level:
                self.difficulty_timer = 0
                # Increase spawn rate (decrease delay)
                min_delay = config.get('difficulty', 'min_spawn_delay')
                decrease_amount = config.get('difficulty', 'spawn_delay_decrease')
                
                if self.enemy_spawn_delay > min_delay:
                    self.enemy_spawn_delay = max(min_delay, self.enemy_spawn_delay - decrease_amount)
                    self.difficulty_level += 1
                    self.difficulty_flash = 60  # Flash for 1 second
                    self.audio.play_sound('warning')  # Play warning sound on difficulty increase
            
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            
            # Player shooting (continuous with arrow keys)
            bullets, should_play_sound, sound_name = self.player.shoot(keys)
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
            
            # Play appropriate shoot sound
            if should_play_sound and sound_name:
                self.audio.play_sound(sound_name)
            
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
            
            # Update health packs
            for health_pack in self.health_packs:
                health_pack.update()
            
            # Check player bullet-enemy collisions
            for bullet in self.player_bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                if hit_enemies:
                    bullet.kill()
                    for enemy in hit_enemies:
                        if enemy.take_damage(10):
                            # Enemy destroyed - add energy and check for health pack drop
                            health_drop_chance = 0.0
                            energy_charge = 0.0
                            points = 10
                            
                            if hasattr(enemy, 'enemy_type'):
                                if enemy.enemy_type == "triangle":
                                    health_drop_chance = config.get('enemy_triangle', 'health_pack_drop_chance')
                                    energy_charge = config.get('enemy_triangle', 'energy_charge')
                                    points = config.get('enemy_triangle', 'points')
                                else:
                                    health_drop_chance = config.get('enemy_circle', 'health_pack_drop_chance')
                                    energy_charge = config.get('enemy_circle', 'energy_charge')
                                    points = config.get('enemy_circle', 'points')
                            
                            self.score += points
                            
                            # Add energy (cap at 1.0)
                            self.energy = min(1.0, self.energy + energy_charge)
                            
                            # Drop health pack with calculated chance
                            if random.random() < health_drop_chance:
                                health_pack = HealthPack(enemy.rect.centerx, enemy.rect.centery)
                                self.health_packs.add(health_pack)
                                self.all_sprites.add(health_pack)
                            
                            self.audio.play_sound('hit')  # Play hit sound
            
            # Check enemy bullet-player collisions
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            if hit_bullets:
                self.audio.play_sound('explosion')  # Play explosion sound when player is hit
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    self.audio.stop_music()  # Stop music when game over
                    self.audio.play_sound('game_over')  # Play game over sound
                    if self.score > self.high_score:
                        self.high_score = self.score
            
            # Check player-enemy collisions
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, True)
            if hit_enemies:
                self.audio.play_sound('explosion')  # Play explosion sound when player is hit
                if self.player.take_damage(1):
                    self.state = self.GAME_OVER
                    self.audio.stop_music()  # Stop music when game over
                    self.audio.play_sound('game_over')  # Play game over sound
                    if self.score > self.high_score:
                        self.high_score = self.score
            
            # Check player-health pack collisions
            collected_packs = pygame.sprite.spritecollide(self.player, self.health_packs, True)
            if collected_packs:
                # Heal player using config heal amount
                heal_amount = config.get('health_pack', 'heal_amount')
                self.player.health += heal_amount
                self.audio.play_sound('heal')  # Play heal sound when collecting health pack
    
    def draw(self):
        """Draw game based on current state"""
        # Draw dark space background with difficulty-based color shift
        base_color = 5
        # Background gets slightly redder as difficulty increases
        red_shift = min(30, self.difficulty_level * 3)
        bg_color = (base_color + red_shift, base_color, base_color + 15)
        self.screen.fill(bg_color)
        
        # Draw animated starfield
        self.draw_starfield()
        
        # Draw difficulty warning border flash
        if self.difficulty_flash > 0:
            self.draw_difficulty_warning()
        
        # Draw persistent danger border based on difficulty level
        if self.difficulty_level > 0:
            self.draw_danger_border()
        
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
        
        # Draw difficulty level indicator
        if self.difficulty_level > 0:
            level_text = self.font.render(f"Level: {self.difficulty_level + 1}", True, (255, 150, 0))
            self.screen.blit(level_text, (self.screen_width - 200, 50))
        
        # Draw UI - Power-up status
        if self.player.powered_up:
            fps = config.get('game', 'fps')
            time_left = self.player.powerup_timer / fps
            powerup_text = self.font.render(f"POWER-UP: {time_left:.1f}s", True, (255, 215, 0))
            # Draw with pulsing effect
            pulse = abs(math.sin(self.player.powerup_timer * 0.1)) * 20
            powerup_bg = pygame.Surface((powerup_text.get_width() + 20, powerup_text.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(powerup_bg, (255, 215, 0, int(50 + pulse)), powerup_bg.get_rect(), border_radius=5)
            self.screen.blit(powerup_bg, (self.screen_width // 2 - powerup_text.get_width() // 2 - 10, 10))
            self.screen.blit(powerup_text, (self.screen_width // 2 - powerup_text.get_width() // 2, 15))
        
        # Draw energy bar at bottom of screen
        self.draw_energy_bar()
    
    def draw_energy_bar(self):
        """Draw energy bar at the bottom of the screen"""
        bar_width = 400
        bar_height = 30
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 60
        
        # Background (dark)
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        # Clamp energy to 0.0-1.0 range for display
        display_energy = max(0.0, min(1.0, self.energy))
        
        # Energy fill
        fill_width = int(bar_width * display_energy)
        if fill_width > 0:
            # Color gradient from blue to gold as it fills
            if display_energy < 1.0:
                # Blue to cyan gradient - ensure values are in 0-255 range
                color = (
                    int(max(0, min(255, 0 + display_energy * 255))),
                    int(max(0, min(255, 150 + display_energy * 105))),
                    int(max(0, min(255, 255 - display_energy * 40)))
                )
            else:
                # Full - gold color with pulsing effect
                pulse = abs(math.sin(self.game_time * 3)) * 50
                color = (255, int(max(0, min(255, 215 + pulse))), 0)
            
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
        
        # Border
        border_color = (255, 215, 0) if self.energy >= 1.0 else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), width=3, border_radius=5)
        
        # Text
        if self.energy >= 1.0:
            energy_text = self.font.render("PRESS SPACE TO ACTIVATE!", True, (255, 255, 0))
            pulse_y = int(abs(math.sin(self.game_time * 3)) * 3)
            self.screen.blit(energy_text, (self.screen_width // 2 - energy_text.get_width() // 2, bar_y - 30 - pulse_y))
        else:
            percentage = int(display_energy * 100)
            energy_text = self.font.render(f"ENERGY: {percentage}%", True, (200, 200, 200))
            self.screen.blit(energy_text, (self.screen_width // 2 - energy_text.get_width() // 2, bar_y - 30))
    
    def draw_game_over(self):
        """Draw game over screen"""
        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press SPACE to Continue", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, 200))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, 400))
