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

from guizero import App, Text, Box, PushButton
from gpiozero import LED


#app = App(title="Call A Robot", width=800, height=430)
#app.full_screen=True
#message = Text(app, text="Welcome to Call A Robot.")

#box = Box(app, layout="grid", grid=[1,0])
#button1 = PushButton(box, text="Call", grid=[0,0])
#button2 = PushButton(box, text="Cancel", grid=[1,0])
#button3 = PushButton(box, bg="blue", text="Load", grid=[2,0])

#app.display()
from tkinter import *
import tkinter as tk

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

# initialize tkinter
root = Tk()
app = Window(root)
label_text = StringVar()

# set window title
root.wm_title("Call A Robot")

text = Label(root,text="Welcome to Call A Robot.",foreground="red",
    font = "arial 20 bold",textvariable = label_text)
text.place(relx = 0.5, rely = 0.1, anchor = CENTER)

gbutton = Button(root,text="Call",bg="white", height=5, width=10)
#gbutton.grid(row = 2, column = 0, padx=5, pady=50, )
#gbutton.pack(padx=5, pady=50, side=tk.TOP)
gbutton.place(relx = 0.25, rely = 0.5, anchor = 'w') 
gbutton.config(highlightbackground="green")

rbutton = Button(root,text="Cancel",bg="white", height=5, width=10)
#rbutton.grid(row = 2, column = 1, padx=5, pady=50)
#rbutton.pack(padx=5, pady=50, side=tk.TOP)
rbutton.place(relx = 0.5, rely = 0.5, anchor = CENTER) 
rbutton.config(highlightbackground="red")

bbutton = Button(root,text="Load",bg="white", height=5, width=10)
bbutton.place(relx = 0.75, rely = 0.5, anchor = 'e') 
bbutton.config(highlightbackground="blue")

root.geometry("800x430")

def main_screen():
    mainscreen = Tk()   # create a GUI window 
    mainscreen.geometry("800x800") # set the configuration of GUI window 
    mainscreen.title(" Login Page") # set the title of GUI window
# create a Form label 
Label(text="Login Window Example", width="30", height="2", font=("Calibri", 13)).pack() 
Label(text="").pack() 
# create Login Button 
Button(text="Login", height="2", width="30").pack() 
Label(text="").pack() 
# create a register button
Button(text="Register", height="2",width="30").pack()



gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)

#Set the Buttons and LED pins
greenButton = 23
greenLED = 24

redButton = 16
redLED = 13

blueButton = 27
blueLED = 4



#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

#Setup the Buttons and LEDs
GPIO.setup(greenButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(greenLED,GPIO.OUT)

GPIO.setup(redButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(redLED,GPIO.OUT)

GPIO.setup(blueButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(blueLED,GPIO.OUT)



#Globals
lat = ''
long = ''

user = ''


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
        
        main_screen()

        #Main program
        print("Welcome to Call A Robot")
        label_text.set("Welcome to Call A Robot.")
        
        rs = RobotState()
        print ("The first state in the state machine is: %s" % rs.state)
            
                
        def green_callback(channel):
            print("Green button pressed")
            if (rs.state=="INIT"):
                print("Calling Robot.")
                label_text.set("Calling Robot.")
                
                GPIO.output(greenLED, True)
                gbutton.configure(bg = "green")
                
                rs.call_robot()
                
                #Websocket connection for robot call.
                ws.send(json.dumps({'method':'call', 'user': 'Hayden'}))
                print("A Robot is on the way.")
                label_text.set("A Robot is on the way")
                 
                #arrival testing
                #sleep(5)
                #robot_arrived_callback()
                
            else:
                print("A Robot has already been called.")
                label_text.set("A Robot has already been called.")
                sleep(1)
                label_text.set("A Robot is on the way")
                
        def red_callback(channel):
            print("Red button pressed")
            if (rs.state=="CALLED"):
                print("Cancelling...")
                label_text.set("Cancelling...")
                
                GPIO.output(redLED, True)
                rbutton.configure(bg = "red")
                
                rs.cancel_robot()
                
                #Websocket Connection for robot cancel.
                ws.send(json.dumps({'method':'cancel', 'user': 'Hayden'}))
                
                sleep(1)
                print("Robot Successfully Cancelled.")
                label_text.set("Robot Successfully Cancelled.")
                GPIO.output(greenLED, False)
                gbutton.configure(bg = "white")
                GPIO.output(redLED, False)
                rbutton.configure(bg = "white")
                sleep(1)
                label_text.set("Welcome to Call A Robot.")
                
            
            elif (rs.state=="ARRIVED"):
                print("Cancelling...")
                label_text.set("Cancelling...")
                
                GPIO.output(redLED, True)
                rbutton.configure(bg = "red")
                
                rs.cancel_load()
                
                #Websocket Connection for robot cancel.
                #ws.send(json.dumps({'method':'cancel', 'user': 'Hayden'}))
                
                sleep(1)
                print("Robot Load Successfully Cancelled.")    
                label_text.set("Robot Successfully Cancelled.")
                GPIO.output(blueLED, False)
                bbutton.configure(bg = "white")
                GPIO.output(redLED, False)
                rbutton.configure(bg = "white")
                
                sleep(1)
                label_text.set("Welcome to Call A Robot.")
            
            else:
                print("No incoming robots to cancel.")
                label_text.set("No incoming robots to cancel.")
                sleep(1)
                label_text.set("Welcome to Call A Robot.")
    
        def blue_callback(channel):
            if (rs.state=="ARRIVED"):
                
                label_text.set("Thank you the robot will now drive away.")
                #Websocket Connection for robot loaded.
                #ws.send(json.dumps({'method':'set_state', 'user': 'Hayden', 'state': 'LOADED'}))
                
                rs.robot_loaded()
                
                sleep(2)
                label_text.set("Welcome to Call A Robot.")
                
            else:
                print("No robots to load.")
                label_text.set("No robots to load.")
                sleep(1)
                label_text.set("Welcome to Call A Robot.")
        
        
        def robot_arrived_callback():
            rs.robot_arrived()
            GPIO.output(greenLED, False)
            gbutton.configure(bg = "white")
            
            print("Robot has arrived.")
            print("Please load the tray on the robot then press the blue button.")
            label_text.set("Please load the tray on the robot then press the blue button.")
                
            
            x = threading.Thread(target=blue_blink)
            x.start()
            
        def blue_blink():    
            
            while (rs.state=="ARRIVED"):
                
                bbutton.configure(bg = "blue")
                GPIO.output(blueLED, True)
                sleep(0.5)
                
                bbutton.configure(bg = "white")
                GPIO.output(blueLED, False)
                sleep(0.5) 
        
        
        
        #   if GPIO.event_detected(blueButton):
              #      print("Blue button pressed")
                
               # elif GPIO.event_detected(redButton):
                #    print("Red button pressed")
        
        GPIO.add_event_detect(greenButton, GPIO.RISING, callback=green_callback, bouncetime=1100)
        GPIO.add_event_detect(redButton, GPIO.FALLING, callback=red_callback, bouncetime=1100)
        GPIO.add_event_detect(blueButton, GPIO.FALLING, callback=blue_callback, bouncetime=1100)
        
        root.mainloop()
        #pause()               
                    
    if __name__ == "__main__":
        
        GPIO.output(greenLED, False)
        GPIO.output(blueLED, False)
        GPIO.output(redLED, False)
        ws = create_connection("wss://lcas.lincoln.ac.uk/car/ws")
        ws.connect("wss://lcas.lincoln.ac.uk/car/ws")
        
        #r = requests.get('http://lcas.lincoln.ac.uk/car/')
        #r = requests.post('http://lcas.lincoln.ac.uk/car/', data = {'username':'Hayden'})
        
        #ws.send(json.dumps({'method':'register','admin': True, 'user': 'admin'}))
        #ws.send(json.dumps({'method':'get_state', 'user': 'Hayden'}))        
       
        #getPositionData(gpsd)    
       
        
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
