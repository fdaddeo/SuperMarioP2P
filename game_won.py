import arcade
import arcade.gui
from arcade.gui import UIManager
import os
import time
import menu as menu_file
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error

def database_connection(): 
    """ Connect to our MySQL database"""

    connection = None
    try:
        connection = mysql.connector.connect(host = "localhost", database = "super_mario", user = "root", password = "root")
        if connection.is_connected():
            print("Connected to MySQL database")

    except Error as e:
        print(e)

    return connection

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

JOIN_BTN_SCALE = 1.6

class WriteButton(arcade.gui.UIImageButton):
    def __init__(self, normal_texture, hover_texture, press_texture, center_x, center_y, input_box):
        super().__init__(normal_texture = normal_texture, hover_texture = hover_texture, press_texture = press_texture, center_x = center_x, center_y = center_y)
        self.input_box = input_box

        # Used to know if the button has been clicked
        self.clicked = False

    def on_click(self):
        """ This callback will be triggered if the button has been clicked """

        self.clicked = True

class GameWonView(arcade.View):
    """ View to show when game is over """

    def __init__(self, game_mode, total_time, lives_count):
        """ This is run once when we switch to this view """

        super().__init__()

        self.ui_manager = UIManager()

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Holds the game mode
        self.co_op = game_mode

        # Holds the lives counter
        self.lives_count = lives_count

        # Holds the game time
        self.total_time = total_time

        # Holds the ui_button
        self.write_btn = None

        # True if it is the first time that we click the button
        self.first_time = True

        # Holds the text for the input box label
        self.label = ""

        # Holds the ui_input_box
        self.ui_input_box = None

        # Holds the db connection
        self.database_connection = database_connection()
        self.cursor = self.database_connection.cursor()

        # Hold the records informations
        self.text_0 = ""
        self.text_1 = ""
        self.text_2 = ""
        self.text_3 = ""
        self.text_4 = ""

        # Holds the background
        self.background = None

        # Holds the tuples of the records contained in the file
        self.records = []

        # Game finished sound
        self.gameover_sound = arcade.load_sound("musica/smb_world_clear.wav")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
    
    def on_show(self):
        """ Called once when view is activated. """

        self.background = arcade.load_texture("Immagini/gameWon.png")
        time.sleep(0.3)
        arcade.play_sound(self.gameover_sound, 1)

    def on_show_view(self):
        """ Called once when view is activated. """

        self.setup()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_draw(self):
        """ Draw this view """

        arcade.start_render()

        # Draw the background
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        
        # Coordinates for drawing the input box
        y_slot = SCREEN_HEIGHT // 2
        left_column_x = SCREEN_WIDTH // 10

        # Draw the label for the input box
        self.label = "Your name here, use only three letters:"
        arcade.draw_text(self.label, left_column_x, y_slot + 20, arcade.csscolor.BLACK, 18, font_name = ('SHOWG'))

        # Draw the bottom text
        center_x = SCREEN_WIDTH // 2
        center_y = 20
        text = "Premi invio per tornare al menu"
        arcade.draw_text(text, center_x, center_y, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))

        # Draw our results
        center_y = SCREEN_HEIGHT - 140
        
        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        text = f"Your results:          time: {minutes:02d}:{seconds:02d}           lives left: {self.lives_count}"
        arcade.draw_text(text, center_x, center_y, arcade.color.BLACK, 16, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'), bold = True)

        # Draw the record text
        center_y = SCREEN_HEIGHT // 3
        arcade.draw_text(self.text_0, center_x, center_y, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))
        arcade.draw_text(self.text_1, center_x, center_y - 20, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))
        arcade.draw_text(self.text_2, center_x, center_y - 40, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))
        arcade.draw_text(self.text_3, center_x, center_y - 60, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))
        arcade.draw_text(self.text_4, center_x, center_y - 80, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center", font_name = ('SHOWG'))

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        self.ui_manager.purge_ui_elements()

        # Reset the records in memory
        self.records = []

        # Coordinates for drawing the input box
        y_slot = SCREEN_HEIGHT // 2
        left_column_x = SCREEN_WIDTH // 4
        right_column_x = 3 * SCREEN_WIDTH // 4

        # Draw the input box
        self.ui_input_box = arcade.gui.UIInputBox(center_x = left_column_x, center_y = y_slot, width = 300)
        self.ui_input_box.text = "Your name here"
        self.ui_input_box.cursor_index = len(self.ui_input_box.text)
        self.ui_manager.add_ui_element(self.ui_input_box)

        # Draw the button
        self.button_normal = arcade.load_texture('Immagini/RecordButton.png')
        self.hovered_texture = arcade.load_texture('Immagini/RecordButtonPressed.png')
        self.pressed_texture = arcade.load_texture('Immagini/RecordButtonPressed.png')
        self.write_btn = WriteButton(normal_texture = self.button_normal, hover_texture = self.hovered_texture, press_texture = self.pressed_texture, center_x = right_column_x, center_y = y_slot, input_box = self.ui_input_box)
        self.write_btn.scale = JOIN_BTN_SCALE
        self.ui_manager.add_ui_element(self.write_btn)

        # The game was in singleplayer
        if self.co_op == False:

            self.cursor.execute("SELECT * FROM singleplayer_record ORDER BY total_time ASC")
            table_records = self.cursor.fetchmany(5)

            for record in table_records:
                self.records.append(record)
        
        # The game was in multiplayer
        if self.co_op == True:

            self.cursor.execute("SELECT * FROM multiplayer_record ORDER BY total_time ASC")
            table_records = self.cursor.fetchall()

            for record in table_records:
                self.records.append(record)

        # Used to iterate only the first 5 records
        index = 0
        for tuples in self.records:
            # Calculate minutes
            minutes = int(tuples[2]) // 60

            # Calculate seconds by using a modulus (remainder)
            seconds = int(tuples[2]) % 60

            # Format the datestamp string
            date_string = tuples[4].strftime("%b-%d-%Y")

            # Setting the text for display the best 5 records
            if index == 0:
                self.text_0 = f"{tuples[1]}         {minutes:02d}:{seconds:02d}         {tuples[3]}         {date_string}"
            if index == 1:
                self.text_1 = f"{tuples[1]}         {minutes:02d}:{seconds:02d}         {tuples[3]}         {date_string}"
            if index == 2:
                self.text_2 = f"{tuples[1]}         {minutes:02d}:{seconds:02d}         {tuples[3]}         {date_string}"
            if index == 3:
                self.text_3 = f"{tuples[1]}         {minutes:02d}:{seconds:02d}         {tuples[3]}         {date_string}"
            if index == 4:
                self.text_4 = f"{tuples[1]}         {minutes:02d}:{seconds:02d}         {tuples[3]}         {date_string}"
            if index > 4:
                break

            index += 1

    def on_key_press(self, key, modifiers):
        """ If the user presses the mouse button, re-start the game. """

        if key == arcade.key.ENTER:
            # Close the connection with the db
            self.database_connection.close()
            print("Connection to MySQL database closed")

            # Load and set the menu view
            game_view = menu_file.MyMenu()
            game_view.setup()
            self.window.show_view(game_view)

    def on_update(self, delta_time):

        # Display only the first three letter of the name in the input box
        # otherwise delete the string inserted
        if len(self.ui_input_box.text) > 3:
            self.ui_input_box.text = ""

        # Insert the result achieved into the records file
        if self.write_btn.clicked == True and self.first_time == True and len(self.ui_input_box.text) == 3:
            # Getting the date
            timestamp = date.today()

            # The game was in singleplayer
            if self.co_op == False:
                insert_query = f"INSERT INTO singleplayer_record (player_name, total_time, lives, date_played) VALUES ('{self.ui_input_box.text}' , '{self.total_time}', '{self.lives_count}', '{timestamp}')"
                self.cursor.execute(insert_query)
                self.database_connection.commit()

                print(self.cursor.rowcount, "record inserted.")
            
            # The game was in multiplayer
            if self.co_op == True:
                insert_query = f"INSERT INTO multiplayer_record (player_name, total_time, lives, date_played) VALUES ('{self.ui_input_box.text}' , '{self.total_time}', '{self.lives_count}', '{timestamp}')"
                self.cursor.execute(insert_query)
                self.database_connection.commit()

                print(self.cursor.rowcount, "record inserted.")
            
            # Setting the button information
            self.first_time = False
            
            # Recall the setup in order to update our view
            self.setup()

        # Reset the button
        if self.write_btn.clicked == True:
            self.write_btn.clicked = False
