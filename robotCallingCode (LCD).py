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

#Set up the LCD screen
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
    cols=16, rows=2, dotsize=8,
    charmap='A02',
    auto_linebreaks=True,
    backlight_enabled=True)
lcd.clear()

#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

try:
    def main():
        
        lcd.write_string('Welcome to\r\nCall a Robot.')
        
        #Set the Buttons and LED pins
        greenButton = 23
        greenLED = 24
    
        redButton = 16
        redLED = 20
    
        blueButton = 19
        blueLED = 26
    
        #Setup the Buttons and LEDs
        GPIO.setup(greenButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(greenLED,GPIO.OUT)
    
        GPIO.setup(redButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(redLED,GPIO.OUT)
    
        GPIO.setup(blueButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(blueLED,GPIO.OUT)
        
        GPIO.add_event_detect(greenButton, GPIO.RISING, bouncetime=200)
        GPIO.add_event_detect(redButton, GPIO.RISING, bouncetime=200)
        GPIO.add_event_detect(blueButton, GPIO.RISING, bouncetime=200)
        
        #Flags
        greenFlag        = False
        redFlag          = False
        blueFlag         = False
        arrivedFlag      = False
        loadedFlag       = False
        loadOnFlag       = False
        loadCanceledFlag = False
        
        #Button states
        #Arrived button for testing robot arrival
        arrivedButton = 21
        GPIO.setup(arrivedButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        
        #Main program
        while True:
            green_button_state = GPIO.input(greenButton)
            if green_button_state==0:
            #If green robot call button is pressed.    
                sleep(0.5)
                if greenFlag==False:
                    greenFlag=True
                    GPIO.output(greenLED, True)
                    print("Calling Robot.")
                    
                    lcd.clear()
                    lcd.write_string('Calling Robot.')
                    
                    #TODO Websocket connection for robot call.        
                    sleep(2.0)# simulate websocket.
                    print("A Robot is on the way.")
                    
                    lcd.clear()
                    lcd.write_string('A Robot is on the way.')
                
                else:
                    print("A Robot has already been called.")
                    
                    lcd.clear()
                    lcd.write_string('A Robot has already been called.')
                    sleep(2.0)
                    lcd.clear()
                    lcd.write_string('A Robot is on the way.')
            
            if greenFlag==1:
                GPIO.output(greenLED, True)
            else:
                GPIO.output(greenLED, False)
            
            if GPIO.event_detected(redButton):
                # If the red cancel button is pressed.
                sleep(0.5)
                if redFlag==False:
                    if greenFlag==True:
                        print("Cancel Robot.")
                        greenFlag=False
                        redFlag=True
                        
                        lcd.clear()
                        lcd.write_string('Cancel Robot')
                        
                    else:
                        print("No incoming robots to cancel.")
                        lcd.clear()
                        lcd.write_string('No incoming Robot to cancel.')
                        sleep(2.0)
                        lcd.clear()
                        lcd.write_string('Welcome to\r\nCall a Robot.')
            
            if redFlag==True:
                GPIO.output(redLED, True)
                print("Cancelling...")
                
                lcd.clear()
                lcd.write_string('Cancelling...')
                
                #TODO Websocket Connection for robot cancel.
                sleep(2.0)#Simulate websocket.
                print("Robot Successfully Cancelled.")
                
                lcd.clear()
                lcd.write_string('Robot Successfully Cancelled. ')
                sleep(2.0)
                lcd.clear()
                lcd.write_string('Welcome to\r\nCall a Robot.')
                
                redFlag=False
            else:
                GPIO.output(redLED, False)
            
            #Run if blue button is pressed unprompted.
            if GPIO.event_detected(blueButton):
                if arrivedFlag==False:
                    print("There are currently no robots to load.")
                    
                    lcd.clear()
                    lcd.write_string('No Robot to load. ')
                    sleep(2.0)
                    lcd.clear()
                    lcd.write_string('Welcome to\r\nCall a Robot.')
        
            ########## ROBOT ARRIVAL TESTING ###############
            arrived_button_state = GPIO.input(arrivedButton)
            #TODO change over to websocket connection of arrived robot instead of button input.
            if arrived_button_state==0:
                sleep(0.5)
                arrivedFlag=True
                
                if arrivedFlag==True:
                    greenFlag=False
                    print("Robot has arrived.")
                    print("Please load the tray on the robot then press the blue button.")
                    
                    lcd.clear()
                    lcd.write_string('Robot has arrived. ')
                    sleep(2.0)
                    lcd.clear()
                    lcd.write_string('Load Robot\r\nPress blue.')
                    
                    while (loadedFlag is False):
                        GPIO.output(blueLED, True)
                        sleep(0.5)
                        GPIO.output(blueLED, False)
                        sleep(0.5)
                        if GPIO.event_detected(blueButton):
                            #If blue loaded button is pressed.
                            loadOnFlag=True 
                            loadedFlag=True
                        
                        if GPIO.event_detected(redButton):
                            #If red cancel button is pressed. 
                            loadCanceledFlag=True
                            loadedFlag=True 
                    
                    if loadOnFlag==True:
                        print("Robot loaded, thank you")
                        
                        lcd.clear()
                        lcd.write_string('Robot loaded, thank you. ')
                        sleep(3.0)
                        lcd.clear()
                        lcd.write_string('Welcome to\r\nCall a Robot.')
                        
                        #TODO Websocket connection for loaded robot.   
                        loadOnFlag=False 
                    
                    if loadCanceledFlag==True:
                        GPIO.output(redLED, True)
                        print("Loading cancelling...")
                        
                        lcd.clear()
                        lcd.write_string('Robot Successfully Cancelled. ')
                
                        #TODO Websocket Connection for robot cancel.
                        sleep(2.0)#Simulate websocket.
                        print("Robot loading cancelled.")
                        
                        lcd.clear()
                        lcd.write_string('Robot loading cancelled.')
                        lcd.clear()
                        lcd.write_string('Welcome to\r\nCall a Robot.')
                        
                        loadCanceledFlag=False 
                    
                    #Reset flags after the robot has left after loading is finished.
                    arrivedFlag=False
                    loadedFlag=False
                       
                    
    if __name__ == "__main__":
        main()
 
except KeyboardInterrupt:    
    #Exits with CTRL+C  
    lcd.clear()
    print ("Exiting")
  
except:  
    #Catches all exceptions and errors. 
    print ("An error or exception occurred!")  
  
finally:  
    GPIO.cleanup() #clean exit  
