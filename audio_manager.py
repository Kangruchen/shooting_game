"""
Audio Manager - Handles background music and sound effects
"""

import pygame
import os

class AudioManager:
    """Manages all audio in the game"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Volume settings (0.0 to 1.0)
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load sound effects (with error handling for missing files)
        self.load_sounds()
        
    def load_sounds(self):
        """Load all sound effects"""
        sound_files = {
            'shoot': 'assets/sounds/shoot.wav',
            'hit': 'assets/sounds/hit.wav',
            'enemy_shoot': 'assets/sounds/enemy_shoot.wav',
            'game_over': 'assets/sounds/game_over.wav',
            'menu_select': 'assets/sounds/menu_select.wav'
        }
        
        for name, filepath in sound_files.items():
            try:
                if os.path.exists(filepath):
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(self.sfx_volume)
                else:
                    # Create a placeholder silent sound if file doesn't exist
                    self.sounds[name] = None
            except Exception as e:
                print(f"Warning: Could not load sound '{name}': {e}")
                self.sounds[name] = None
    
    def play_music(self, music_file='assets/sounds/background_music.mp3', loops=-1):
        """Play background music (loops infinitely by default)"""
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                return True
            else:
                print(f"Warning: Music file '{music_file}' not found")
                return False
        except Exception as e:
            print(f"Warning: Could not play music: {e}")
            return False
    
    def restart_music(self, music_file='assets/sounds/background_music.mp3', loops=-1):
        """Restart music from the beginning"""
        self.stop_music()
        return self.play_music(music_file, loops)
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Warning: Could not play sound '{sound_name}': {e}")
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def toggle_music(self):
        """Toggle music on/off"""
        if pygame.mixer.music.get_busy():
            self.pause_music()
            return False
        else:
            self.resume_music()
            return True
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_music()
        pygame.mixer.quit()
