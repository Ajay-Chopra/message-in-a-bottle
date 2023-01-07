import pygame
import sys
import argparse
from util.settings import (
    WIDTH,
    HEIGTH,
    INITIAL_PLAYER_DATA,
    FPS
)
from level import Level
from title_screen.title import Title
from intro.intro_screen import IntroScreen
from audio.audio import AudioPlayer
from util.models import PlayerStats

class Game:
    """
    High level class responsible for transfering between levels
    and running the pygame loop
    """

    def __init__(self, start_level=None, with_music=False, with_sound_fx=False, debug=False):
        # setting up pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        pygame.display.set_caption("Message in a Bottle")
        self.clock = pygame.time.Clock()

        self.audio_player = AudioPlayer(with_music, with_sound_fx)

        self.player_data = INITIAL_PLAYER_DATA

        self.levels = ["Title", "Intro", "1", "2", "3"]
        self.current_level_index = start_level if start_level is not None else 0
        if self.current_level_index == 0:
            self.level = Title(self.advance_to_next_level, self.resume_game, self.audio_player)
        elif self.current_level_index == 1:
            self.level = IntroScreen(self.advance_to_next_level)
        else:
            self.level = Level(
                self.levels[self.current_level_index],
                self.advance_to_next_level,
                self.restart_level,
                self.return_to_title_page,
                self.audio_player,
                self.player_data
            )
    
    def advance_to_next_level(self, updated_player_data):
        """
        Advance the game to the next level and pass in 
        the updated player data
        """
        self.current_level_index += 1
        if self.current_level_index >= len(self.levels):
            sys.exit()
        
        if updated_player_data is not None:
            self.player_data = updated_player_data
        
        if self.current_level_index == 1:
            self.level = IntroScreen(self.advance_to_next_level)
        else:
            self.level = Level(
                self.levels[self.current_level_index],
                self.advance_to_next_level,
                self.restart_level,
                self.return_to_title_page,
                self.audio_player,
                self.player_data
            )
    
    def restart_level(self):
        """
        Restart the current level
        """
        self.level = Level(
                self.levels[self.current_level_index],
                self.advance_to_next_level,
                self.restart_level,
                self.return_to_title_page,
                self.audio_player,
                self.player_data
            )
    
    def resume_game(self, game_data):
        """
        Resume a previously exited game based on data
        loaded in from file
        """
        self.load_game_data(game_data)
        self.restart_level()
    
    def load_game_data(self, game_data):
        """
        Take data from game_data dict and put it in
        format usable by Level class
        """
        self.player_data = PlayerStats(**game_data["player_data"])
        self.current_level_index = int(game_data["level_number"]) + 1
    
    def return_to_title_page(self):
        """
        Returns user to main title page after they save/exit a current game
        """
        self.current_level_index = 0
        self.level = Title(self.advance_to_next_level, self.resume_game, self.audio_player)
    
    def run(self):
        """
        Run the pygame loop to run the game
        """
        self.audio_player.play_song(0)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill('black')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", help="Level index to start from", type=int)
    parser.add_argument("--music", help="Play game with music", action="store_true")
    parser.add_argument("--soundfx", help="Play this game with sound effects", action="store_true")
    parser.add_argument("--debug", help="Run the game with debug logging to the console", action="store_true")
    args = parser.parse_args()

    game = Game(args.level, args.music, args.soundfx, args.debug)
    game.run()
