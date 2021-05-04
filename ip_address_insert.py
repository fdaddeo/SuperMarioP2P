import arcade
import arcade.gui
from arcade.gui import UIManager
import os
import sys
import threading
import psutil
import subprocess
from python_banyan.banyan_base import BanyanBase
import multi_player as multiplayer_file

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

JOIN_BTN_SCALE = 1.6

PROCESS_NAME = "SuperMario P2P"

# Boolean to check status
player_two_start = False

# Get the input
ip_address_inserted = None

class StartButton(arcade.gui.UIImageButton, threading.Thread, BanyanBase):
    def __init__(self, normal_texture, hover_texture, press_texture, center_x, center_y, input_box):
        arcade.gui.UIImageButton.__init__(self, normal_texture = normal_texture, hover_texture = hover_texture, press_texture = press_texture, center_x = center_x, center_y = center_y)
        self.input_box = input_box

    def on_click(self):
        global ip_address_inserted
        ip_address_inserted = str(self.input_box.text)

        # initialize the threading.Thread parent
        threading.Thread.__init__(self)

        # create a threading lock
        self.the_lock = threading.Lock()

        # set this thread as a daemon thread
        self.daemon = True

        # create a threading event that will allow the start
        # and stopping of thread processing
        self.run_the_thread = threading.Event()

        # initially allow the thread to run
        self.run_the_thread = True

        BanyanBase.__init__(self, back_plane_ip_address = ip_address_inserted, process_name = PROCESS_NAME, loop_time = .0001)

        # add banyan subscription topic
        self.set_subscriber_topic("ip_inserted")
        self.set_subscriber_topic("result_connection")

        # start the second thread
        self.start()

        # send message
        topic = "ip_inserted"
        payload = {"ip" : ip_address_inserted}
        self.publish_payload(payload, topic)
        print("Ip Sent")

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
            if topic == "result_connection":
                # Non riceve!!!!!! :)
                print("Received Result")
                if payload["res"] == "ok":
                    global player_two_start
                    player_two_start = True
                else:
                    print("Bad IP")
        

class IPAdressWindow(arcade.View):
    """
    Main application class.
    """
    def __init__(self):
        arcade.View.__init__(self)
        self.ui_manager = UIManager()

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.background = None

    def on_show(self):
        """ Called once when view is activated. """
        self.background = arcade.load_texture("Immagini/sky.png")

    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

    def setup(self):
        """ Set up this view. """
        self.ui_manager.purge_ui_elements()
        # Player1 has to insert the IP address to perform the connection
        y_slot = SCREEN_HEIGHT // 2
        left_column_x = SCREEN_WIDTH // 4
        right_column_x = 3 * SCREEN_WIDTH // 4

        # left side elements
        self.ui_input_box = arcade.gui.UIInputBox(center_x = left_column_x, center_y = y_slot, width = 300)
        self.ui_input_box.text = "IP address here"
        self.ui_input_box.cursor_index = len(self.ui_input_box.text)
        self.ui_manager.add_ui_element(self.ui_input_box)

        self.button_normal = arcade.load_texture('Immagini/Start.png')
        self.hovered_texture = arcade.load_texture('Immagini/StartPressed.png')
        self.pressed_texture = arcade.load_texture('Immagini/StartPressed.png')
        self.start_btn = StartButton(normal_texture = self.button_normal, hover_texture = self.hovered_texture, press_texture = self.pressed_texture, center_x = right_column_x, center_y = y_slot, input_box = self.ui_input_box)
        self.start_btn.scale = JOIN_BTN_SCALE
        self.ui_manager.add_ui_element(self.start_btn)

       
    def on_update(self, delta_time):

        if player_two_start == True:
            game_view = multiplayer_file.MyGame(ip_address_inserted, PROCESS_NAME, 1)
            self.window.show_view(game_view)        