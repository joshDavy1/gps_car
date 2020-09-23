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
from json import dumps, loads, load
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


from tkinter import *
import tkinter as tk


#Globals
lat = ''
long = ''

user =''



class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master


#def MainPage():
    
    
# initialize tkinter
root = Tk()
app = Window(root)
label_text = StringVar()

user_text = StringVar()

# set window title
root.wm_title("Call A Robot")

text = Label(root,text="Welcome to Call A Robot.",foreground="red",
font = "arial 20 bold",textvariable = label_text)
text.place(relx = 0.5, rely = 0.1, anchor = CENTER)

userText = Label(root,text="",foreground="blue",
font = "arial 12 normal",textvariable = user_text)
userText.place(relx = 0.5, rely = 0.2, anchor = CENTER)

gbutton = Button(root,text="Call",bg="white", height=5, width=10)
gbutton.place(relx = 0.25, rely = 0.5, anchor = 'w') 
gbutton.config(highlightbackground="green")

rbutton = Button(root,text="Cancel",bg="white", height=5, width=10)
rbutton.place(relx = 0.5, rely = 0.5, anchor = CENTER) 
rbutton.config(highlightbackground="red")

bbutton = Button(root,text="Load",bg="white", height=5, width=10)
bbutton.place(relx = 0.75, rely = 0.5, anchor = 'e') 
bbutton.config(highlightbackground="blue")

root.geometry("800x430")
#root.attributes("-fullscreen", True)      
    

    
def LoginPage():
    login_screen=Tk()
    login_screen.title("User Login")
    login_screen.focus_force()
    login_screen.geometry("300x250")
    #login_screen.attributes("-fullscreen", True)  
    loginText = Label(login_screen, text="Please enter login details", font = "arial 12 bold", foreground="red")
    loginText.place(relx = 0.5, rely = 0.1, anchor = CENTER)
    usernameText = Label(login_screen, text="Username:")
    usernameText.place(relx = 0.2, rely = 0.3, anchor = CENTER)
    username_login_entry = Entry(login_screen)
    username_login_entry.place(relx = 0.5, rely = 0.4, anchor = CENTER, width = 270)
    
    def submit(): 
        global user
        user = username_login_entry.get()
        print("The user is : " + user)
        login_screen.destroy()
        main()
    
    subButton = Button(login_screen, text="Login", width=30, height=1, command = submit, bg = "green")
    subButton.place(relx = 0.5, rely = 0.6, anchor = CENTER)
    login_screen.mainloop()



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



try:
   
    def getPositionData(gps):
            
            global lat
            global long
            
            lat = ''
            long = ''
            
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
                            
            ws.send(json.dumps({'method':'location_update', 'row':'A1', 'user': user, 'latitude':lat, 'longitude':long, 'accuracy':epx, 'rcv_time':time}))    
    
    def main():
       
        #Main program
        print("Welcome to Call A Robot")
        label_text.set("Welcome to Call A Robot.")
        
        rs = RobotState()
        print("The first state in the state machine is: %s" % rs.state)
        
        print("Logged in: " + user)
        user_text.set("User: " + user)
                
        def green_callback(channel):
            
            
            print("Green button pressed")
            if (rs.state=="INIT"):
                print("Calling Robot.")
                label_text.set("Calling Robot.")
                
                GPIO.output(greenLED, True)
                gbutton.configure(bg = "green")
                
                rs.call_robot()
                
                #Websocket connection for robot call.
                ws.send(json.dumps({'method':'call', 'user': user}))
                print("A Robot is on the way.")
                label_text.set("A Robot is on the way")
                
                y = threading.Thread(target=check_arrived)
                y.start()
                
                z = threading.Thread(target=check_location)
                z.start()
               
            
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
                ws.send(json.dumps({'method':'cancel', 'user': user}))
                
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
                ws.send(json.dumps({'method':'cancel', 'user': user}))
                
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
                ws.send(json.dumps({'method':'set_state', 'user': user, 'state': 'LOADED'}))
                
                rs.robot_loaded()
                
                sleep(2)
                label_text.set("Welcome to Call A Robot.")
                ws.send(json.dumps({'method':'set_state', 'user': user, 'state': 'INIT'}))
                rs.user_reset()
                
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
        
        def check_arrived():
            
            # Robot arrival 
            ws.send(json.dumps({'method':'get_states', 'user': user}))
            
            while rs.state=="CALLED":
                
                sleep(5)
                
                jsondata = ws.recv()
                
                data = loads(jsondata) 
                
                states = data['states']
                
                for key in states:
                    if key == user:
                        print(states[key])
                        if states[key] == "ARRIVED":
                            print("Robot Arrived")
                            robot_arrived_callback()
            
            
        def check_location():

            while rs.state=="CALLED":
                sleep(5)
                getPositionData(gpsd) 
        
        
        #   if GPIO.event_detected(blueButton):
              #      print("Blue button pressed")
                
               # elif GPIO.event_detected(redButton):
                #    print("Red button pressed")
        
        GPIO.add_event_detect(greenButton, GPIO.RISING, callback=green_callback, bouncetime=1100)
        GPIO.add_event_detect(redButton, GPIO.FALLING, callback=red_callback, bouncetime=1100)
        GPIO.add_event_detect(blueButton, GPIO.FALLING, callback=blue_callback, bouncetime=1100)
        
        
        root.focus_force()
        #getPositionData(gpsd) 
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
       
           
        
        LoginPage()
        
        
        
        
 
except KeyboardInterrupt:    
    #Exits with CTRL+C  
    ws.close()
    print ("Exiting")
  
#except:  
    #Catches all exceptions and errors. 
 #   print ("An error or exception occurred!")  
  
finally:  
    GPIO.cleanup() #clean exit  



