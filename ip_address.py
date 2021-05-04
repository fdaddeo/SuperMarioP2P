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

# Boolean to check the player status
player_one_start = False

class IPAdressWindow(arcade.View, threading.Thread, BanyanBase):
    """
    Main application class.
    """
    def __init__(self):
        """
        :param player: 0 = player one, 1 = player two
        """
        arcade.View.__init__(self)

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

        self.start_backplane()

        # initialize the python-banyan base class parent.
        # if the backplane_ip_address is == None, then the local IP
        # address is used.
        # The process name is just informational for the Banyan header
        # printed on the console.
        # The loop_time the amount of idle time in seconds for the
        # banyan receive_loop to wait to check for the next message
        # available in its queue.
        BanyanBase.__init__(self, back_plane_ip_address = None, process_name = PROCESS_NAME, loop_time = .0001)

        # add banyan subscription topic
        self.set_subscriber_topic("ip_inserted")
        self.set_subscriber_topic("result_connection")
        
        self.ip_address = self.back_plane_ip_address

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # start the second thread
        self.start()

        self.background = None

    def on_show_view(self):
        """ Called once when view is activated. """
        self.background = arcade.load_texture("Immagini/sky.png")

    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        # Player0 has to know the IP address in order to comunicate it
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        arcade.draw_text(f"Your IP address to be comunicated is: {self.ip_address}", center_x, center_y, arcade.color.BLACK, 14, width = SCREEN_WIDTH, align = "center", anchor_x = "center", anchor_y = "center")
       
    def on_update(self, delta_time):
        if player_one_start == True:
            game_view = multiplayer_file.MyGame(self.ip_address, PROCESS_NAME, 0)
            self.window.show_view(game_view)

    def start_backplane(self):
        """
        Start the backplane
        """
        # check to see if the backplane is already running
        try:
            for proc in psutil.process_iter(attrs = ["pid", "name"]):
                if "backplane" in proc.info["name"]:
                    # its running - return its pid
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        # backplane is not running, so start one
        if sys.platform.startswith("win32"):
            return subprocess.Popen(["backplane"], creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
        else:
            return subprocess.Popen(["backplane"], stdin = subprocess.PIPE, stderr = subprocess.PIPE, stdout = subprocess.PIPE)

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
            if topic == "ip_inserted":
                # In realtà controllo inutile perchè se mex arriva allora IP giusto per forza
                print("IP Received")
                if payload["ip"] == self.ip_address:
                    global player_one_start
                    topic_back = "result_connection"
                    payload_back = {"res" : "ok"}
                    self.publish_payload(payload_back, topic_back)
                    print("Result Ok Sent")

                    player_one_start = True
                else:
                    topic_back = "result_connection"
                    payload_back = {"res" : "no"}
                    self.publish_payload(payload_back, topic_back)
                    print("Result No Sent")