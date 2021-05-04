import arcade
import arcade.gui
from arcade.gui import UIManager
import os
import sys
import time
import signal
import single_player as singleplayer_file
import ip_address as ipaddress_file
import ip_address_insert as ipaddressinsert_file

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
MUSIC_VOLUME = 0.7
SCREEN_TITLE = "Super Mario"

BTN_SCALE = 1.3
JOIN_BTN_SCALE = 1.6

class SinglePlayerButton(arcade.gui.UIImageButton):

    def __init__(self, normal_texture, hover_texture, press_texture, center_x, center_y, input_box = None):
        super().__init__(normal_texture = normal_texture, hover_texture = hover_texture, press_texture = press_texture, center_x = center_x, center_y = center_y)
        self.pressed = False

    def on_click(self):
        self.pressed = True

class MultiPlayerButton(arcade.gui.UIImageButton):
    def __init__(self, normal_texture, hover_texture, press_texture, center_x, center_y, input_box = None):
        super().__init__(normal_texture = normal_texture, hover_texture = hover_texture, press_texture = press_texture, center_x = center_x, center_y = center_y)
        self.pressed = False

    def on_click(self):
        self.pressed = True

class JoinSessionButton(arcade.gui.UIImageButton):
    def __init__(self, normal_texture, hover_texture, press_texture, center_x, center_y, input_box = None):
        super().__init__(normal_texture = normal_texture, hover_texture = hover_texture, press_texture = press_texture, center_x = center_x, center_y = center_y)
        self.pressed = False

    def on_click(self):
        self.pressed = True
            
class MyMenu(arcade.View):
    """
    Main application class.
    """
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.background = None

        # Variables used to manage our music. See setup() for giving them values.
        self.music_list = []
        self.current_song_index = 0
        self.current_music_player = None
        self.music = None

    def advance_song(self):
        """ Advance our pointer to the next song. This does NOT start the song. """
        
        self.current_song_index += 1
        if self.current_song_index >= len(self.music_list):
            self.current_song_index = 0
        print(f"Advancing song to {self.current_song_index}.")

    def play_song(self):
        """ Play the song. """

        # Play the next song
        print(f"Playing {self.music_list[self.current_song_index]}")
        self.music = arcade.Sound(self.music_list[self.current_song_index], streaming=True)
        self.current_music_player = self.music.play(MUSIC_VOLUME)
        # This is a quick delay. If we don't do this, our elapsed time is 0.0
        # and on_update will think the music is over and advance us to the next
        # song before starting this one.
        time.sleep(0.08)

    def on_show(self):
        """ Called once when view is activated. """
        self.background = arcade.load_texture("Immagini/sky.png")

    def on_show_view(self):
        # List of music
        self.music_list = ["musica/MenuMusic.mp3"]
        # Array index of what to play
        self.current_song_index = 0
        # Play the song
        self.play_song()

        self.ui_manager.purge_ui_elements()
        self.setup()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        self.button_normal = arcade.load_texture('Immagini/SinglePlayer.png')
        self.hovered_texture = arcade.load_texture('Immagini/SinglePlayerPressed.png')
        self.pressed_texture = arcade.load_texture('Immagini/SinglePlayerPressed.png')
        self.singleplayer_btn = SinglePlayerButton(normal_texture = self.button_normal, hover_texture = self.hovered_texture, press_texture = self.pressed_texture, center_x = 200, center_y = 300)
        self.singleplayer_btn.scale = BTN_SCALE
        self.ui_manager.add_ui_element(self.singleplayer_btn)

        self.button_normal = arcade.load_texture('Immagini/MultiPlayer.png')
        self.hovered_texture = arcade.load_texture('Immagini/MultiPlayerPressed.png')
        self.pressed_texture = arcade.load_texture('Immagini/MultiPlayerPressed.png')
        self.multiplayer_btn = MultiPlayerButton(normal_texture = self.button_normal, hover_texture = self.hovered_texture, press_texture = self.pressed_texture, center_x = 800, center_y = 300)
        self.multiplayer_btn.scale = BTN_SCALE
        self.ui_manager.add_ui_element(self.multiplayer_btn)

        self.button_normal = arcade.load_texture('Immagini/Join.png')
        self.hovered_texture = arcade.load_texture('Immagini/JoinPressed.png')
        self.pressed_texture = arcade.load_texture('Immagini/JoinPressed.png')
        self.join_btn = JoinSessionButton(normal_texture = self.button_normal, hover_texture = self.hovered_texture, press_texture = self.pressed_texture, center_x = 500, center_y = 100)
        self.join_btn.scale = JOIN_BTN_SCALE
        self.ui_manager.add_ui_element(self.join_btn)

    def on_update(self, delta_time):
        
        if self.singleplayer_btn.pressed == True:
            self.music.stop(self.current_music_player)
            game_view = singleplayer_file.MyGame()
            self.window.show_view(game_view)

        if self.multiplayer_btn.pressed == True:
            self.music.stop(self.current_music_player)
            ip_address_view = ipaddress_file.IPAdressWindow()
            self.window.show_view(ip_address_view)

        if self.join_btn.pressed == True:
            self.music.stop(self.current_music_player)
            ip_address_view = ipaddressinsert_file.IPAdressWindow()
            self.window.show_view(ip_address_view)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MyMenu()
    window.show_view(menu_view)
    # start the arcade loop
    try:
        arcade.run()
    except KeyboardInterrupt:
        # we are outta here!
        sys.exit(0)

# signal handler function called when Control-C occurs
# noinspection PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print("Exiting Through Signal Handler")
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    main()