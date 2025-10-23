"""
Game Entities - Player, Enemy, Bullet classes
"""

import pygame
import random
import math

class Player(pygame.sprite.Sprite):
    """Player character class"""
    
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create player surface with transparency
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        self.draw_player()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = 5
        self.health = 3  # 3 lives
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # frames between shots
    
    def draw_player(self):
        """Draw player in retro space game style - simple square ship"""
        # Clear surface
        self.image.fill((0, 0, 0, 0))
        
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
    
    def shoot(self, keys):
        """Create bullets based on arrow key direction"""
        if self.shoot_cooldown > 0:
            return []
        
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
            
            bullet = Bullet(self.rect.centerx, self.rect.centery, shoot_x * 10, shoot_y * 10, (255, 255, 0), is_enemy=False)
            bullets.append(bullet)
            self.shoot_cooldown = self.shoot_delay
        
        return bullets
    
    def take_damage(self, damage):
        """Reduce player health"""
        self.health -= damage
        return self.health <= 0


class Enemy(pygame.sprite.Sprite):
    """Enemy character class"""
    
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create enemy surface with transparency
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.draw_enemy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = random.randint(1, 2)
        self.health = 30
        self.shoot_cooldown = random.randint(60, 180)  # Random shooting interval
    
    def draw_enemy(self):
        """Draw enemy in retro space game style - simple circle with details"""
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
            # Normalize direction
            dx = dx / distance * 5  # Bullet speed
            dy = dy / distance * 5
            
            self.shoot_cooldown = random.randint(60, 180)  # Reset cooldown
            return Bullet(self.rect.centerx, self.rect.centery, dx, dy, (255, 100, 100), is_enemy=True)
        
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
