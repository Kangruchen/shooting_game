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
        
        # Create player surface
        self.image = pygame.Surface((50, 40))
        self.image.fill((0, 255, 0))  # Green player
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = 5
        self.health = 3  # 3 lives
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # frames between shots
        
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
        
        # Create enemy surface
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))  # Red enemy
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = random.randint(1, 2)
        self.health = 30
        self.shoot_cooldown = random.randint(60, 180)  # Random shooting interval
        
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
        
        # Create bullet surface
        self.image = pygame.Surface((8, 8))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.is_enemy = is_enemy
        
    def update(self, screen_width, screen_height):
        """Move bullet"""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Remove if off screen
        if (self.rect.right < 0 or self.rect.left > screen_width or
            self.rect.bottom < 0 or self.rect.top > screen_height):
            self.kill()
