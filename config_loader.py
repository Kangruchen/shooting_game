"""
Configuration loader for the shooting game.
Loads game parameters from config.json file.
"""

import json
import os

class Config:
    """Singleton class to load and access game configuration"""
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance
    
    def load_config(self):
        """Load configuration from config.json"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print("Configuration loaded successfully!")
        except FileNotFoundError:
            print(f"Warning: config.json not found at {config_path}")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing config.json: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration if file is not found or invalid"""
        return {
            "player": {
                "max_health": 3,
                "speed": 5,
                "shoot_cooldown": 10,
                "bullet_speed": 7
            },
            "enemy_circle": {
                "health": 30,
                "speed": 1,
                "shoot_cooldown_min": 120,
                "shoot_cooldown_max": 240,
                "bullet_speed": 3,
                "points": 10,
                "spawn_weight": 0.75,
                "health_pack_drop_chance": 0.05
            },
            "enemy_triangle": {
                "health": 20,
                "speed": 3,
                "shoot_cooldown_min": 30,
                "shoot_cooldown_max": 60,
                "bullet_speed": 4,
                "points": 20,
                "spawn_weight": 0.25,
                "health_pack_drop_chance": 0.1
            },
            "health_pack": {
                "heal_amount": 1,
                "drift_speed": 0.5,
                "lifetime_seconds": 10,
                "pulse_interval": 30
            },
            "difficulty": {
                "level_up_interval_seconds": 20,
                "initial_spawn_delay": 90,
                "min_spawn_delay": 30,
                "spawn_delay_decrease": 10
            },
            "game": {
                "screen_width": 800,
                "screen_height": 600,
                "fps": 60,
                "background_color": [20, 20, 40],
                "star_count": 100
            }
        }
    
    def get(self, *keys):
        """Get configuration value using dot notation
        
        Example: config.get('player', 'max_health')
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def reload(self):
        """Reload configuration from file"""
        self.load_config()


# Global configuration instance
config = Config()
