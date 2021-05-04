import arcade
import os
import time
import threading
import signal
import sys
import subprocess
import psutil
import mysql.connector
from mysql.connector import Error
from python_banyan.banyan_base import BanyanBase
import GameOver as GameOver_file
import game_won as game_won_file

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
MUSIC_VOLUME = 0.2

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.5
TILE_SCALING = 1.5
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1.75
PLAYER_JUMP_SPEED = 21
PLAYER_START_X = 11
PLAYER_START_Y = 200
FIREBALL_SPEED = 6

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Used to check when the second player connects
player_ready = False

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

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally = True)
    ]

class PlayerCharacter(arcade.Sprite):
    """ Player Sprite """
    def __init__(self, in_control):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Used to know if we are in control of this sprite or not
        self.in_control = in_control

        # Used to know if the power up has been taken
        self.powerup = False
        self.powerup_start = None

        # Used to know if the player reached the door
        self.level_ended = False

        # Used to know if the player is alive
        self.death = False

        # Used to store the information about the death animation
        self.coffin_boundary_top = 819
        self.coffin_boundary_top_reached = False
        self.coffin_boundary_bottom = 284
        self.coffin_boundary_bottom_reached = True

        # Load textures for idle standing
        if self.in_control == True:
            self.idle_texture_pair = load_texture_pair("Immagini/guy1.png")
            self.jump_texture_pair = load_texture_pair("Immagini/guy2.png")
        
        if self.in_control == False:
            self.idle_texture_pair = load_texture_pair("Immagini/guy1R.png")
            self.jump_texture_pair = load_texture_pair("Immagini/guy2R.png")

        self.idle_texture_pair_powerup = load_texture_pair("Immagini/guy1OP.png")
        self.jump_texture_pair_powerup = load_texture_pair("Immagini/guy2OP.png")
        self.death_texture = arcade.load_texture("Immagini/tomb.png")

        # Load textures for walking
        self.walk_textures = []
        if self.in_control == True:
            texture = load_texture_pair("Immagini/guy2.png")
            self.walk_textures.append(texture)
            texture = load_texture_pair("Immagini/guy3.png")
            self.walk_textures.append(texture)
            texture = load_texture_pair("Immagini/guy4.png")
            self.walk_textures.append(texture)

        if self.in_control == False:
            texture = load_texture_pair("Immagini/guy2R.png")
            self.walk_textures.append(texture)
            texture = load_texture_pair("Immagini/guy3R.png")
            self.walk_textures.append(texture)
            texture = load_texture_pair("Immagini/guy4R.png")
            self.walk_textures.append(texture)

        # Load textures for walking when is powered up
        self.walk_textures_powerup = []
        texture = load_texture_pair("Immagini/guy2OP.png")
        self.walk_textures_powerup.append(texture)
        texture = load_texture_pair("Immagini/guy3OP.png")
        self.walk_textures_powerup.append(texture)
        texture = load_texture_pair("Immagini/guy4OP.png")
        self.walk_textures_powerup.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):
        # If the player is alive
        if self.death == False:
            # Figure out if we need to flip face left or right
            if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
                self.character_face_direction = LEFT_FACING
            elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
                self.character_face_direction = RIGHT_FACING

            # Jumping animation
            if self.change_y > 0:
                if self.powerup == False:
                    self.texture = self.jump_texture_pair[self.character_face_direction]
                else:
                    self.texture = self.jump_texture_pair_powerup[self.character_face_direction]
                return

            # Idle animation
            if self.change_x == 0:
                if self.powerup == False:
                    self.texture = self.idle_texture_pair[self.character_face_direction]
                else:
                    self.texture = self.idle_texture_pair_powerup[self.character_face_direction]
                return

            # Walking animation
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            if self.powerup == False:
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
            else:
                self.texture = self.walk_textures_powerup[self.cur_texture][self.character_face_direction]
        # Death animation
        else:
            self.cur_texture = 0
            self.texture = self.death_texture

            # Update and record the information about reaching the boundaries of the animation
            # Is going up
            if self.center_y < self.coffin_boundary_top and self.coffin_boundary_bottom_reached == True:
                self.coffin_boundary_top_reached = False
            # Have to go down
            if self.center_y >= self.coffin_boundary_top and self.coffin_boundary_bottom_reached == True:
                self.coffin_boundary_top_reached = True
                self.coffin_boundary_bottom_reached = False
            # Is going down
            if self.center_y > self.coffin_boundary_bottom and self.coffin_boundary_top_reached == True:
                self.coffin_boundary_bottom_reached = False
            # Have to go up
            if self.center_y <= self.coffin_boundary_bottom and self.coffin_boundary_top_reached == True:
                self.coffin_boundary_bottom_reached = True
                self.coffin_boundary_top_reached = False

            # Do the movement
            if self.coffin_boundary_bottom_reached == True and self.coffin_boundary_top_reached == False:
                self.center_y += 1
            if self.coffin_boundary_bottom_reached == False and self.coffin_boundary_top_reached == True:
                self.center_y -= 1
            
class Platform(arcade.Sprite):
    def __init__(self, x, y, max_left, max_right, speed):

        # Set up parent class
        super().__init__()

        self.center_x = x
        self.center_y = y
        self.boundary_left = max_left
        self.boundary_right = max_right
        self.change_x = speed
        self.scale = TILE_SCALING

        self.texture = arcade.load_texture(f"Immagini/Level4/platform.png")

class FireBall(arcade.Sprite):
    """ Fire ball Sprite """
    def __init__(self, x, y):

        # Set up parent class
        super().__init__()

        self.center_x = x
        self.center_y = y
        # change_x will be managed in key press function
        self.change_y = 0

        # Getting the starting point so after 10 blocks the fireball will disappear
        # That will manged in update function of MyGame class
        self.starting_x = x 

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.start_animation = False
        self.scale = TILE_SCALING

        # Set true when hits something
        self.exploded = False

        # Set true when the death animation is finished
        self.exploded_animation_finished = False

        # Index for image loading and counting
        index = 1

        # Load textures for walking
        self.animation_textures = []
        while index <= 4:
            texture = arcade.load_texture(f"Immagini/FireBall/FireBall{index}.png")
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            index += 1

        self.exploded_textures = []
        texture = arcade.load_texture("Immagini/FireBall/FireBallBang.png")
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)
        self.exploded_textures.append(texture)

        self.texture = self.animation_textures[0]

    def update_animation(self, delta_time: float = 1/60):
        if self.exploded == False:
            if self.start_animation == True:
                self.cur_texture += 1
                if self.cur_texture > 11:
                    self.cur_texture = 0
                self.texture = self.animation_textures[self.cur_texture]
        elif self.exploded == True:
            self.change_x = 0
            self.cur_texture = 0
            if self.cur_texture <= 9:
                self.texture = self.exploded_textures[self.cur_texture]
                self.cur_texture += 1
            self.cur_texture = 0
            self.exploded_animation_finished = True

class Powerup(arcade.Sprite):
    """ Powerup Sprite """
    def __init__(self, x, y):
        
        super().__init__()

        self.center_x = x
        self.center_y = y
        
        self.scale = TILE_SCALING

        self.texture = arcade.load_texture("Immagini/FireFlower.png")

        # Set true when taken by the player
        self.taken = False

class GoombaCharacter(arcade.Sprite):
    """ Goomba Sprite """
    def __init__(self, boundary_left, boundary_right, speed):

        super().__init__()
        
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.change_x = speed

        # Default to face-right
        self.character_face_direction = LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = TILE_SCALING

        # Set true when the goomba dies
        self.death = False

        # Set true when the death animation is finished
        self.death_animation_finished = False

        # Index for image loading and counting
        index = 1

        # Load textures for walking
        self.walk_textures = []
        while index <= 7:
            texture = load_texture_pair(f"Immagini/Enemy/goomba{index}.png")
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            index += 1
        index = 1

        # Load texture for death animation
        self.death_textures = []
        while index <= 4:
            texture = arcade.load_texture(f"Immagini/Enemy/goombaKO{index}.png")
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            index += 1

        # Set the initial texture
        self.texture = self.walk_textures[0][self.character_face_direction]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING

        # Walking animation
        if self.death == False:
            self.cur_texture += 1
            if self.cur_texture > 20:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        elif self.death == True:
            self.change_x = 0
            self.cur_texture = 0
            while self.cur_texture <= 19:
                self.texture = self.death_textures[self.cur_texture]
                self.cur_texture += 1
            self.cur_texture = 0
            self.death_animation_finished = True
        
class KoopaCharacter(arcade.Sprite):
    """ Koopa Sprite """
    def __init__(self, boundary_left, boundary_right, speed):

        super().__init__()

        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.change_x = speed

        # Default to face-left
        self.character_face_direction = LEFT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = TILE_SCALING

        # Set true when the goomba dies
        self.death = False

        # Set true when the death animation is finished
        self.death_animation_finished = False

        # Index for image loading and counting
        index = 1

        # Load textures for walking
        self.walk_textures = []
        while index <= 16:
            texture = arcade.load_texture_pair(f"Immagini/Enemy/tartaruga{index}.png")
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            self.walk_textures.append(texture)
            index += 1
        index = 1

        # Load textures death animation
        self.death_textures = []
        while index <= 5:
            texture = arcade.load_texture_pair(f"Immagini/Enemy/tartarugaKO{index}.png")
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            self.death_textures.append(texture)
            index += 1

        # Set the initial texture
        self.texture = self.walk_textures[0][self.character_face_direction]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x > 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        
        # Walking animation
        if self.death == False:
            self.cur_texture += 1
            if self.cur_texture > 79:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        elif self.death == True:
            self.change_x = 0
            self.cur_texture = 0
            while self.cur_texture <= 24:
                self.texture = self.death_textures[self.cur_texture][self.character_face_direction]
                self.cur_texture += 1
            self.cur_texture = 0
            self.death_animation_finished = True
        

class Coin(arcade.Sprite):
    """ Coin Sprite """
    def __init__(self, x, y):

        super().__init__()

        self.center_x = x
        self.center_y = y

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = TILE_SCALING

        # Set true when taken by the player
        self.taken = False

        # Index for image loading and counting
        index = 1

        # Load textures for animation
        self.animation_textures = []
        while index <= 11:
            texture = arcade.load_texture(f"Immagini/Coin/coin{index}.png")
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            self.animation_textures.append(texture)
            index += 1

        # Set the initial texture
        self.texture = self.animation_textures[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        #self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1/60):
        
        self.cur_texture += 1
        if self.cur_texture > 54:
            self.cur_texture = 0
        self.texture = self.animation_textures[self.cur_texture]

class CheckpointFlag(arcade.Sprite):
    """ Checkpoint flag sprite """
    def __init__(self):

        # Set up the parent class
        super().__init__()

        self.cur_texture = 0

        # Set true when player reaches the checkpoint
        self.reached = False

        # Index for image loading and counting
        index = 1

        # Load textures for animation
        self.animation_textures = []
        while index <= 23:
            texture = arcade.load_texture(f"Immagini/Checkpoint/Flag{index}.png")
            self.animation_textures.append(texture)
            index += 1

        # Set the initial texture
        self.texture = self.animation_textures[0]

    def update_animation(self, delta_time: float = 1/60):
        if self.reached == True:
            self.cur_texture += 1
            if self.cur_texture <= 22:
                self.texture = self.animation_textures[self.cur_texture]
            else:
                self.texture = self.animation_textures[22]

class Door(arcade.Sprite):
    """ Door Sprite """
    def __init__(self):

        # Set up parent class
        super().__init__()
        
        self.cur_texture = 0
        self.scale = TILE_SCALING

        # Set true when reached by the player
        self.reached = False

        # Set true when opening animation is finished
        self.animation_ended = False

        # Index for image loading and counting
        index = 1

        # Load textures for animation
        self.animation_textures = []
        while index <= 13:
            texture = arcade.load_texture(f"Immagini/Door/Door{index}.png")
            self.animation_textures.append(texture)
            index += 1

        # Set the initial texture
        self.texture = self.animation_textures[0]

    def update_animation(self, delta_time: float = 1/60):
        if self.reached == True:
            if self.cur_texture < 12:
                self.cur_texture += 1
                self.texture = self.animation_textures[self.cur_texture]
            else:
                self.animation_ended = True
                self.cur_texture = 12
                self.texture = self.animation_textures[self.cur_texture]
        elif self.reached == False:
            if self.cur_texture > 0:
                self.cur_texture -= 1
                self.texture = self.animation_textures[self.cur_texture]

class MyGame(arcade.View, threading.Thread, BanyanBase):
    """
    Main application class.
    """

    def __init__(self, back_plane_ip_address, process_name, player):
        """
        :param back_plane_ip_address: specify if running across multiple computers
        :param process_name: the name in the banyan header for this process
        :param player: 0=player one 1=player two
        """
        # initialize the python-banyan base class parent.
        # if the backplane_ip_address is == None, then the local IP
        # address is used.
        # The process name is just informational for the Banyan header
        # printed on the console.
        # The loop_time the amount of idle time in seconds for the
        # banyan receive_loop to wait to check for the next message
        # available in its queue.
        BanyanBase.__init__(self, back_plane_ip_address = back_plane_ip_address, process_name = process_name, loop_time = .0001)

        #add banyan subscription topic
        self.set_subscriber_topic("moveP1")
        self.set_subscriber_topic("powerup_taken")
        self.set_subscriber_topic("coin_taken")
        self.set_subscriber_topic("move_goomba")
        self.set_subscriber_topic("goomba_death")
        self.set_subscriber_topic("move_koopa")
        self.set_subscriber_topic("koopa_death")
        self.set_subscriber_topic("create_fireball")
        self.set_subscriber_topic("new_life")
        self.set_subscriber_topic("life_lost")
        self.set_subscriber_topic("respawn")
        self.set_subscriber_topic("door_reached") 
        self.set_subscriber_topic("checkpoint_reached")
        self.set_subscriber_topic("move_platform")
        self.set_subscriber_topic("next_level")

        # Call the parent class and set up the window
        arcade.View.__init__(self)
        
        # initialize the threading.Thread parent
        threading.Thread.__init__(self)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # create a threading lock
        self.the_lock = threading.Lock()

        # set this thread as a daemon thread
        self.daemon = True

        # create a threading event that will allow the start
        # and stopping of thread processing
        self.run_the_thread = threading.Event()

        # initially allow the thread to run
        self.run_the_thread = True

        # Understand who is the player
        self.player_logged = player

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.fireball_list = None
        self.goomba_list = None
        self.koopa_list = None
        self.lava_list = None
        self.powerup_list = None
        self.background_list = None
        self.platform_list = None
        self.window_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.player_two_sprite = None

        # Variable that holds lives image sprite
        self.lives_sprite = None

        # Holds the fire ball sprite
        self.fireball_sprite = None

        # Holds the mashroom sprite
        self.goomba_sprite = None

        # Holds the koopa sprite
        self.koopa_sprite = None

        # Holds the coin sprite
        self.coin_sprite = None

        # Holds the checkpoint sprite
        self.checkpoint_sprite = None

        # Holds the power up sprite
        self.powerup_sprite = None

        # Holds the door sprite
        self.door_sprite = None

        # Holds the moving platform sprite
        self.platform_sprite = None

        # Number of lives 
        self.lives_count = 5

        # Number of coins collected
        self.coin_count = 0

        # Used to check if it is the first time we reach the checkpoint
        self.first_time = True

        # Holds the db connection
        self.database_connection = database_connection()
        self.cursor = self.database_connection.cursor()

        # Variables used to manage our music. See setup() for giving them
        # values.
        self.music_list = []
        self.current_song_index = 0
        self.current_music_player = None
        self.music = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Used to set the timer
        self.total_time = 0.0

        # Holds the elapsed time from beginning
        self.final_time = 0.0

        # Holds the level number
        self.level = 1

        self.player_two_ready = True

        # Jump sound
        self.jump_sound = arcade.load_sound("musica/smb_jump-small.wav")

        # Coin collected sound
        self.coin_sound = arcade.load_sound("musica/smb_coin.wav")

        # Arrived at checkpoint sound
        self.checkpoint_sound = arcade.load_sound("musica/fanfare.mp3")

        # Shoot fireball sound
        self.fireball_sound = arcade.load_sound("musica/smb_fireball.wav")

        # Powerup taken sound
        self.powerup_taken = arcade.load_sound("musica/smb_powerup.wav")

        # Enemy killed sound
        self.enemy_killed = arcade.load_sound("musica/smb_kick.wav")

        # All lives lost
        self.gameover_sound = arcade.load_sound("musica/smb_mariodie.wav")

        # End of the level reached
        self.level_finished = arcade.load_sound("musica/smb_stage_clear.wav")

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

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_show_view(self):
        # List of music
        self.music_list = ["musica/TheWellerman8bit.mp3"]
        # Array index of what to play
        self.current_song_index = 0
        # Play the song
        self.play_song()
        # Set up player, physics and stuff
        self.setup(self.level)
        # start the second thread
        self.start()

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.background_list.draw()
        self.window_list.draw()
        self.wall_list.draw()
        self.door_sprite.draw()
        self.checkpoint_sprite.draw()
        self.coin_list.draw()
        self.powerup_list.draw()
        self.player_list.draw()
        self.fireball_list.draw()
        self.lava_list.draw()
        self.goomba_list.draw()
        self.koopa_list.draw()

        # Moves the lives counter on the screen
        self.lives_sprite._set_center_x(180 + self.view_left)
        self.lives_sprite._set_center_y(675 + self.view_bottom)
        self.lives_sprite.draw()

        # Moves the coin counter on the screen
        self.coin_logo_sprite._set_center_x(270 + self.view_left)
        self.coin_logo_sprite._set_center_y(675 + self.view_bottom)
        self.coin_logo_sprite.draw()

        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        # Figure out our time
        timer = f"Time: {minutes:02d}:{seconds:02d}"

        # Draw the timer
        arcade.draw_text(timer, 2 + self.view_left, 660 + self.view_bottom, arcade.csscolor.BLACK, 20)

        # Draw the lives count
        arcade.draw_text("x" + str(self.lives_count), 200 + self.view_left, 660 + self.view_bottom, arcade.csscolor.BLACK, 20)

        # Draw the coins count
        arcade.draw_text(str(self.coin_count), 290 + self.view_left, 660 + self.view_bottom, arcade.csscolor.BLACK, 20)

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Used to set the timer
        self.total_time = 0.0

        # Set up the lives sprite
        self.lives_sprite = arcade.Sprite("Immagini/vita.png", TILE_SCALING)

        # Set up the coin sprite on top of the screen
        self.coin_logo_sprite = arcade.Sprite("Immagini/moneta.png", TILE_SCALING)

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.fireball_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.lava_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()
        self.goomba_list = arcade.SpriteList()
        self.koopa_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.window_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter(True)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        
        self.player_list.append(self.player_sprite)

        # Set up the second player, specifically placing it at these coordinates.
        self.player_two_sprite = PlayerCharacter(False)
        self.player_two_sprite.center_x = PLAYER_START_X
        self.player_two_sprite.center_y = PLAYER_START_Y

        self.player_list.append(self.player_two_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = f"Map/Livello{level}.tmx"
        # Name of the layer in the file that has our platforms/walls
        wall_layer_name = "wall_list"
        background_layer_name = "background_list"
        lava_layer_name = "enemy_list"
        window_layer_name = "window_list"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object = my_map, layer_name = wall_layer_name, scaling = TILE_SCALING, use_spatial_hash = True)
        self.background_list = arcade.tilemap.process_layer(map_object = my_map, layer_name = background_layer_name, scaling = TILE_SCALING)
        self.lava_list = arcade.tilemap.process_layer(map_object = my_map, layer_name = lava_layer_name, scaling = TILE_SCALING, use_spatial_hash = True, hit_box_algorithm = "Detailed")

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # --- Load in the coordinates for powerup creation ---
        self.cursor.execute(f"SELECT * FROM Livello{level}Powerup")
        powerup_records = self.cursor.fetchall()
        for record in powerup_records:
            self.powerup_sprite = Powerup(float(record[1]), float(record[2]))
            self.powerup_list.append(self.powerup_sprite)
        

        # --- Load in the coordinates for goomba creation ---
        self.cursor.execute(f"SELECT * FROM Livello{level}Goomba")
        goomba_records = self.cursor.fetchall()
        for record in goomba_records:
            self.goomba_sprite = GoombaCharacter(float(record[3]), float(record[4]), float(record[5]))
            self.goomba_sprite.center_x = record[1]
            self.goomba_sprite.center_y = record[2]
            self.goomba_list.append(self.goomba_sprite)


        # --- Load in the coordinates for koopa creation
        self.cursor.execute(f"SELECT * FROM Livello{level}Koopa")
        koopa_records = self.cursor.fetchall()
        for record in koopa_records:
            self.koopa_sprite = KoopaCharacter(float(record[3]), float(record[4]), float(record[5]))
            self.koopa_sprite.center_x = record[1]
            self.koopa_sprite.center_y = record[2]
            self.koopa_list.append(self.koopa_sprite)


        # -- Load in the coordinates for coin creation ---
        self.cursor.execute(f"SELECT * FROM Livello{level}Coin")
        coin_records = self.cursor.fetchall()
        for record in coin_records:
            self.coin_sprite = Coin(float(record[1]), float(record[2]))
            self.coin_list.append(self.coin_sprite)


        # --- Load in the coordinates for checkpoint creation ---
        self.cursor.execute(f"SELECT * FROM Livello{level}Checkpoint")
        checkpoint_records = self.cursor.fetchall()
        for record in checkpoint_records:
            self.checkpoint_sprite = CheckpointFlag()
            self.checkpoint_sprite.center_x = float(record[1])
            self.checkpoint_sprite.center_y = float(record[2])


        # --- Load in the coordinates for door creation ---
        self.cursor.execute(f"SELECT * FROM Livello{level}Door")
        door_records = self.cursor.fetchall()
        for record in door_records:
            self.door_sprite = Door()
            self.door_sprite.center_x = float(record[1])
            self.door_sprite.center_y = float(record[2])
                

        if self.level == 4:
            self.window_list = arcade.tilemap.process_layer(map_object = my_map, layer_name = window_layer_name, scaling = TILE_SCALING, use_spatial_hash = True)
            # --- Load in the coordinates for door creation ---
            self.cursor.execute(f"SELECT * FROM Livello{level}Platform")
            platforms_records = self.cursor.fetchall()
            for record in platforms_records:
                self.platform_sprite = Platform(float(record[1]), float(record[2]), float(record[3]), float(record[4]), float(record[5]))
                self.platform_list.append(self.platform_sprite)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if (key == arcade.key.UP or key == arcade.key.W) and self.player_sprite.death == False: 
            if self.physics_engine.can_jump(): 
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound, 0.5)
        elif (key == arcade.key.LEFT or key == arcade.key.A) and self.player_sprite.center_x > 10 and self.player_sprite.death == False:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif (key == arcade.key.LEFT or key == arcade.key.A) and self.player_sprite.center_x > 10 and self.player_sprite.death == False:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif (key == arcade.key.RIGHT or key == arcade.key.D) and self.player_sprite.center_x < 7865 and self.level <= 2:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif (key == arcade.key.RIGHT or key == arcade.key.D) and self.player_sprite.center_x < 18890 and self.level > 2:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE and self.player_sprite.powerup == True and len(self.fireball_list) == 0:
            # Create the fireball and locate it where is the player
            self.fireball_sprite = FireBall(self.player_sprite.center_x, self.player_sprite.center_y)

            # Manage the firball direction
            if self.player_sprite.character_face_direction == RIGHT_FACING:
                self.fireball_sprite.change_x = FIREBALL_SPEED
            elif self.player_sprite.character_face_direction == LEFT_FACING:
                self.fireball_sprite.change_x = -FIREBALL_SPEED
            
            # Move the fireball
            self.fireball_sprite.start_animation = True

            # Tell the other player to create the fireball
            payload = {"fireball_x" : self.fireball_sprite.center_x, "fireball_y" : self.fireball_sprite.center_y, "fireball_change_x" : self.fireball_sprite.change_x, "player_logged" : self.player_logged}
            topic = "create_fireball"
            self.publish_payload(payload, topic)

            self.fireball_list.append(self.fireball_sprite)
            arcade.play_sound(self.fireball_sound, 0.5)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        if self.lives_count < 0:
            self.music.stop(self.current_music_player)
            arcade.play_sound(self.gameover_sound, 1)
            time.sleep(2.5)
            gameover_view = GameOver_file.GameOverView()
            self.window.show_view(gameover_view)
            arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        # The other player revive us
        if arcade.check_for_collision(self.player_sprite, self.player_two_sprite) and self.player_sprite.death == True:
            # Reset the view
            self.view_bottom = 0
            if self.player_two_sprite.center_x < SCREEN_WIDTH/2:
                self.view_left = 0
                arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            else:
                if self.level <= 2:
                    if self.player_two_sprite.center_x < (7875 - (SCREEN_WIDTH / 2)):
                        self.view_left = self.player_two_sprite.center_x - SCREEN_WIDTH/2
                        arcade.set_viewport(self.player_two_sprite.center_x - SCREEN_WIDTH/2, self.player_two_sprite.center_x + SCREEN_WIDTH/2, 0, SCREEN_HEIGHT)
                    else:
                        arcade.set_viewport((7875 - SCREEN_WIDTH), 7875, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
                else:
                    if self.player_two_sprite.center_x < (18900 - (SCREEN_WIDTH / 2)):
                        self.view_left = self.player_two_sprite.center_x - SCREEN_WIDTH/2
                        arcade.set_viewport(self.player_two_sprite.center_x - SCREEN_WIDTH/2, self.player_two_sprite.center_x + SCREEN_WIDTH/2, 0, SCREEN_HEIGHT)
                    else:
                        arcade.set_viewport((18900 - SCREEN_WIDTH), 18900, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

            self.player_sprite.death = False
            
            # Reset the animation for death
            self.player_sprite.coffin_boundary_top_reached = False
            self.player_sprite.coffin_boundary_bottom_reached = True
            # Tell the other player that we respawn
            payload = {"player_logged" : self.player_logged}
            topic = "respawn"
            self.publish_payload(payload, topic)

        # Move the player with the physics engine only if he is alive
        if self.player_sprite.death == False:
            self.physics_engine.update()

        # Move the player connected
        payload = {"p1_x" : self.player_sprite.center_x, "p1_y" : self.player_sprite.center_y, "p1_change_x" : self.player_sprite.change_x, "p2_change_y" : self.player_sprite.change_y, "powerup" : self.player_sprite.powerup, "player_logged" : self.player_logged}
        topic = "moveP1"
        self.publish_payload(payload, topic)

        # Add a life if the coin taken are 10
        if self.coin_count >= 10:
            self.coin_count -= 10
            self.lives_count += 1
            payload = {"player_logged" : self.player_logged}
            topic = "new_life"
            self.publish_payload(payload, topic)

        # Reset the the door reached by the player
        self.player_sprite.level_ended = False

        # Reset the door animation for closing if not reached
        self.door_sprite.reached = False

        # Update the fire balls position
        self.fireball_list.update()

        # Check goomba elimination by the player two
        for goomba in self.goomba_list:
            if goomba.death_animation_finished == True:
                arcade.play_sound(self.enemy_killed, 0.5)
                goomba.remove_from_sprite_lists()
                

        # Check koopa elimination by the player two
        for koopa in self.koopa_list:
            if koopa.death_animation_finished == True:
                arcade.play_sound(self.enemy_killed, 0.5)
                koopa.remove_from_sprite_lists()

        # --- Manage Enemy movement ---
        # Update goomba and koopa position if the player logged is the player 0
        if self.player_logged == 0:
            # Update goombas position
            self.goomba_list.update()
            # Update koopas position
            self.koopa_list.update()

             # See if the goomba hits a boundary and needs to reverse direction.
            for goomba in self.goomba_list:
                if goomba.boundary_right and goomba.right > goomba.boundary_right and goomba.change_x > 0:
                    goomba.change_x *= -1
                if goomba.boundary_left and goomba.left < goomba.boundary_left and goomba.change_x < 0:
                    goomba.change_x *= -1
                
                # Tell other player the goomba position
                if self.player_two_ready == True:
                    payload = {"goomba_index": self.goomba_list.index(goomba), "goomba_x" : goomba.center_x, "goomba_y" : goomba.center_y, "goomba_change_x" : goomba.change_x, "player_logged" : self.player_logged}
                    topic = "move_goomba"
                    self.publish_payload(payload, topic)

            # See if the koopa hits a boundary and needs to reverse direction.
            for koopa in self.koopa_list:
                if koopa.boundary_right and koopa.right > koopa.boundary_right and koopa.change_x > 0:
                    koopa.change_x *= -1
                if koopa.boundary_left and koopa.left < koopa.boundary_left and koopa.change_x < 0:
                    koopa.change_x *= -1
            
                # Tell other player the koopa position
                if self.player_two_ready == True:
                    payload = {"koopa_index": self.koopa_list.index(koopa), "koopa_x" : koopa.center_x, "koopa_y" : koopa.center_y, "koopa_change_x" : koopa.change_x, "player_logged" : self.player_logged}
                    topic = "move_koopa"
                    self.publish_payload(payload, topic)

            # --- Manage moving platforms ---
            if self.level == 4:
                self.platform_list.update()
                for platform in self.platform_list:
                    if platform.boundary_right and platform.right > platform.boundary_right and platform.change_x > 0:
                        platform.change_x *= -1
                    if platform.boundary_left and platform.left < platform.boundary_left and platform.change_x < 0:
                        platform.change_x *= -1

                    # Tell other player the platform position
                    if self.player_two_ready == True:
                        payload = {"platform_index": self.platform_list.index(platform), "platform_x" : platform.center_x, "platform_y" : platform.center_y, "platform_change_x" : platform.change_x, "player_logged" : self.player_logged}
                        topic = "move_platform"
                        self.publish_payload(payload, topic)

        # Update the lives img
        self.lives_sprite.update()

        # --- Manage Collision ---

        # Manage Fire Ball extinction and collision
        for fireball in self.fireball_list:

            if fireball.exploded_animation_finished == True:
                fireball.remove_from_sprite_lists()

            # Manage the auto destruction
            # Need >= and <= because center_x reflects the delta_time
            # After 10 block the fire ball will be extinguished or 
            # if it goes out of the screen
            if fireball.center_x >= (fireball.starting_x + 315):
                fireball.exploded = True
            if fireball.center_x <= (fireball.starting_x - 315):
                fireball.exploded = True
            if fireball.center_x <= 10:
                fireball.exploded = True

            # Manage the collision with a wall
            if arcade.check_for_collision_with_list(fireball, self.wall_list):
                fireball.exploded = True

            if self.player_logged == 0:
                # Manage the collision with a goomba
                for goomba in self.goomba_list:
                    if arcade.check_for_collision(fireball, goomba):
                        goomba.death = True
                        fireball.exploded = True
                        arcade.play_sound(self.enemy_killed, 0.5)
                        
                        # Tell the other player that a goomba has died
                        payload = {"fireball_index" : self.fireball_list.index(fireball), "goomba_index" : self.goomba_list.index(goomba), "player_logged" : self.player_logged}
                        topic = "goomba_death"
                        self.publish_payload(payload, topic)

                # Manage the collision with a koopa
                for koopa in self.koopa_list:
                    if arcade.check_for_collision(fireball, koopa):
                        koopa.death = True
                        fireball.exploded = True
                        arcade.play_sound(self.enemy_killed, 0.5)
                        
                        # Tell the other player that a goomba has died
                        payload = {"fireball_index" : self.fireball_list.index(fireball), "koopa_index" : self.koopa_list.index(koopa), "player_logged" : self.player_logged}
                        topic = "koopa_death"
                        self.publish_payload(payload, topic)

        # See if we hit a a coin
        for coin in self.coin_list:
            if arcade.check_for_collision(self.player_sprite, coin):
                arcade.play_sound(self.coin_sound, 0.5)
                coin.taken = True

                # Tell the other player that coin has been taken
                payload = {"coin_index" : self.coin_list.index(coin), "player_logged" : self.player_logged}
                topic = "coin_taken"
                self.publish_payload(payload, topic)
            
            # Remove coin from map if it has been taken
            if coin.taken == True:
                self.coin_count += 1
                coin.remove_from_sprite_lists()

        # See if we hit any enemy or lava
        if arcade.check_for_collision_with_list(self.player_sprite, self.goomba_list) or arcade.check_for_collision_with_list(self.player_sprite, self.koopa_list) or arcade.check_for_collision_with_list(self.player_sprite, self.lava_list):
            self.player_sprite.death = True
            self.lives_count -= 1

            # Tell the other player that we lost a life
            payload = {"player_logged" : self.player_logged}
            topic = "life_lost"
            self.publish_payload(payload, topic)

            self.player_sprite.powerup = False
            if self.checkpoint_sprite.reached == False and self.player_two_sprite.death == True:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.player_sprite.center_x = PLAYER_START_X
                self.player_sprite.center_y = PLAYER_START_Y
                # Set the camera to the start
                self.view_left = 0
                self.view_bottom = 0
                arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
                self.player_sprite.death = False
                # Tell the other player that we respawn
                payload = {"player_logged" : self.player_logged}
                topic = "respawn"
                self.publish_payload(payload, topic)

            elif self.checkpoint_sprite.reached == True and self.player_two_sprite.death == True:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.player_sprite.center_x = self.checkpoint_sprite.center_x
                self.player_sprite.center_y = self.checkpoint_sprite.center_y
                self.view_bottom = 0
                self.player_sprite.death = False
                # Tell the other player that we respawn
                payload = {"player_logged" : self.player_logged}
                topic = "respawn"
                self.publish_payload(payload, topic)

            elif self.player_two_sprite.death == False:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.player_sprite.center_x = self.player_two_sprite.center_x
                # Respawn three block over the other player
                self.player_sprite.center_y = 285
                self.view_bottom = 0
                if self.player_two_sprite.center_x < SCREEN_WIDTH/2:
                    self.view_left = 0
                    arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
                else:
                    if self.level <= 2:
                        if self.player_two_sprite.center_x < (7875 - (SCREEN_WIDTH / 2)):
                            self.view_left = self.player_two_sprite.center_x - SCREEN_WIDTH/2
                            arcade.set_viewport(self.player_two_sprite.center_x - SCREEN_WIDTH/2, self.player_two_sprite.center_x + SCREEN_WIDTH/2, 0, SCREEN_HEIGHT)
                        else:
                            arcade.set_viewport((7875 - SCREEN_WIDTH), 7875, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
                    else:
                        if self.player_two_sprite.center_x < (18900 - (SCREEN_WIDTH / 2)):
                            self.view_left = self.player_two_sprite.center_x - SCREEN_WIDTH/2
                            arcade.set_viewport(self.player_two_sprite.center_x - SCREEN_WIDTH/2, self.player_two_sprite.center_x + SCREEN_WIDTH/2, 0, SCREEN_HEIGHT)
                        else:
                            arcade.set_viewport((18900 - SCREEN_WIDTH), 18900, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

        # See if we reached the checkpoint
        if arcade.check_for_collision(self.player_sprite, self.checkpoint_sprite):
            if self.checkpoint_sprite.reached == False:
                self.checkpoint_sprite.reached = True
            if self.first_time == True:
                    # Tell the other player that the checkpoint has been reached
                    payload = {"player_logged" : self.player_logged}
                    topic = "checkpoint_reached"
                    self.publish_payload(payload, topic)

                    arcade.play_sound(self.checkpoint_sound, 0.34)
                    self.first_time = False
        # Update checkpoint animation only if the checkpoint has been reached    
        self.checkpoint_sprite.update_animation()

        # See if we caught the power up
        for powerup in self.powerup_list:

            if arcade.check_for_collision(self.player_sprite, powerup):
                # Tell the other player that powerup has been taken
                topic = "powerup_taken"
                payload = {"powerup_index" : self.powerup_list.index(powerup), "player_logged" : self.player_logged}
                self.publish_payload(payload, topic)

                self.powerup_sprite.taken = True
                self.player_sprite.powerup = True
                self.player_sprite.powerup_start = int(self.total_time)
                arcade.play_sound(self.powerup_taken, 0.5)

            # Remove powerup from map if it has been taken
            if powerup.taken == True:
                powerup.remove_from_sprite_lists()

        # See if we reached the door
        if arcade.check_for_collision(self.player_sprite, self.door_sprite):
            self.door_sprite.reached = True
            self.player_sprite.level_ended = True
    
        # Tell other player if we reached the door
        payload = {"player_arrived" : self.player_sprite.level_ended ,"player_logged" : self.player_logged}
        topic = "door_reached"
        self.publish_payload(payload, topic)

        # Advance to the next level
        if self.player_sprite.level_ended == True and self.player_two_sprite.level_ended == True:
            if self.door_sprite.animation_ended == True and self.level < 4:
                self.door_sprite.animation_ended = False
                self.first_time = True
                self.level += 1
                self.final_time += self.total_time
                arcade.play_sound(self.level_finished, 1)
                time.sleep(5.5)
                self.player_two_ready = False
                self.player_sprite.powerup = False
                self.setup(self.level)
                # Set the camera to the start
                self.view_left = 0
                self.view_bottom = 0
                arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
                if self.player_logged == 1:
                    payload = {"player_logged" : self.player_logged}
                    topic = "next_level"
                    self.publish_payload(payload, topic)
            
            # That was the last level so the game ends
            if self.door_sprite.animation_ended == True and self.level == 4:
                self.music.stop(self.current_music_player)
                self.final_time += self.total_time
                arcade.play_sound(self.level_finished, 1)
                time.sleep(5.5)
                gamewon_view = game_won_file.GameWonView(True, self.final_time, self.lives_count)
                self.window.show_view(gamewon_view)
                arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        # --- Manage Scrolling ---
        # Track if we need to change the viewport
        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        self.player_list.update_animation(delta_time)

        if changed and self.view_left > 0:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            if self.level <= 2:
                if (self.view_left + SCREEN_WIDTH) < 7875:
                    self.view_bottom = int(self.view_bottom)
                    self.view_left = int(self.view_left)

                    # Do the scrolling
                    arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
            else:
                if (self.view_left + SCREEN_WIDTH) < 18900:
                    self.view_bottom = int(self.view_bottom)
                    self.view_left = int(self.view_left)

                    # Do the scrolling
                    arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
        
        # --- Manage Position ---
        # Too left
        if self.player_sprite.center_x <= 10:
            self.player_sprite.change_x = 0
        
        # Too right
        if self.level <=2:
            if self.player_sprite.center_x >= 7865:
                self.player_sprite.change_x = 0
        if self.level > 2:
            if self.player_sprite.center_x >= 18890:
                self.player_sprite.change_x = 0

        # --- Manage Animations ---
        self.player_list.update_animation(delta_time)
        self.fireball_list.update_animation(delta_time)
        self.goomba_list.update_animation(delta_time)
        self.koopa_list.update_animation(delta_time)
        self.coin_list.update_animation(delta_time)

        self.door_sprite.update_animation(delta_time)

        # Update the timer
        self.total_time += delta_time

        # Useful to know if the song is still running
        position = self.music.get_stream_position(self.current_music_player)

        # The position pointer is reset to 0 right after we finish the song.
        # This makes it very difficult to figure out if we just started playing
        # or if we are doing playing.
        if position == 0.0:
            self.advance_song()
            self.play_song()

    # Process banyan subscribed messages
    def run(self):
        """
        This thread continually attempts to receive
        incoming Banyan messages. If a message is received,
        incoming_message_processing is called to handle
        the message.

        """
        # start the banyan loop - incoming messages will be processed
        # by incoming_message_processing in this thread.
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        """
        Process the incoming Banyan messages

        :param topic: Message Topic string.

        :param payload: Message Data.
        """
        if self.external_message_processor:
            self.external_message_processor(topic, payload)
        else:
            if topic == "moveP1" and payload["player_logged"] != self.player_logged:
                self.player_two_sprite.center_x = payload["p1_x"]
                self.player_two_sprite.center_y = payload["p1_y"]
                self.player_two_sprite.change_x = payload["p1_change_x"]
                self.player_two_sprite.change_y = payload["p2_change_y"]
                self.player_two_sprite.powerup = payload["powerup"]

            if topic == "move_platform" and payload["player_logged"] != self.player_logged:
                self.platform_list[payload["platform_index"]].center_x = payload["platform_x"]
                self.platform_list[payload["platform_index"]].center_Y = payload["platform_y"]
                self.platform_list[payload["platform_index"]].change_x = payload["platform_change_x"]

            if topic == "move_goomba" and payload["player_logged"] != self.player_logged:
                if self.goomba_list[payload["goomba_index"]].death == False:
                    self.goomba_list[payload["goomba_index"]].center_x = payload["goomba_x"]
                    self.goomba_list[payload["goomba_index"]].center_Y = payload["goomba_y"]
                    self.goomba_list[payload["goomba_index"]].change_x = payload["goomba_change_x"]

            if topic == "move_koopa" and payload["player_logged"] != self.player_logged:
                self.koopa_list[payload["koopa_index"]].center_x = payload["koopa_x"]
                self.koopa_list[payload["koopa_index"]].center_y = payload["koopa_y"]
                self.koopa_list[payload["koopa_index"]].change_x = payload["koopa_change_x"]
            
            if topic == "powerup_taken" and payload["player_logged"] != self.player_logged:
                self.powerup_list[payload["powerup_index"]].taken = True

            if topic == "coin_taken" and payload["player_logged"] != self.player_logged:
                self.coin_list[payload["coin_index"]].taken = True

            if topic == "goomba_death" and payload["player_logged"] != self.player_logged:
                self.goomba_list[payload["goomba_index"]].death = True
                self.fireball_list[payload["fireball_index"]].exploded = True

            if topic == "koopa_death" and payload["player_logged"] != self.player_logged:
                self.koopa_list[payload["koopa_index"]].death = True
                self.fireball_list[payload["fireball_index"]].exploded = True

            if topic == "create_fireball" and payload["player_logged"] != self.player_logged:
                center_x = payload["fireball_x"]
                center_y = payload["fireball_y"]
                change_x = payload["fireball_change_x"]
                self.fireball_sprite = FireBall(center_x, center_y)
                self.fireball_sprite.change_x = change_x
                self.fireball_sprite.start_animation = True
                self.fireball_list.append(self.fireball_sprite)
                arcade.play_sound(self.fireball_sound, 0.5)

            if topic == "new_life" and payload["player_logged"] != self.player_logged:
                self.coin_count -= 10
                self.lives_count += 1

            if topic == "life_lost" and payload["player_logged"] != self.player_logged:
                self.player_two_sprite.death = True
                self.lives_count -= 1

            if topic == "respawn" and payload["player_logged"] != self.player_logged:
                self.player_two_sprite.death = False

            if topic == "checkpoint_reached" and payload["player_logged"] != self.player_logged:
                self.checkpoint_sprite.reached = True
                if self.first_time == True:
                    arcade.play_sound(self.checkpoint_sound, 0.34)
                    self.first_time = False

            if topic == "door_reached" and payload["player_logged"] != self.player_logged:
                self.player_two_sprite.level_ended = payload["player_arrived"]
            
            if topic == "next_level" and payload["player_logged"] != self.player_logged:
                self.player_two_ready = True