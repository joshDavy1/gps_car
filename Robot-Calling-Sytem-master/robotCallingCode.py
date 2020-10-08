###############################
#
# File   : robotCallingCode.py
# Author : Hayden Coe
# Date   : 24/08/2020
#
##############################

from os import path, getenv
from robotStateCode import RobotState
from logging import basicConfig, INFO
basicConfig(level=INFO)
import threading
import json
import time

import gui
import buttons
import gpsCode
import ws


class MainApp():

    def __init__(self, gps_rate=None):
        # initialize objects
        self.stop_blink = threading.Event()
        self._gui = gui.GUI()
        self._buttons = buttons.Buttons(
            on_green=self.green_callback, 
            on_blue=self.blue_callback, 
            on_red=self.red_callback
        )
        self.rs = RobotState()
        print("The first state in the state machine is: %s" % self.rs.state)
        
        self._gps = gpsCode.GPS()

    def start(self, gps_rate=None):
        # get user to login
        self.user_name = self._gui.waitForLogin() # < blocking

        # init websocket
        self._ws = ws.WS(address="wss://lcas.lincoln.ac.uk/car/ws", user_name=self.user_name, 
            update_orders_cb=self.update_orders_cb)

        # setup the main gui window
        self._gui.setupMainWindow()

        self._gui.setUser(self.user_name)
        self._gui.setDescription("Welcome to Call A Robot.")
        
        # start gps thread
        self._gps.start()

        # start ws thread
        self._ws.start()

        if gps_rate is None:
            ## we want gps readings as soon as they arrive
            self._gps.set_callback(self._ws.send_gps)

            # start gui thread (tkinter only runs on the main thread :( )
            self._gui.loopMainWindow()  # < blocking
        else:
            ## we want gps readings at a certain rate
            seconds = 1./float(gps_rate)

            while self._gps.has_more_data():
                lat, lon, epx, epy, ts  = self._gps.get_latest_data()
                
                self._ws.send_gps(lat, lon, epx, epy, ts)

                time.sleep(seconds)

    def stop(self):
        self._gps.stop()
        self._ws.stop()
        self._buttons.cleanup()

    # this receives updated state for the current user
    def update_orders_cb(self, state):
        if state == "ACCEPT":
            if self.rs.state == "CALLED":
                print("A Robot is on the way.")
                self._gui.setDescription("A Robot is on the way")
        elif state == "INIT":
            if self.rs.state == "CALLED":
                print("Robot Successfully Cancelled.")
                self._gui.setDescription("Robot Successfully Cancelled.")
                self._buttons.setGreenLed(False)
                self._gui.setGreenButton(False)
                self._buttons.setRedLed(False)
                self._gui.setRedButton(False)
            elif self.rs.state == "ARRIVED":
                print("Robot Load Successfully Cancelled.")    
                self._gui.setDescription("Robot Successfully Cancelled.")
                self._buttons.setBlueLed(False)
                self._gui.setBlueButton(False)
                self._buttons.setRedLed(False)
                self._gui.setRedButton(False)
            time.sleep(1)
            self._gui.setDescription("Welcome to Call A Robot.")
        elif state == "ARRIVED":
            if self.rs.state == "CALLED":
                self._buttons.setGreenLed(False)
                self._gui.setGreenButton(False)
                print("Robot has arrived.")
                print("Please load the tray on the robot then press the blue button.")
                self._gui.setDescription("Please load the tray on the robot then press the blue button.")

                self.blink_thr = threading.Thread(target=self.blue_blink)
                
                self.blink_thr.start()
                self.rs.robot_arrived()
        elif state == "LOADED":
            if self.rs.state == "ARRIVED":
                self.stop_blink.set()

        # update internal state
        #self.rs.state = state


    def green_callback(self, channel):
        print("Green button pressed")
        if (self.rs.state == "INIT"):
            print("Calling Robot.")
            self._gui.setDescription("Calling Robot.")
            self._buttons.setGreenLed(True)
            self._gui.setGreenButton(True)
            self._ws.call_robot()
            
            self.rs.call_robot()
            # y = threading.Thread(target=check_arrived)
            # y.start()
        else:
            print("A Robot has already been called.")
            self._gui.setDescription("A Robot has already been called.")
            
    def red_callback(self, channel):
        print("Red button pressed")
        if (self.rs.state=="CALLED"):
            print("Cancelling...")
            self._gui.setDescription("Cancelling...")
            self._buttons.setRedLed(True)
            self._gui.setRedButton(True)
            self._ws.cancel_robot()
            self.rs.cancel_robot()
        elif (self.rs.state=="ARRIVED"):
            print("Cancelling...")
            self._gui.setDescription("Cancelling...")
            self._buttons.setRedLed(True)
            self._gui.setRedButton(True)
            self._ws.cancel_robot()
            self.rs.cancel_robot()
        else:
            print("No incoming robots to cancel.")
            self._gui.setDescription("No incoming robots to cancel.")
            time.sleep(1)
            self._gui.setDescription("Welcome to Call A Robot.")

    def blue_callback(self, channel):
        if (self.rs.state=="ARRIVED"):
            self._gui.setDescription("Thank you the robot will now drive away.")
            self._ws.set_loaded()
            self.rs.robot_loaded()
        else:
            print("No robots to load.")
            self._gui.setDescription("No robots to load.")
            time.sleep(1)
            self._gui.setDescription("Welcome to Call A Robot.")
    
    def blue_blink(self):        
        while not (self.stop_blink.is_set()):
            self._buttons.setBlueLed(True)
            self._gui.setBlueButton(True)
            time.sleep(0.5)
            self._buttons.setBlueLed(False)
            self._gui.setBlueButton(False)
            time.sleep(0.5) 


if __name__ == "__main__":
    # pub gps rate
    rate = 2 # hz
    app = MainApp(rate)

    try:
        app.start()
    except KeyboardInterrupt: 
        print ("Exiting")
        app.stop()
