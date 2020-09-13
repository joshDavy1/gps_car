###############################
#
# File   : robotCallingCode.py
# Author : Hayden Coe
# Date   : 24/08/2020
#
##############################

import RPi.GPIO as GPIO
from time import sleep
import logging
import threading

from RPLCD.i2c import CharLCD
import smbus

from websocket import create_connection
import websocket

import webnsock
import web
from signal import signal, SIGINT, pause
from os import path
from csv import DictWriter
from datetime import datetime
from time import mktime
from collections import defaultdict
from json import dumps
from uuid import uuid4
from os import getenv
from logging import error, warn, info, debug, basicConfig, INFO, exception
basicConfig(level=INFO)

from statemachine import StateMachine, State
from transitions import Machine
from robotStateCode import RobotState

import requests
import json

from callarobot import *

import os
from gps import *


#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

#Set the Buttons and LED pins
greenButton = 23
greenLED = 24

redButton = 16
redLED = 13

blueButton = 5
blueLED = 26

state=0

#Setup the Buttons and LEDs
GPIO.setup(greenButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(greenLED,GPIO.OUT)

GPIO.setup(redButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(redLED,GPIO.OUT)

GPIO.setup(blueButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(blueLED,GPIO.OUT)

#Button states
#Arrived button for testing robot arrival
arrivedButton = 21
GPIO.setup(arrivedButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)

lat = ''
long = ''

try:
   
    def getPositionData(gps):
            
            global lat
            global long
            
            while (lat == '') and (long == ''):
                nx = gpsd.next()
                
                if nx['class'] == 'TPV':
                    lat = getattr(nx, 'lat', "Unknown")
                    long = getattr(nx, 'lon', "Unknown")
                    print ("Your position: lat = " + str(lat) + ", long = " + str(long))
                    
                    epx = getattr(nx, 'epx', "Unknown")
                    epy = getattr(nx, 'epy', "Unknown")
                    print ("lat error = " + str(epy) + "m" + ", long error = " + str(epx) + "m") 
                    #epe = epy+'/'+epx
                    
                    time = getattr(nx, 'time', "Unknown")
                    print ("time = " + str(time))
                            
            ws.send(json.dumps({'method':'location_update', 'row':'A1', 'user': 'Hayden', 'latitude':lat, 'longitude':long, 'accuracy':epx, 'rcv_time':time}))    
    
    def main():

        #Main program
        print("Welcome to Call A Robot")
        
        rs = RobotState()
        print ("The first state in the state machine is: %s" % rs.state)
            
                
        def green_callback(channel):
            #print("Green Button pressed")
            if (rs.state=="init"):
                print("Calling Robot.")
                GPIO.output(greenLED, True)
                
                rs.call_robot()
                
                #Websocket connection for robot call.
                ws.send(json.dumps({'method':'call', 'user': 'Hayden'}))
                print("A Robot is on the way.")
                
                
            else:
                print("A Robot has already been called.")
                
        def red_callback(channel):
    
            if (rs.state=="called"):
                print("Cancelling...")
                GPIO.output(redLED, True)
                
                rs.cancel_robot()
                
                #Websocket Connection for robot cancel.
                ws.send(json.dumps({'method':'cancel', 'user': 'Hayden'}))
                
                sleep(1)
                print("Robot Successfully Cancelled.")    
                GPIO.output(greenLED, False)
                GPIO.output(redLED, False)
            else:
                print("No incoming robots to cancel.")
    
        
        GPIO.add_event_detect(greenButton, GPIO.FALLING, callback=green_callback, bouncetime=200)
        GPIO.add_event_detect(redButton, GPIO.FALLING, callback=red_callback, bouncetime=1100)
        
        
        pause()               
                    
    if __name__ == "__main__":
       
        ws = create_connection("wss://lcas.lincoln.ac.uk/car/ws")
        ws.connect("wss://lcas.lincoln.ac.uk/car/ws")
        
        r = requests.get('http://0.0.0.0:8127/car/')
        r = requests.post('http://0.0.0.0:8127/car/', data = {'username':'Hayden'})
        
        ws.send(json.dumps({'method':'register','admin': True, 'user': 'admin'}))
        ws.send(json.dumps({'method':'get_state', 'user': 'Hayden'}))        
       
        getPositionData(gpsd)    
       
        
        main()
 
except KeyboardInterrupt:    
    #Exits with CTRL+C  
    ws.close()
    print ("Exiting")
  
#except:  
    #Catches all exceptions and errors. 
 #   print ("An error or exception occurred!")  
  
finally:  
    GPIO.cleanup() #clean exit  

