import arcade
import os
import time
import menu as menu_file

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

class GameOverView(arcade.View):
    """ View to show when game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.background = None

        self.gameover_sound = arcade.load_sound("musica/smb_gameover.wav")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
    
    def on_show(self):
        """ Called once when view is activated. """
        self.background = arcade.load_texture("Immagini/gameOver.png")
        time.sleep(0.3)
        arcade.play_sound(self.gameover_sound, 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 3
        text = "Premi invio per tornare al menu"
        arcade.draw_text(text, center_x, center_y, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))

    def on_key_press(self, key, modifiers):
        """ If the user presses the mouse button, re-start the game. """

        if key == arcade.key.ENTER:
            game_view = menu_file.MyMenu()
            game_view.setup()
            self.window.show_view(game_view)