"""
Game Manager - Handles game states, scoring, and game logic
"""

import pygame
import random
import time
import math
from entities import Player, Enemy, TriangleEnemy, SquareEnemy, Bullet, HealthPack, PowerUp, Particle
from audio_manager import AudioManager
from config_loader import config

class ScorePopup(pygame.sprite.Sprite):
    """Floating score text that appears when enemy is destroyed"""
    
    def __init__(self, x, y, points, is_powered=False):
        super().__init__()
        self.points = points
        self.lifetime = 60  # Show for 1 second at 60 FPS
        self.age = 0
        self.is_powered = is_powered
        
        # Create text with outline for better visibility
        font_size = 40 if is_powered else 30
        font = pygame.font.Font(None, font_size)
        text = f"+{points}"
        
        if is_powered:
            # Create a surface with glow effect for powered-up scores
            text_color = (255, 215, 0)  # Gold
            outline_color = (255, 165, 0)  # Orange outline
            
            # Render text with outline
            text_surface = font.render(text, True, text_color)
            outline_surface = font.render(text, True, outline_color)
            
            # Create image with padding for outline
            padding = 4
            self.image = pygame.Surface((text_surface.get_width() + padding * 2, 
                                        text_surface.get_height() + padding * 2), pygame.SRCALPHA)
            
            # Draw outline (4 directions)
            self.image.blit(outline_surface, (padding - 2, padding))
            self.image.blit(outline_surface, (padding + 2, padding))
            self.image.blit(outline_surface, (padding, padding - 2))
            self.image.blit(outline_surface, (padding, padding + 2))
            
            # Draw main text
            self.image.blit(text_surface, (padding, padding))
        else:
            # Normal score - simple white text
            text_color = (255, 255, 255)
            self.image = font.render(text, True, text_color)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Movement
        self.vel_y = -2  # Float upward
        self.start_y = y
        
    def update(self):
        """Update popup animation"""
        self.age += 1
        
        # Float upward
        self.rect.y += self.vel_y
        
        # Fade out effect by adjusting alpha
        if self.age > self.lifetime * 0.5:
            fade = 1.0 - (self.age - self.lifetime * 0.5) / (self.lifetime * 0.5)
            self.image.set_alpha(int(255 * fade))
        
        # Remove when lifetime expires
        if self.age >= self.lifetime:
            self.kill()

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
        self.score_popups = pygame.sprite.Group()  # Floating score text
        self.particles = pygame.sprite.Group()  # Particle effects
        
        # Player
        self.player = None
        
        # Screen shake effect
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Energy bar system for power-up
        self.energy = 0.0  # 0.0 to 1.0 (0% to 100%)
        
        # Low health warning effect
        self.low_health_flash = 0  # Flash timer for low health warning
        
        # Enemy spawn timer - load from config
        self.enemy_spawn_timer = 0
        # Get initial spawn delay from stage 0
        stages = config.get('difficulty', 'stages')
        self.base_spawn_delay = stages[0]['spawn_delay']
        self.enemy_spawn_delay = self.base_spawn_delay
        self.difficulty_timer = 0  # Timer for difficulty increases
        self.difficulty_level = 0  # Track difficulty level (0-6 for 7 stages)
        self.difficulty_flash = 0  # Flash effect counter
        self.max_difficulty_level = config.get('difficulty', 'max_level')
        
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
        
        # Create nebula layers for background
        self.nebula_layers = self.create_nebula_layers()
        
    def reset_game(self):
        """Reset game for new playthrough"""
        self.all_sprites.empty()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.health_packs.empty()
        self.score_popups.empty()
        
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
        """Create a starfield background with multiple star types"""
        stars = []
        star_count = config.get('game', 'star_count')
        for _ in range(star_count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.choice([1, 1, 1, 2, 2, 3])  # More small stars
            brightness = random.randint(150, 255)
            speed = random.uniform(0.1, 0.8) * (size * 0.5)  # Bigger stars move slightly faster
            # Add twinkling effect
            twinkle_speed = random.uniform(0.02, 0.05)
            twinkle_offset = random.uniform(0, 6.28)  # Random phase
            stars.append({
                'x': x, 
                'y': y, 
                'size': size, 
                'brightness': brightness, 
                'speed': speed,
                'twinkle_speed': twinkle_speed,
                'twinkle_offset': twinkle_offset
            })
        return stars
    
    def create_nebula_layers(self):
        """Create nebula background layers for depth"""
        layers = []
        num_layers = config.get('game', 'nebula_layers')
        
        for i in range(num_layers):
            layer = {
                'offset_x': random.uniform(0, 100),
                'offset_y': random.uniform(0, 100),
                'speed': 0.05 * (i + 1),  # Each layer moves at different speed
                'scale': 150 + i * 50,
                'alpha': 20 + i * 10
            }
            layers.append(layer)
        return layers
    
    def update_starfield(self):
        """Update starfield animation with parallax scrolling"""
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.screen_height:
                star['y'] = 0
                star['x'] = random.randint(0, self.screen_width)
        
        # Update nebula layers
        for layer in self.nebula_layers:
            layer['offset_y'] += layer['speed']
            if layer['offset_y'] > 200:
                layer['offset_y'] = 0
    
    def draw_starfield(self):
        """Draw animated starfield with twinkling stars"""
        for star in self.stars:
            # Twinkling effect using sine wave
            twinkle = math.sin(self.game_time * star['twinkle_speed'] + star['twinkle_offset'])
            brightness = int(star['brightness'] + twinkle * 30)
            brightness = max(100, min(255, brightness))
            
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])
    
    def draw_nebula(self):
        """Draw nebula background layers"""
        for i, layer in enumerate(self.nebula_layers):
            nebula_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            
            # Color shifts based on difficulty
            if self.difficulty_level <= 2:
                # Blue-purple nebula for early stages
                base_color = (20, 10, 60)
            elif self.difficulty_level <= 4:
                # Purple-red nebula for mid stages
                base_color = (40, 10, 40)
            else:
                # Red nebula for hell stages
                base_color = (50, 10, 20)
            
            # Draw multiple nebula clouds
            for j in range(3):
                x = (self.screen_width // 3 * j + layer['offset_x']) % self.screen_width
                y = (layer['offset_y'] + j * 150) % self.screen_height
                
                for radius in range(layer['scale'], 0, -20):
                    alpha = int(layer['alpha'] * (radius / layer['scale']))
                    color = (*base_color, alpha)
                    pygame.draw.circle(nebula_surface, color, (int(x), int(y)), radius)
            
            self.screen.blit(nebula_surface, (0, 0))
    
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
        
        # Display stage name text
        if self.difficulty_flash > 30:  # Show text for first half of flash
            warning_font = pygame.font.Font(None, 48)
            
            # Get current stage name
            stages = config.get('difficulty', 'stages')
            stage_name = stages[self.difficulty_level]['name']
            
            text = warning_font.render(stage_name, True, (255, 200, 0))
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
    
    def add_screen_shake(self, intensity, duration):
        """Add screen shake effect
        
        Args:
            intensity: Maximum offset in pixels
            duration: Number of frames to shake
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
    
    def update_screen_shake(self):
        """Update screen shake effect"""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            # Random offset within intensity
            self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            
            # Decay intensity
            if self.shake_duration <= 0:
                self.shake_offset_x = 0
                self.shake_offset_y = 0
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def update_low_health_warning(self):
        """Update low health warning visual effect"""
        if self.player.health <= 1:
            # Continuous flashing when at 1 health
            self.low_health_flash += 1
        else:
            # Fade out effect
            if self.low_health_flash > 0:
                self.low_health_flash -= 2
                if self.low_health_flash < 0:
                    self.low_health_flash = 0
    
    def create_explosion_particles(self, x, y, color, count=None):
        """Create particle explosion effect
        
        Args:
            x, y: Position of explosion
            color: Base color for particles (will add variation)
            count: Number of particles (uses config default if None)
        """
        if count is None:
            count = config.get('particles', 'explosion_count')
        
        speed_min = config.get('particles', 'explosion_speed_min')
        speed_max = config.get('particles', 'explosion_speed_max')
        lifetime = config.get('particles', 'explosion_lifetime')
        size_min = config.get('particles', 'explosion_size_min')
        size_max = config.get('particles', 'explosion_size_max')
        
        for _ in range(count):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_min, speed_max)
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            
            # Color variation
            color_variation = random.randint(-30, 30)
            particle_color = tuple(max(0, min(255, c + color_variation)) for c in color[:3])
            
            # Size variation
            size = random.randint(size_min, size_max)
            
            # Create particle
            particle = Particle(x, y, particle_color, speed_x, speed_y, size, lifetime)
            self.particles.add(particle)
            self.all_sprites.add(particle)
        
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
                        
                        # Screen shake when activating powerup
                        shake_intensity = config.get('screen_shake', 'powerup_activate_intensity')
                        shake_duration = config.get('screen_shake', 'powerup_activate_duration')
                        self.add_screen_shake(shake_intensity, shake_duration)
                        
                        # self.audio.play_sound('powerup')
    
    def spawn_enemy(self):
        """Spawn a new enemy from random edge of screen"""
        # Get current stage weights
        stages = config.get('difficulty', 'stages')
        current_stage = stages[min(self.difficulty_level, len(stages) - 1)]
        
        circle_weight = current_stage['circle_weight']
        triangle_weight = current_stage['triangle_weight']
        square_weight = current_stage['square_weight']
        
        enemy_roll = random.random()
        enemy_type = None
        
        if enemy_roll < circle_weight:
            enemy_type = 'circle'
            offset = 40
        elif enemy_roll < circle_weight + triangle_weight:
            enemy_type = 'triangle'
            offset = 40
        else:
            enemy_type = 'square'
            offset = 50  # Adjusted offset for large enemy (closer to screen edge)
        
        edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
        
        if edge == 0:  # Top
            x = random.randint(0, self.screen_width)
            y = -offset
        elif edge == 1:  # Right
            x = self.screen_width + offset
            y = random.randint(0, self.screen_height)
        elif edge == 2:  # Bottom
            x = random.randint(0, self.screen_width)
            y = self.screen_height + offset
        else:  # Left
            x = -offset
            y = random.randint(0, self.screen_height)
        
        # Create enemy based on determined type
        if enemy_type == 'circle':
            enemy = Enemy(x, y, self.screen_width, self.screen_height)
        elif enemy_type == 'triangle':
            enemy = TriangleEnemy(x, y, self.screen_width, self.screen_height)
        else:
            enemy = SquareEnemy(x, y, self.screen_width, self.screen_height)
        
        # Apply Stage 7 damage boost if applicable
        if 'all_enemies_damage' in current_stage:
            enemy.bullet_damage = current_stage['all_enemies_damage']
        if 'all_enemies_collision_damage' in current_stage:
            enemy.collision_damage = current_stage['all_enemies_collision_damage']
        
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
    
    def update(self):
        """Update game logic based on current state"""
        # Update starfield in all states
        self.update_starfield()
        
        # Update screen shake
        self.update_screen_shake()
        
        if self.state == self.PLAYING:
            # Update game time
            self.game_time = time.time() - self.game_start_time
            
            # Update low health warning effect
            self.update_low_health_warning()
            
            # Update difficulty flash effect
            if self.difficulty_flash > 0:
                self.difficulty_flash -= 1
            
            # Difficulty increase based on config stages
            fps = config.get('game', 'fps')
            level_interval = config.get('difficulty', 'level_up_interval_seconds')
            frames_per_level = level_interval * fps
            
            self.difficulty_timer += 1
            if self.difficulty_timer >= frames_per_level:
                self.difficulty_timer = 0
                
                # Check if we can increase difficulty level
                if self.difficulty_level < self.max_difficulty_level:
                    self.difficulty_level += 1
                    
                    # Get new stage configuration
                    stages = config.get('difficulty', 'stages')
                    new_stage = stages[self.difficulty_level]
                    self.enemy_spawn_delay = new_stage['spawn_delay']
                    
                    self.difficulty_flash = 60  # Flash for 1 second
                    self.audio.play_sound('warning')  # Play warning sound on difficulty increase
                    print(f"[难度提升] {new_stage['name']} - 刷新间隔={new_stage['spawn_delay']}帧")
            
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
                health_pack.update(self.player.rect.center, self.player.powered_up)
            
            # Update score popups
            self.score_popups.update()
            
            # Update particles
            self.particles.update()
            
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
                            enemy_color = (220, 50, 50)  # Default red (circle)
                            
                            if hasattr(enemy, 'enemy_type'):
                                if enemy.enemy_type == "triangle":
                                    health_drop_chance = config.get('enemy_triangle', 'health_pack_drop_chance')
                                    energy_charge = config.get('enemy_triangle', 'energy_charge')
                                    points = config.get('enemy_triangle', 'points')
                                    enemy_color = (200, 50, 200)  # Purple/Magenta for triangle
                                elif enemy.enemy_type == "square":
                                    health_drop_chance = config.get('enemy_square', 'health_pack_drop_chance')
                                    energy_charge = config.get('enemy_square', 'energy_charge')
                                    points = config.get('enemy_square', 'points')
                                    enemy_color = (255, 180, 50)  # Orange for square
                                    # Bigger explosion for square
                                    self.create_explosion_particles(enemy.rect.centerx, enemy.rect.centery, enemy_color, count=25)
                                    # Stronger shake for square
                                    shake_intensity = config.get('screen_shake', 'square_kill_intensity')
                                    shake_duration = config.get('screen_shake', 'square_kill_duration')
                                    self.add_screen_shake(shake_intensity, shake_duration)
                                else:
                                    health_drop_chance = config.get('enemy_circle', 'health_pack_drop_chance')
                                    energy_charge = config.get('enemy_circle', 'energy_charge')
                                    points = config.get('enemy_circle', 'points')
                                    enemy_color = (220, 50, 50)  # Red for circle
                            
                            # Create explosion particles if not square (square handled above)
                            if not hasattr(enemy, 'enemy_type') or enemy.enemy_type != "square":
                                self.create_explosion_particles(enemy.rect.centerx, enemy.rect.centery, enemy_color)
                                # Normal shake for other enemies
                                shake_intensity = config.get('screen_shake', 'enemy_kill_intensity')
                                shake_duration = config.get('screen_shake', 'enemy_kill_duration')
                                self.add_screen_shake(shake_intensity, shake_duration)
                            
                            # Apply score multiplier when powered up
                            if self.player.powered_up:
                                score_multiplier = config.get('powerup', 'score_multiplier')
                                points *= score_multiplier
                            
                            self.score += points
                            
                            # Create floating score popup
                            score_popup = ScorePopup(enemy.rect.centerx, enemy.rect.centery, points, self.player.powered_up)
                            self.score_popups.add(score_popup)
                            
                            # Add energy (cap at 1.0)
                            self.energy = min(1.0, self.energy + energy_charge)
                            
                            # Drop health pack with calculated chance
                            # Use multiplier from config when player is powered up
                            health_multiplier = config.get('powerup', 'health_drop_rate_multiplier')
                            actual_drop_chance = health_drop_chance * health_multiplier if self.player.powered_up else health_drop_chance
                            if random.random() < actual_drop_chance:
                                health_pack = HealthPack(enemy.rect.centerx, enemy.rect.centery)
                                self.health_packs.add(health_pack)
                                self.all_sprites.add(health_pack)
                            
                            self.audio.play_sound('hit')  # Play hit sound
            
            # Check enemy bullet-player collisions
            hit_bullets = pygame.sprite.spritecollide(self.player, self.enemy_bullets, False)
            if hit_bullets:
                # Only remove bullets and play sound if player actually takes damage (not invincible)
                if not self.player.invincible:
                    # Calculate total damage from all bullets
                    total_damage = sum(bullet.damage if hasattr(bullet, 'damage') else 1 for bullet in hit_bullets)
                    for bullet in hit_bullets:
                        bullet.kill()
                    
                    # Screen shake when player is hit
                    shake_intensity = config.get('screen_shake', 'player_hit_intensity')
                    shake_duration = config.get('screen_shake', 'player_hit_duration')
                    self.add_screen_shake(shake_intensity, shake_duration)
                    
                    self.audio.play_sound('explosion')  # Play explosion sound when player is hit
                    if self.player.take_damage(total_damage):
                        self.state = self.GAME_OVER
                        self.audio.stop_music()  # Stop music when game over
                        self.audio.play_sound('game_over')  # Play game over sound
                        if self.score > self.high_score:
                            self.high_score = self.score
                else:
                    # Remove bullets even during invincibility but don't play sound
                    for bullet in hit_bullets:
                        bullet.kill()
            
            # Check player-enemy collisions
            hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hit_enemies:
                # Only kill enemies and play sound if player actually takes damage (not invincible)
                if not self.player.invincible:
                    # Calculate total collision damage from all hit enemies
                    total_damage = sum(enemy.collision_damage for enemy in hit_enemies)
                    for enemy in hit_enemies:
                        enemy.kill()
                    
                    # Screen shake when player collides with enemy
                    shake_intensity = config.get('screen_shake', 'player_hit_intensity')
                    shake_duration = config.get('screen_shake', 'player_hit_duration')
                    self.add_screen_shake(shake_intensity, shake_duration)
                    
                    self.audio.play_sound('explosion')  # Play explosion sound when player is hit
                    if self.player.take_damage(total_damage):
                        self.state = self.GAME_OVER
                        self.audio.stop_music()  # Stop music when game over
                        self.audio.play_sound('game_over')  # Play game over sound
                        if self.score > self.high_score:
                            self.high_score = self.score
                else:
                    # Kill enemies even during invincibility but don't play sound
                    for enemy in hit_enemies:
                        enemy.kill()
            
            # Check player-health pack collisions
            collected_packs = pygame.sprite.spritecollide(self.player, self.health_packs, True)
            if collected_packs:
                max_health_limit = config.get('player', 'max_health_limit')
                
                for pack in collected_packs:
                    # Check if player is at full health for bonus score
                    if self.player.health >= max_health_limit:
                        # Award bonus score instead of healing
                        bonus_score = config.get('health_pack', 'full_health_bonus_score')
                        self.score += bonus_score
                        
                        # Create floating score popup at health pack position
                        score_popup = ScorePopup(pack.rect.centerx, pack.rect.centery, bonus_score, False)
                        self.score_popups.add(score_popup)
                        
                        self.audio.play_sound('heal')  # Play heal sound for bonus
                    else:
                        # Heal player using config heal amount
                        heal_amount = config.get('health_pack', 'heal_amount')
                        self.player.health = min(self.player.health + heal_amount, max_health_limit)
                        self.audio.play_sound('heal')  # Play heal sound when collecting health pack
    
    def draw(self):
        """Draw game based on current state"""
        # Draw dark space background with difficulty-based color shift
        base_color = 5
        # Background gets slightly redder as difficulty increases
        red_shift = min(30, self.difficulty_level * 3)
        bg_color = (base_color + red_shift, base_color, base_color + 15)
        self.screen.fill(bg_color)
        
        # Draw nebula layers for depth
        self.draw_nebula()
        
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
        # Apply screen shake offset to all sprite drawing
        offset_x = self.shake_offset_x
        offset_y = self.shake_offset_y
        
        # Draw all sprites with shake offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x + offset_x, sprite.rect.y + offset_y))
        
        # Draw score popups with shake offset (on top of game sprites but below UI)
        for popup in self.score_popups:
            self.screen.blit(popup.image, (popup.rect.x + offset_x, popup.rect.y + offset_y))
        
        # Draw enemy warning indicators
        self.draw_enemy_warnings()
        
        # Draw UI panel background (semi-transparent)
        self.draw_ui_panel()
        
        # Draw UI - Score with shadow
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        shadow_text = self.font.render(f"SCORE: {self.score}", True, (0, 0, 0))
        self.screen.blit(shadow_text, (22, 17))
        self.screen.blit(score_text, (20, 15))
        
        # Draw UI - Health (Hearts as shapes with glow)
        heart_x = 20
        heart_y = 55
        max_health_limit = config.get('player', 'max_health_limit')
        
        for i in range(max_health_limit):
            x = heart_x + i * 40
            y = heart_y
            
            if i < self.player.health:
                # Filled heart with glow
                # Glow effect
                glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 100, 100, 80), (20, 20), 18)
                self.screen.blit(glow_surface, (x - 6, y - 2))
                
                # Main heart
                pygame.draw.circle(self.screen, (255, 50, 50), (x + 8, y + 8), 8)
                pygame.draw.circle(self.screen, (255, 50, 50), (x + 20, y + 8), 8)
                pygame.draw.polygon(self.screen, (255, 50, 50), [
                    (x + 2, y + 10),
                    (x + 26, y + 10),
                    (x + 14, y + 28)
                ])
                # Highlight
                pygame.draw.circle(self.screen, (255, 150, 150), (x + 6, y + 6), 3)
                pygame.draw.circle(self.screen, (255, 150, 150), (x + 18, y + 6), 3)
            else:
                # Empty heart outline
                pygame.draw.circle(self.screen, (100, 30, 30), (x + 8, y + 8), 8, width=2)
                pygame.draw.circle(self.screen, (100, 30, 30), (x + 20, y + 8), 8, width=2)
                pygame.draw.polygon(self.screen, (100, 30, 30), [
                    (x + 2, y + 10),
                    (x + 26, y + 10),
                    (x + 14, y + 28)
                ], width=2)
        
        # Draw UI - Game Time with icon
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (200, 200, 255))
        shadow_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))
        # Clock icon
        pygame.draw.circle(self.screen, (200, 200, 255), (self.screen_width - 220, 28), 12, width=2)
        pygame.draw.line(self.screen, (200, 200, 255), (self.screen_width - 220, 28), (self.screen_width - 220, 20), 2)
        pygame.draw.line(self.screen, (200, 200, 255), (self.screen_width - 220, 28), (self.screen_width - 214, 28), 2)
        self.screen.blit(shadow_text, (self.screen_width - 185, 17))
        self.screen.blit(time_text, (self.screen_width - 187, 15))
        
        # Draw difficulty level indicator with style
        if self.difficulty_level > 0:
            stages = config.get('difficulty', 'stages')
            stage_name = stages[self.difficulty_level]['name']
            level_text = self.font.render(stage_name, True, (255, 200, 100))
            shadow_text = self.font.render(stage_name, True, (0, 0, 0))
            self.screen.blit(shadow_text, (self.screen_width - level_text.get_width() - 18, 52))
            self.screen.blit(level_text, (self.screen_width - level_text.get_width() - 20, 50))
        
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
        
        # Draw low health warning visual effects if health is critical
        if self.player.health <= 1:
            self.draw_low_health_warning()
    
    def draw_low_health_warning(self):
        """Draw visual warning effects when health is critically low - optimized version"""
        # Slower pulsing with reduced frequency
        pulse = abs(math.sin(self.low_health_flash * 0.05))
        alpha = int(60 * pulse)
        
        if alpha == 0:
            return
        
        # Create warning overlay with red tint
        warning_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw smooth gradient from edges using rectangles for performance
        border_size = int(min(self.screen_width, self.screen_height) * 0.1)  # 10% from each edge
        
        # Draw gradient layers - much faster than per-pixel
        steps = 20  # Number of gradient steps (reduced for performance)
        for i in range(steps):
            # Calculate distance and alpha for this layer
            layer_dist = int((i / steps) * border_size)
            fade = i / steps
            layer_alpha = int(alpha * (1 - fade))
            
            if layer_alpha > 0:
                color = (255, 0, 0, layer_alpha)
                thickness = max(1, border_size // steps)
                
                # Top border
                pygame.draw.rect(warning_surface, color, 
                               (layer_dist, layer_dist, 
                                self.screen_width - 2 * layer_dist, thickness))
                # Bottom border
                pygame.draw.rect(warning_surface, color,
                               (layer_dist, self.screen_height - layer_dist - thickness,
                                self.screen_width - 2 * layer_dist, thickness))
                # Left border
                pygame.draw.rect(warning_surface, color,
                               (layer_dist, layer_dist,
                                thickness, self.screen_height - 2 * layer_dist))
                # Right border
                pygame.draw.rect(warning_surface, color,
                               (self.screen_width - layer_dist - thickness, layer_dist,
                                thickness, self.screen_height - 2 * layer_dist))
        
        self.screen.blit(warning_surface, (0, 0))
        
        # Subtle screen edge accent lines
        edge_alpha = int(80 * pulse)
        if edge_alpha > 0:
            edge_thickness = 2
            
            # Top edge
            pygame.draw.rect(warning_surface, (255, 50, 50, edge_alpha), 
                            (0, 0, self.screen_width, edge_thickness))
            # Bottom edge
            pygame.draw.rect(warning_surface, (255, 50, 50, edge_alpha), 
                            (0, self.screen_height - edge_thickness, self.screen_width, edge_thickness))
            # Left edge
            pygame.draw.rect(warning_surface, (255, 50, 50, edge_alpha), 
                            (0, 0, edge_thickness, self.screen_height))
            # Right edge
            pygame.draw.rect(warning_surface, (255, 50, 50, edge_alpha), 
                            (self.screen_width - edge_thickness, 0, edge_thickness, self.screen_height))
            
            self.screen.blit(warning_surface, (0, 0))
    
    def draw_enemy_warnings(self):
        """Draw warning indicators for off-screen or near-edge enemies"""
        arrow_size = config.get('warning', 'arrow_size')
        arrow_distance = config.get('warning', 'arrow_distance')
        pulse_speed = config.get('warning', 'pulse_speed')
        warning_color = config.get('warning', 'warning_color')
        
        # Pulse effect for animation
        pulse = abs(math.sin(self.game_time * pulse_speed * 10))
        
        for enemy in self.enemies:
            # Only show warning if enemy is OUTSIDE the screen (not visible yet)
            is_off_screen = False
            arrow_x = 0
            arrow_y = 0
            direction = None  # 'top', 'bottom', 'left', 'right'
            
            # Check if enemy is outside screen bounds
            # Use strict checks - warning disappears as soon as enemy touches screen edge
            if enemy.rect.bottom <= 0:  # Enemy completely above screen
                is_off_screen = True
                direction = 'top'
                arrow_x = max(arrow_distance, min(self.screen_width - arrow_distance, enemy.rect.centerx))
                arrow_y = arrow_distance
            elif enemy.rect.top >= self.screen_height:  # Enemy completely below screen
                is_off_screen = True
                direction = 'bottom'
                arrow_x = max(arrow_distance, min(self.screen_width - arrow_distance, enemy.rect.centerx))
                arrow_y = self.screen_height - arrow_distance
            elif enemy.rect.right <= 0:  # Enemy completely left of screen
                is_off_screen = True
                direction = 'left'
                arrow_x = arrow_distance
                arrow_y = max(arrow_distance, min(self.screen_height - arrow_distance, enemy.rect.centery))
            elif enemy.rect.left >= self.screen_width:  # Enemy completely right of screen
                is_off_screen = True
                direction = 'right'
                arrow_x = self.screen_width - arrow_distance
                arrow_y = max(arrow_distance, min(self.screen_height - arrow_distance, enemy.rect.centery))
            
            if is_off_screen and direction:
                # Adjust color brightness with pulse
                pulse_brightness = int(155 + pulse * 100)
                color = tuple(int(c * pulse_brightness / 255) for c in warning_color)
                
                # Draw warning indicator
                self.draw_warning_arrow(arrow_x, arrow_y, direction, color, arrow_size, pulse)
    
    def draw_warning_arrow(self, x, y, direction, color, size, pulse):
        """Draw a warning arrow at the edge of the screen
        
        Args:
            x, y: Position to draw arrow
            direction: 'top', 'bottom', 'left', 'right'
            color: RGB color tuple
            size: Size of arrow
            pulse: Pulse value (0-1) for animation
        """
        # Create semi-transparent surface for glow
        glow_size = int(size * 2.5)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Glow effect
        for i in range(3, 0, -1):
            alpha = int(80 * (i / 3) * pulse)
            glow_color = (*color, alpha)
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), size + i * 5)
        
        self.screen.blit(glow_surface, (int(x - glow_size), int(y - glow_size)))
        
        # Draw arrow pointing toward enemy
        if direction == 'top':
            # Arrow pointing up
            points = [
                (x, y - size),
                (x - size * 0.6, y + size * 0.5),
                (x + size * 0.6, y + size * 0.5)
            ]
        elif direction == 'bottom':
            # Arrow pointing down
            points = [
                (x, y + size),
                (x - size * 0.6, y - size * 0.5),
                (x + size * 0.6, y - size * 0.5)
            ]
        elif direction == 'left':
            # Arrow pointing left
            points = [
                (x - size, y),
                (x + size * 0.5, y - size * 0.6),
                (x + size * 0.5, y + size * 0.6)
            ]
        else:  # right
            # Arrow pointing right
            points = [
                (x + size, y),
                (x - size * 0.5, y - size * 0.6),
                (x - size * 0.5, y + size * 0.6)
            ]
        
        # Draw arrow with outline
        pygame.draw.polygon(self.screen, (0, 0, 0), points, width=0)  # Black fill for outline
        pygame.draw.polygon(self.screen, color, [(p[0], p[1]) for p in points])
        pygame.draw.polygon(self.screen, (255, 255, 255), points, width=2)  # White outline
    
    def draw_ui_panel(self):
        """Draw semi-transparent UI panel background"""
        # Top panel for score and stats
        top_panel = pygame.Surface((self.screen_width, 100), pygame.SRCALPHA)
        pygame.draw.rect(top_panel, (0, 0, 0, 120), (0, 0, self.screen_width, 100))
        # Bottom gradient
        for i in range(20):
            alpha = int(120 * (1 - i / 20))
            pygame.draw.line(top_panel, (0, 0, 0, alpha), (0, 100 + i), (self.screen_width, 100 + i))
        self.screen.blit(top_panel, (0, 0))
        
        # Bottom panel for energy bar
        bottom_panel = pygame.Surface((self.screen_width, 100), pygame.SRCALPHA)
        # Top gradient
        for i in range(20):
            alpha = int(100 * (i / 20))
            pygame.draw.line(bottom_panel, (0, 0, 0, alpha), (0, i), (self.screen_width, i))
        pygame.draw.rect(bottom_panel, (0, 0, 0, 100), (0, 20, self.screen_width, 80))
        self.screen.blit(bottom_panel, (0, self.screen_height - 100))
    
    def draw_energy_bar(self):
        """Draw enhanced energy bar with glow effects"""
        bar_width = 500
        bar_height = 35
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 70
        
        # Clamp energy to 0.0-1.0 range for display
        display_energy = max(0.0, min(1.0, self.energy))
        
        # Background (dark with slight border) - DRAW FIRST
        pygame.draw.rect(self.screen, (20, 20, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        
        # Energy fill - DRAW ON TOP OF BACKGROUND
        fill_width = int(bar_width * display_energy)
        if fill_width > 0:
            # Color gradient from blue to gold as it fills
            if display_energy < 1.0:
                # Blue to cyan gradient
                color = (
                    int(max(0, min(255, 0 + display_energy * 255))),
                    int(max(0, min(255, 150 + display_energy * 105))),
                    int(max(0, min(255, 255 - display_energy * 40)))
                )
                # Inner glow
                glow_surface = pygame.Surface((fill_width + 20, bar_height + 20), pygame.SRCALPHA)
                for i in range(10, 0, -1):
                    alpha = int(30 * (i / 10))
                    glow_color = (*color, alpha)
                    pygame.draw.rect(glow_surface, glow_color, 
                                   (10 - i, 10 - i, fill_width + i * 2, bar_height + i * 2), 
                                   border_radius=8)
                self.screen.blit(glow_surface, (bar_x - 10, bar_y - 10))
            else:
                # Full - gold color with strong pulsing effect
                pulse = abs(math.sin(self.game_time * 5)) * 100
                color = (255, int(max(0, min(255, 215 + pulse))), 0)
                
                # Strong glow when full
                glow_surface = pygame.Surface((bar_width + 40, bar_height + 40), pygame.SRCALPHA)
                for i in range(20, 0, -1):
                    alpha = int(80 * (i / 20))
                    glow_color = (255, 200, 0, alpha)
                    pygame.draw.rect(glow_surface, glow_color, 
                                   (20 - i, 20 - i, bar_width + i * 2, bar_height + i * 2), 
                                   border_radius=10)
                self.screen.blit(glow_surface, (bar_x - 20, bar_y - 20))
            
            # Draw energy fill
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=8)
            
            # Shine effect on energy bar
            shine_surface = pygame.Surface((fill_width, bar_height // 2), pygame.SRCALPHA)
            for i in range(bar_height // 2):
                alpha = int(50 * (1 - i / (bar_height // 2)))
                pygame.draw.line(shine_surface, (255, 255, 255, alpha), (0, i), (fill_width, i))
            self.screen.blit(shine_surface, (bar_x, bar_y + 2))
        
        # Border - DRAW LAST
        border_color = (255, 215, 0) if self.energy >= 1.0 else (80, 80, 100)
        border_width_px = 4 if self.energy >= 1.0 else 3
        pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), 
                        width=border_width_px, border_radius=8)
        
        # Text
        if self.energy >= 1.0:
            # Pulsing text when ready
            pulse_alpha = int(200 + abs(math.sin(self.game_time * 6)) * 55)
            energy_text = self.font.render("⚡ PRESS SPACE TO ACTIVATE ⚡", True, (255, 255, 0))
            energy_text.set_alpha(pulse_alpha)
            text_x = self.screen_width // 2 - energy_text.get_width() // 2
            text_y = bar_y - 40
            
            # Text shadow
            shadow = self.font.render("⚡ PRESS SPACE TO ACTIVATE ⚡", True, (100, 100, 0))
            self.screen.blit(shadow, (text_x + 2, text_y + 2))
            self.screen.blit(energy_text, (text_x, text_y))
        else:
            # Energy percentage
            energy_percent = int(display_energy * 100)
            percent_text = self.font.render(f"ENERGY: {energy_percent}%", True, (150, 200, 255))
            text_x = self.screen_width // 2 - percent_text.get_width() // 2
            text_y = bar_y + (bar_height - percent_text.get_height()) // 2
            
            # Text shadow
            shadow = self.font.render(f"ENERGY: {energy_percent}%", True, (0, 0, 0))
            self.screen.blit(shadow, (text_x + 2, text_y + 2))
            self.screen.blit(percent_text, (text_x, text_y))
    
    def draw_game_over(self):
        """Draw game over screen"""
        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press SPACE to Continue", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, 200))
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (self.screen_width // 2 - restart_text.get_width() // 2, 400))
