"""
Game Entities - Player, Enemy, Bullet classes
"""

import pygame
import random
import math
from config_loader import config

class Player(pygame.sprite.Sprite):
    """Player character class"""
    
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load player stats from config
        self.speed = config.get('player', 'speed')
        self.health = config.get('player', 'max_health')
        self.shoot_cooldown = 0
        self.shoot_delay = config.get('player', 'shoot_cooldown')
        
        # Power-up state
        self.powered_up = False
        self.powerup_timer = 0
        self.base_shoot_delay = self.shoot_delay
        
        # Sound effect counter for powered-up state
        self.shoot_sound_counter = 0
        self.sound_effect_interval = 3  # Play sound every 3 shots when powered up
        
        # Invincibility state after taking damage
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = config.get('player', 'invincibility_duration_frames')  # 0.5 seconds at 60 FPS (30 frames)
        
        # Create player surface with transparency (after all attributes are initialized)
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.draw_player()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def draw_player(self):
        """Draw player in retro space game style - simple square ship"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        # Check if should be visible (flashing effect during invincibility)
        if self.invincible:
            # Flash every 4 frames (fast blinking)
            if (self.invincible_timer // 4) % 2 == 0:
                return  # Skip drawing for flashing effect
        
        # Main ship body - bright green square with slight rounded corners
        pygame.draw.rect(self.image, (0, 220, 0), (10, 8, 30, 24), border_radius=4)
        
        # Darker inner panel (retro detail)
        pygame.draw.rect(self.image, (0, 150, 0), (14, 12, 22, 16), border_radius=2)
        
        # Cockpit window (bright cyan)
        pygame.draw.rect(self.image, (0, 255, 255), (20, 14, 10, 8), border_radius=2)
        
        # Wing details (small rectangles on sides)
        pygame.draw.rect(self.image, (0, 180, 0), (8, 16, 4, 8))  # Left wing
        pygame.draw.rect(self.image, (0, 180, 0), (38, 16, 4, 8))  # Right wing
        
        # Engine exhausts (simple rectangles at bottom)
        pygame.draw.rect(self.image, (255, 150, 0), (14, 32, 6, 4))  # Left engine
        pygame.draw.rect(self.image, (255, 150, 0), (30, 32, 6, 4))  # Right engine
        
        # Bright engine cores
        pygame.draw.rect(self.image, (255, 255, 100), (15, 33, 4, 2))
        pygame.draw.rect(self.image, (255, 255, 100), (31, 33, 4, 2))
        
        # White highlights on edges (retro reflections)
        pygame.draw.line(self.image, (100, 255, 150), (11, 9), (38, 9), 2)  # Top edge
        pygame.draw.line(self.image, (0, 180, 100), (11, 30), (38, 30), 1)  # Bottom edge
        
    def update(self, keys):
        """Update player position based on keyboard input (WASD only)"""
        move_x = 0
        move_y = 0
        
        # WASD for movement
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_d]:
            move_x += 1
        if keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_s]:
            move_y += 1
        
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707  # 1/sqrt(2)
            move_y *= 0.707
        
        self.rect.x += move_x * self.speed
        self.rect.y += move_y * self.speed
            
        # Keep player on screen
        self.rect.x = max(0, min(self.rect.x, self.screen_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, self.screen_height - self.rect.height))
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Update power-up timer
        if self.powered_up:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.deactivate_powerup()
        
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
            # Update visual appearance for flashing effect
            self.draw_player()
        elif hasattr(self, '_was_invincible') and self._was_invincible:
            # Redraw player when invincibility ends to ensure visibility
            self.draw_player()
        
        # Track invincibility state for redraw
        self._was_invincible = self.invincible
    
    def shoot(self, keys):
        """Create bullets based on arrow key direction
        Returns: (bullets, should_play_sound, sound_name)
        """
        if self.shoot_cooldown > 0:
            return [], False, None
        
        bullets = []
        shoot_x = 0
        shoot_y = 0
        
        # Arrow keys for shooting direction
        if keys[pygame.K_LEFT]:
            shoot_x -= 1
        if keys[pygame.K_RIGHT]:
            shoot_x += 1
        if keys[pygame.K_UP]:
            shoot_y -= 1
        if keys[pygame.K_DOWN]:
            shoot_y += 1
        
        # Only shoot if an arrow key is pressed
        if shoot_x != 0 or shoot_y != 0:
            # Normalize diagonal shooting
            if shoot_x != 0 and shoot_y != 0:
                shoot_x *= 0.707
                shoot_y *= 0.707
            
            # Get bullet speed from config
            bullet_speed = config.get('player', 'bullet_speed')
            
            # Normal shot - center bullet
            bullet = Bullet(self.rect.centerx, self.rect.centery, shoot_x * bullet_speed, shoot_y * bullet_speed, (255, 255, 0), is_enemy=False)
            bullets.append(bullet)
            
            # Determine sound effect
            should_play_sound = False
            sound_name = None
            
            # Triple shot when powered up
            if self.powered_up:
                # Calculate perpendicular direction for spread
                perp_x = -shoot_y
                perp_y = shoot_x
                
                # Left bullet (offset perpendicular to shoot direction)
                offset = 15
                left_bullet = Bullet(
                    self.rect.centerx + perp_x * offset,
                    self.rect.centery + perp_y * offset,
                    shoot_x * bullet_speed,
                    shoot_y * bullet_speed,
                    (255, 255, 100),  # Slightly different color when powered
                    is_enemy=False
                )
                bullets.append(left_bullet)
                
                # Right bullet
                right_bullet = Bullet(
                    self.rect.centerx - perp_x * offset,
                    self.rect.centery - perp_y * offset,
                    shoot_x * bullet_speed,
                    shoot_y * bullet_speed,
                    (255, 255, 100),
                    is_enemy=False
                )
                bullets.append(right_bullet)
                
                # Play super_shoot sound every 3 shots to match normal frequency
                self.shoot_sound_counter += 1
                if self.shoot_sound_counter >= self.sound_effect_interval:
                    should_play_sound = True
                    sound_name = 'super_shoot'
                    self.shoot_sound_counter = 0
            else:
                # Normal state: always play shoot sound
                should_play_sound = True
                sound_name = 'shoot'
            
            self.shoot_cooldown = self.shoot_delay
            return bullets, should_play_sound, sound_name
        
        return [], False, None
    
    def activate_powerup(self, duration_seconds):
        """Activate power-up mode with triple shot and increased fire rate"""
        fps = config.get('game', 'fps')
        fire_rate_multiplier = config.get('powerup', 'fire_rate_multiplier')
        
        self.powered_up = True
        self.powerup_timer = duration_seconds * fps
        self.shoot_delay = self.base_shoot_delay // fire_rate_multiplier
    
    def deactivate_powerup(self):
        """Deactivate power-up mode and restore normal fire rate"""
        self.powered_up = False
        self.powerup_timer = 0
        self.shoot_delay = self.base_shoot_delay
    
    def take_damage(self, damage):
        """Reduce player health with invincibility period
        Returns True if player dies, False otherwise
        """
        # Cannot take damage during invincibility
        if self.invincible:
            return False
        
        # Apply damage
        self.health -= damage
        
        # Activate invincibility after taking damage
        if self.health > 0:
            self.invincible = True
            self.invincible_timer = self.invincible_duration
        
        return self.health <= 0


class Enemy(pygame.sprite.Sprite):
    """Enemy character class - Circle type (slow, common)"""
    
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create enemy surface with transparency
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.draw_circle_enemy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Circle enemy stats from config
        self.speed = config.get('enemy_circle', 'speed')
        self.health = config.get('enemy_circle', 'health')
        self.shoot_cooldown = random.randint(
            config.get('enemy_circle', 'shoot_cooldown_min'),
            config.get('enemy_circle', 'shoot_cooldown_max')
        )
        self.enemy_type = "circle"
    
    def draw_circle_enemy(self):
        """Draw circle enemy in retro space game style"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (20, 20)
        
        # Main body - solid red circle
        pygame.draw.circle(self.image, (220, 0, 0), center, 16)
        
        # Darker inner ring (depth)
        pygame.draw.circle(self.image, (150, 0, 0), center, 12)
        
        # Central core panel (darker red square)
        pygame.draw.rect(self.image, (180, 0, 0), (14, 14, 12, 12))
        
        # Center energy indicator (small yellow square)
        pygame.draw.rect(self.image, (255, 200, 0), (17, 17, 6, 6))
        
        # Four directional panels (retro sci-fi details)
        panel_color = (100, 0, 0)
        pygame.draw.rect(self.image, panel_color, (18, 8, 4, 4))   # Top
        pygame.draw.rect(self.image, panel_color, (18, 28, 4, 4))  # Bottom
        pygame.draw.rect(self.image, panel_color, (8, 18, 4, 4))   # Left
        pygame.draw.rect(self.image, panel_color, (28, 18, 4, 4))  # Right
        
        # Small accent lights on panels (orange dots)
        pygame.draw.circle(self.image, (255, 150, 0), (20, 10), 1)
        pygame.draw.circle(self.image, (255, 150, 0), (20, 30), 1)
        pygame.draw.circle(self.image, (255, 150, 0), (10, 20), 1)
        pygame.draw.circle(self.image, (255, 150, 0), (30, 20), 1)
        
        # Outer ring highlight (retro glow effect)
        pygame.draw.circle(self.image, (255, 100, 100), center, 16, width=2)
        
        # Inner highlight ring
        pygame.draw.circle(self.image, (255, 50, 50), center, 12, width=1)
        
    def update(self, player_pos):
        """Move enemy toward player and handle shooting"""
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and move toward player
            dx = dx / distance
            dy = dy / distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def should_shoot(self):
        """Check if enemy should shoot"""
        return self.shoot_cooldown <= 0
    
    def shoot(self, player_pos):
        """Shoot bullet toward player"""
        if not self.should_shoot():
            return None
        
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction and apply bullet speed from config
            bullet_speed = config.get('enemy_circle', 'bullet_speed')
            dx = dx / distance * bullet_speed
            dy = dy / distance * bullet_speed
            
            # Reset cooldown from config
            self.shoot_cooldown = random.randint(
                config.get('enemy_circle', 'shoot_cooldown_min'),
                config.get('enemy_circle', 'shoot_cooldown_max')
            )
            return Bullet(self.rect.centerx, self.rect.centery, dx, dy, (255, 100, 100), is_enemy=True)
        
        return None
    
    def take_damage(self, damage):
        """Reduce enemy health"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False


class TriangleEnemy(pygame.sprite.Sprite):
    """Triangle Enemy - Fast and aggressive"""
    
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create triangle enemy surface
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
        self.draw_triangle_enemy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Triangle enemy stats from config
        self.speed = config.get('enemy_triangle', 'speed')
        self.health = config.get('enemy_triangle', 'health')
        self.shoot_cooldown = random.randint(
            config.get('enemy_triangle', 'shoot_cooldown_min'),
            config.get('enemy_triangle', 'shoot_cooldown_max')
        )
        self.enemy_type = "triangle"
    
    def draw_triangle_enemy(self):
        """Draw triangle enemy in retro space game style"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        # Triangle points (pointing down for aggressive look)
        points = [
            (18, 6),   # Top center
            (6, 28),   # Bottom left
            (30, 28)   # Bottom right
        ]
        
        # Main body - solid purple/magenta triangle
        pygame.draw.polygon(self.image, (200, 0, 200), points)
        
        # Inner triangle (darker purple for depth)
        inner_points = [
            (18, 12),
            (12, 24),
            (24, 24)
        ]
        pygame.draw.polygon(self.image, (140, 0, 140), inner_points)
        
        # Core triangle (very dark)
        core_points = [
            (18, 16),
            (15, 22),
            (21, 22)
        ]
        pygame.draw.polygon(self.image, (100, 0, 100), core_points)
        
        # Energy core (yellow center)
        pygame.draw.circle(self.image, (255, 255, 0), (18, 20), 3)
        pygame.draw.circle(self.image, (255, 255, 200), (18, 20), 1)
        
        # Three corner lights (cyan accents)
        pygame.draw.circle(self.image, (0, 255, 255), (18, 8), 2)   # Top
        pygame.draw.circle(self.image, (0, 255, 255), (8, 27), 2)   # Bottom left
        pygame.draw.circle(self.image, (0, 255, 255), (28, 27), 2)  # Bottom right
        
        # Outline for definition
        pygame.draw.polygon(self.image, (255, 100, 255), points, width=2)
        
        # Edge highlights (aggressive look)
        pygame.draw.line(self.image, (255, 150, 255), (18, 6), (6, 28), 1)
        pygame.draw.line(self.image, (255, 150, 255), (18, 6), (30, 28), 1)
    
    def update(self, player_pos):
        """Move triangle enemy toward player (same as circle enemy)"""
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and move toward player
            dx = dx / distance
            dy = dy / distance
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def should_shoot(self):
        """Check if enemy should shoot"""
        return self.shoot_cooldown <= 0
    
    def shoot(self, player_pos):
        """Shoot bullet toward player"""
        if not self.should_shoot():
            return None
        
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction and apply bullet speed from config
            bullet_speed = config.get('enemy_triangle', 'bullet_speed')
            dx = dx / distance * bullet_speed
            dy = dy / distance * bullet_speed
            
            # Reset cooldown from config
            self.shoot_cooldown = random.randint(
                config.get('enemy_triangle', 'shoot_cooldown_min'),
                config.get('enemy_triangle', 'shoot_cooldown_max')
            )
            return Bullet(self.rect.centerx, self.rect.centery, dx, dy, (255, 100, 255), is_enemy=True)
        
        return None
    
    def take_damage(self, damage):
        """Reduce enemy health"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    """Bullet class"""
    
    def __init__(self, x, y, speed_x, speed_y, color=(255, 255, 0), is_enemy=False):
        super().__init__()
        
        # Create bullet surface with transparency and glow
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        self.is_enemy = is_enemy
        self.draw_bullet(color, is_enemy)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def draw_bullet(self, color, is_enemy):
        """Draw bullet in retro space game style - simple with clean glow"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (6, 6)
        
        if is_enemy:
            # Enemy bullet - red/orange retro style
            # Outer glow ring
            pygame.draw.circle(self.image, (255, 100, 0, 80), center, 6)
            pygame.draw.circle(self.image, (255, 50, 0, 120), center, 5)
            
            # Main body - solid red
            pygame.draw.circle(self.image, (255, 30, 30), center, 4)
            
            # Inner bright core
            pygame.draw.circle(self.image, (255, 150, 100), center, 2)
            
            # Center pixel highlight
            pygame.draw.circle(self.image, (255, 255, 200), center, 1)
            
        else:
            # Player bullet - cyan/white retro style
            # Outer glow ring
            pygame.draw.circle(self.image, (0, 255, 255, 100), center, 6)
            pygame.draw.circle(self.image, (100, 255, 255, 150), center, 5)
            
            # Main body - bright cyan
            pygame.draw.circle(self.image, (100, 255, 255), center, 4)
            
            # Inner bright core
            pygame.draw.circle(self.image, (200, 255, 255), center, 2)
            
            # Center pixel highlight (pure white)
            pygame.draw.circle(self.image, (255, 255, 255), center, 1)
        
    def update(self, screen_width, screen_height):
        """Move bullet"""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > screen_width or
            self.rect.bottom < 0 or self.rect.top > screen_height):
            self.kill()


class HealthPack(pygame.sprite.Sprite):
    """Health pack pickup - restores 1 health"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Create health pack surface
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.draw_health_pack()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Health pack properties from config
        self.heal_amount = config.get('health_pack', 'heal_amount')
        
        # Slow drift downward
        self.speed_y = config.get('health_pack', 'drift_speed')
        
        # Lifetime timer from config
        lifetime_seconds = config.get('health_pack', 'lifetime_seconds')
        fps = config.get('game', 'fps')
        self.lifetime = lifetime_seconds * fps
        
        # Animation for pulsing effect
        self.pulse_timer = 0
        self.pulse_interval = config.get('health_pack', 'pulse_interval')
    
    def draw_health_pack(self):
        """Draw health pack in retro style - medical cross"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (12, 12)
        
        # Outer glow (green)
        for i in range(3, 0, -1):
            alpha = 60 * (i / 3.0)
            pygame.draw.circle(self.image, (0, 255, 0, int(alpha)), center, 12 + i*2)
        
        # Main circle background (white)
        pygame.draw.circle(self.image, (255, 255, 255), center, 10)
        
        # Red cross (medical symbol)
        # Horizontal bar
        pygame.draw.rect(self.image, (255, 0, 0), (6, 10, 12, 4))
        # Vertical bar
        pygame.draw.rect(self.image, (255, 0, 0), (10, 6, 4, 12))
        
        # White highlights on cross
        pygame.draw.rect(self.image, (255, 200, 200), (7, 11, 10, 1))
        pygame.draw.rect(self.image, (255, 200, 200), (11, 7, 1, 10))
        
        # Outer circle border
        pygame.draw.circle(self.image, (0, 200, 0), center, 10, width=2)
    
    def update(self):
        """Move health pack slowly downward and handle lifetime"""
        self.rect.y += self.speed_y
        self.lifetime -= 1
        self.pulse_timer += 1
        
        # Pulse animation using config interval
        half_interval = self.pulse_interval // 2
        if self.pulse_timer % self.pulse_interval < half_interval:
            # Redraw with brighter glow during pulse
            self.draw_health_pack_pulse()
        else:
            self.draw_health_pack()
        
        # Remove if expired
        if self.lifetime <= 0:
            self.kill()
    
    def draw_health_pack_pulse(self):
        """Draw health pack with enhanced glow during pulse"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (12, 12)
        
        # Brighter outer glow during pulse
        for i in range(4, 0, -1):
            alpha = 80 * (i / 4.0)
            pygame.draw.circle(self.image, (0, 255, 100, int(alpha)), center, 12 + i*3)
        
        # Main circle background (white)
        pygame.draw.circle(self.image, (255, 255, 255), center, 10)
        
        # Red cross (medical symbol)
        pygame.draw.rect(self.image, (255, 0, 0), (6, 10, 12, 4))
        pygame.draw.rect(self.image, (255, 0, 0), (10, 6, 4, 12))
        
        # White highlights on cross
        pygame.draw.rect(self.image, (255, 200, 200), (7, 11, 10, 1))
        pygame.draw.rect(self.image, (255, 200, 200), (11, 7, 1, 10))
        
        # Brighter outer circle border
        pygame.draw.circle(self.image, (100, 255, 100), center, 10, width=2)


class PowerUp(pygame.sprite.Sprite):
    """Power-up item that gives player triple shot and increased fire rate"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Create powerup surface with transparency
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        self.draw_powerup()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Power-up properties from config
        self.duration = config.get('powerup', 'duration_seconds')
        
        # Slow drift downward
        self.speed_y = config.get('powerup', 'drift_speed')
        
        # Lifetime timer from config
        lifetime_seconds = config.get('powerup', 'lifetime_seconds')
        fps = config.get('game', 'fps')
        self.lifetime = lifetime_seconds * fps
        
        # Animation for pulsing effect
        self.pulse_timer = 0
        self.pulse_interval = config.get('powerup', 'pulse_interval')
    
    def draw_powerup(self):
        """Draw power-up in retro style - lightning bolt / star"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (14, 14)
        
        # Outer glow (golden/yellow)
        for i in range(3, 0, -1):
            alpha = 70 * (i / 3.0)
            pygame.draw.circle(self.image, (255, 200, 0, int(alpha)), center, 14 + i*2)
        
        # Main star shape (8-pointed star for power-up)
        star_color = (255, 215, 0)  # Gold color
        
        # Draw diamond shape (rotated square)
        diamond_points = [
            (14, 4),   # Top
            (24, 14),  # Right
            (14, 24),  # Bottom
            (4, 14)    # Left
        ]
        pygame.draw.polygon(self.image, star_color, diamond_points)
        
        # Draw smaller diamond on top (rotated)
        small_diamond = [
            (14, 8),   # Top
            (20, 14),  # Right
            (14, 20),  # Bottom
            (8, 14)    # Left
        ]
        pygame.draw.polygon(self.image, (255, 255, 100), small_diamond)
        
        # Center energy core (bright white)
        pygame.draw.circle(self.image, (255, 255, 255), center, 4)
        
        # Add small accent points (4 corners)
        accent_color = (255, 150, 0)
        pygame.draw.circle(self.image, accent_color, (14, 4), 2)
        pygame.draw.circle(self.image, accent_color, (24, 14), 2)
        pygame.draw.circle(self.image, accent_color, (14, 24), 2)
        pygame.draw.circle(self.image, accent_color, (4, 14), 2)
        
        # Outer glow ring
        pygame.draw.circle(self.image, (255, 200, 0), center, 12, width=2)
    
    def update(self):
        """Move power-up slowly downward and handle lifetime"""
        self.rect.y += self.speed_y
        self.lifetime -= 1
        self.pulse_timer += 1
        
        # Pulse animation using config interval
        half_interval = self.pulse_interval // 2
        if self.pulse_timer % self.pulse_interval < half_interval:
            # Redraw with brighter glow during pulse
            self.draw_powerup_pulse()
        else:
            self.draw_powerup()
        
        # Remove if expired
        if self.lifetime <= 0:
            self.kill()
    
    def draw_powerup_pulse(self):
        """Draw power-up with enhanced glow during pulse"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
        center = (14, 14)
        
        # Brighter outer glow during pulse
        for i in range(4, 0, -1):
            alpha = 90 * (i / 4.0)
            pygame.draw.circle(self.image, (255, 220, 0, int(alpha)), center, 14 + i*3)
        
        # Main star shape (8-pointed star)
        star_color = (255, 230, 0)  # Brighter gold
        
        # Draw diamond shape
        diamond_points = [
            (14, 4),
            (24, 14),
            (14, 24),
            (4, 14)
        ]
        pygame.draw.polygon(self.image, star_color, diamond_points)
        
        # Draw smaller diamond
        small_diamond = [
            (14, 8),
            (20, 14),
            (14, 20),
            (8, 14)
        ]
        pygame.draw.polygon(self.image, (255, 255, 150), small_diamond)
        
        # Brighter center
        pygame.draw.circle(self.image, (255, 255, 255), center, 5)
        
        # Brighter accent points
        accent_color = (255, 180, 0)
        pygame.draw.circle(self.image, accent_color, (14, 4), 3)
        pygame.draw.circle(self.image, accent_color, (24, 14), 3)
        pygame.draw.circle(self.image, accent_color, (14, 24), 3)
        pygame.draw.circle(self.image, accent_color, (4, 14), 3)
        
        # Brighter outer ring
        pygame.draw.circle(self.image, (255, 230, 0), center, 12, width=2)
