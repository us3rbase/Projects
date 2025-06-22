import pygame
import sys
import os
import random
import math
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info
from Dialog import dialog_create, boss_fight_intro

class Attack:
    def __init__(self, x, y, speed=3, pattern="linear", speed_x=None, speed_y=None):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 15
        self.speed = speed
        self.pattern = pattern
        self.is_active = True
        self.start_x = x
        self.start_time = pygame.time.get_ticks()
        self.color = (255, 0, 0)  # Red attack projectile
        self.speed_x = speed_x if speed_x is not None else 0
        self.speed_y = speed_y if speed_y is not None else speed
        
    def update(self):
        """Update attack position based on pattern"""
        if self.pattern == "linear":
            self.x += self.speed_x
            self.y += self.speed_y
        elif self.pattern == "sine":
            time_elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
            self.x = self.start_x + math.sin(time_elapsed * 5) * 50 + (self.speed_x * time_elapsed)
            self.y += self.speed_y
        elif self.pattern == "zigzag":
            time_elapsed = (pygame.time.get_ticks() - self.start_time) / 200.0
            offset = 30 if int(time_elapsed) % 2 == 0 else -30
            self.x += offset * 0.1 + self.speed_x
            self.y += self.speed_y
            
        # Check if attack is off screen
        if self.y > 500:  # Just beyond screen height
            self.is_active = False
            
    def draw(self, screen):
        """Draw the attack"""
        if not self.is_active:
            return
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, width=60, height=60):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = 50
        self.is_active = True
        self.attack_timer = 0
        self.attack_cooldown = 90  # Frames between attacks (1.5 seconds at 60fps)
        self.attacks = []
        self.attack_patterns = ["linear", "sine", "zigzag"]
        self.attack_window_active = False
        self.attack_window_timer = 0
        self.attack_window_duration = 45  # 0.75 seconds at 60fps
        self.attack_count = random.randint(1, 4)  # Random number of attacks between windows
        self.current_attack_count = 0
        
        # Try to load the enemy image, fallback to a colored rectangle
        self.use_image = True
        try:
            self.image = pygame.image.load('virus.jpg')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            print("Could not load virus image. Using colored square instead.")
            self.use_image = False
            self.color = (255, 165, 0)  # Orange color for cookie grabbers
    
    def draw(self, screen):
        if not self.is_active:
            return
            
        if self.use_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = 5
        health_percentage = max(0, self.health / 50.0)
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x, self.y - 10, health_bar_width, health_bar_height))
        # Foreground (green)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x, self.y - 10, int(health_bar_width * health_percentage), health_bar_height))
        
        # Draw attack window indicator
        if self.attack_window_active:
            window_color = (0, 255, 0)  # Green when window is active
            window_percentage = self.attack_window_timer / self.attack_window_duration
            pygame.draw.rect(screen, (100, 100, 100), 
                           (self.x, self.y - 20, health_bar_width, health_bar_height))  # Background
            pygame.draw.rect(screen, window_color,
                           (self.x, self.y - 20, int(health_bar_width * window_percentage), health_bar_height))  # Foreground
    
    def update(self):
        """Update enemy state and create attacks"""
        if not self.is_active:
            return
            
        # Update attack window timer
        if self.attack_window_active:
            self.attack_window_timer -= 1
            if self.attack_window_timer <= 0:
                self.attack_window_active = False
                # Reset attack count for next sequence
                self.attack_count = random.randint(1, 4)
                self.current_attack_count = 0
            
        # Update attack timer
        self.attack_timer += 1
        if self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0
            self.create_attack()
            self.current_attack_count += 1
            
            # Only open attack window after completing the sequence
            if self.current_attack_count >= self.attack_count:
                self.attack_window_active = True
                self.attack_window_timer = self.attack_window_duration
            
        # Update existing attacks
        for attack in self.attacks[:]:
            attack.update()
            if not attack.is_active:
                self.attacks.remove(attack)
    
    def create_attack(self):
        """Create a new attack"""
        # Create 1-3 attacks in a pattern
        attack_count = random.randint(1, 3)
        pattern = random.choice(self.attack_patterns)
        
        for i in range(attack_count):
            # Random x position across the fight box
            min_x = 205  # fight_box_left
            max_x = 496  # fight_box_right
            attack_x = random.randint(min_x, max_x)
            attack_y = self.y + self.height
            
            self.attacks.append(Attack(attack_x, attack_y, pattern=pattern))
    
    def draw_attacks(self, screen):
        """Draw all active attacks"""
        for attack in self.attacks:
            attack.draw(screen)
    
    def take_damage(self, amount):
        """Reduce enemy health by the given amount"""
        self.health -= amount
        if self.health <= 0:
            self.is_active = False
            self.attacks.clear()  # Clear all attacks when enemy dies
            return True  # Enemy is defeated
        return False  # Enemy is still active
    
    def can_be_attacked(self):
        """Check if the enemy can be attacked (attack window is active)"""
        return self.attack_window_active

class Boss(Enemy):
    def __init__(self, x, y, width=80, height=80):
        super().__init__(x, y, width, height)
        self.health = 100  # Boss has more health (2x regular enemy)
        self.attack_cooldown = 60  # Faster attacks
        self.attack_window_duration = 30  # Shorter attack window
        self.attack_patterns = ["linear", "sine", "zigzag", "spiral", "chaos"]  # Added chaos pattern
        self.color = (128, 0, 128)  # Purple color for trojan viruses
        self.chaos_attack_chance = 0.2  # 20% chance for chaos attack
        
        # Load spinner animation
        try:
            self.image = pygame.image.load('Spinner-Virus-Idle.gif')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.use_image = True
        except pygame.error:
            print("Could not load boss image. Using colored square instead.")
            self.use_image = False
        
    def create_attack(self):
        """Create a new attack with boss-specific patterns"""
        # Random chance for multiple attack sequences
        if random.random() < 0.15:  # 15% chance for double attack
            self.create_attack_sequence()
            self.create_attack_sequence()
        else:
            self.create_attack_sequence()
    
    def create_attack_sequence(self):
        """Create a single attack sequence"""
        attack_count = random.randint(2, 4)  # More attacks
        pattern = random.choice(self.attack_patterns)
        
        if pattern == "chaos" or random.random() < self.chaos_attack_chance:
            # Create chaotic attacks with random velocities
            for i in range(attack_count):
                min_x = 205  # fight_box_left
                max_x = 496  # fight_box_right
                attack_x = random.randint(min_x, max_x)
                attack_y = self.y + self.height
                
                # Random velocity components
                speed_x = random.uniform(-2, 2)
                speed_y = random.uniform(2, 4)  # Always move downward
                
                self.attacks.append(ChaosAttack(attack_x, attack_y, speed_x, speed_y))
        elif pattern == "spiral":
            # Create a spiral pattern with random positions and velocities
            for i in range(attack_count):
                angle = (i * 45) % 360  # 45 degrees between each attack
                base_speed = random.uniform(2, 4)
                speed_x = math.cos(math.radians(angle)) * base_speed
                speed_y = math.sin(math.radians(angle)) * base_speed
                
                # Random starting position
                min_x = 205
                max_x = 496
                attack_x = random.randint(min_x, max_x)
                attack_y = self.y + self.height
                
                self.attacks.append(SpiralAttack(attack_x, attack_y, speed_x, speed_y))
        else:
            # Create attacks with random positions and velocities
            for i in range(attack_count):
                min_x = 205
                max_x = 496
                attack_x = random.randint(min_x, max_x)
                attack_y = self.y + self.height
                
                # Random velocity for regular attacks
                speed_x = random.uniform(-1, 1)
                speed_y = random.uniform(2, 3)
                
                self.attacks.append(Attack(attack_x, attack_y, pattern=pattern, speed_x=speed_x, speed_y=speed_y))

class SpiralAttack(Attack):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__(x, y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = (255, 100, 100)  # Lighter red for spiral attacks
        
    def update(self):
        """Update spiral attack position"""
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Check if attack is off screen
        if self.y > 500 or self.x < 0 or self.x > 800:
            self.is_active = False

class ChaosAttack(Attack):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__(x, y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = (255, 50, 50)  # Bright red for chaos attacks
        
    def update(self):
        """Update chaos attack position with random movement"""
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Add slight random movement
        self.speed_x += random.uniform(-0.1, 0.1)
        self.speed_y += random.uniform(-0.1, 0.1)
        
        # Keep speed within reasonable bounds
        self.speed_x = max(min(self.speed_x, 3), -3)
        self.speed_y = max(min(self.speed_y, 4), 1)  # Always move downward
        
        # Check if attack is off screen
        if self.y > 500 or self.x < 0 or self.x > 800:
            self.is_active = False

class EnemyManager:
    def __init__(self, screen_width, screen_height):
        self.enemies = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fight_box_top = 227
        self.fight_box_bottom = 393
        self.fight_box_left = 205
        self.fight_box_right = 496
        self.enemy_spawn_y = 120
        self.boss_spawn_timer = None
        self.is_boss_fight = False
        self.enemy_spawned = False
    
    def spawn_enemy(self, count=1, is_boss=False):
        """Spawn a specified number of enemies or a boss"""
        center_x = self.screen_width / 2
        
        if is_boss:
            x = center_x - 40  # Half of boss width (80)
            y = self.enemy_spawn_y
            self.enemies.append(Boss(x, y))
            self.is_boss_fight = True
        else:
            if count == 1:
                x = center_x - 30
                y = self.enemy_spawn_y
                self.enemies.append(Enemy(x, y))
            else:
                total_width = count * 60 + (count - 1) * 20
                start_x = center_x - total_width / 2
                
                for i in range(count):
                    x = start_x + i * (60 + 20)
                    y = self.enemy_spawn_y
                    self.enemies.append(Enemy(x, y))
    
    def start_boss_fight(self):
        """Start the boss fight sequence"""
        return boss_fight_intro()
    
    def draw_enemies(self, screen):
        """Draw all active enemies and their attacks"""
        for enemy in self.enemies:
            enemy.draw(screen)
            enemy.draw_attacks(screen)
    
    def update_enemies(self):
        """Update all enemies"""
        if self.boss_spawn_timer and pygame.time.get_ticks() >= self.boss_spawn_timer:
            self.spawn_enemy(is_boss=True)
            self.boss_spawn_timer = None
        
        for enemy in self.enemies:
            if enemy.is_active:
                enemy.update()
    
    def check_attack_collisions(self, player_x, player_y, player_width, player_height):
        """Check if any enemy attack collides with the player"""
        for enemy in self.enemies:
            for attack in enemy.attacks:
                if not attack.is_active:
                    continue
                    
                # Simple rectangle collision detection
                if (player_x < attack.x + attack.width and
                    player_x + player_width > attack.x and
                    player_y < attack.y + attack.height and
                    player_y + player_height > attack.y):
                    attack.is_active = False  # Remove the attack
                    return True  # Collision detected
        return False  # No collision
    
    def player_attack(self, damage=10):
        """Player attacks and damages all active enemies"""
        defeated_count = 0
        for enemy in self.enemies:
            if enemy.is_active and enemy.can_be_attacked():
                if enemy.take_damage(damage):
                    defeated_count += 1
        
        return defeated_count
    
    def count_active_enemies(self):
        """Count how many active enemies are remaining"""
        return sum(1 for enemy in self.enemies if enemy.is_active)
    
    def clear_enemies(self):
        """Remove all enemies"""
        self.enemies.clear()

def start_fight_scene():
    """Start a fight scene with enemies"""
    dialog_create("Tut", "Look! There's a virus!", 3)
    # Return a timestamp that marks when the enemy should spawn
    # This timestamp will be after the first dialog message
    spawn_time = pygame.time.get_ticks() + 3000  # 3 seconds for the first message
    
    # Continue with the rest of the tutorial after spawning
    dialog_create("Tut", "Move with WASD to dodge its attacks!", 3)
    dialog_create("Tut", "After each attack sequence, there's a brief window where you can counter-attack!", 4)
    dialog_create("Tut", "Press SPACE during this window to attack!", 3)
    
    return spawn_time
