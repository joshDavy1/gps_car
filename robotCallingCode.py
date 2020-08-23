import RPi.GPIO as GPIO
from time import sleep
import logging
import threading

#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

def main(): 

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
    
    GPIO.add_event_detect(blueButton, GPIO.RISING, bouncetime=200)
    
    #Flags
    greenFlag = 0
    redFlag = 0
    blueFlag = 0
    loadedFlag = False
    arrivedFlag = False

    #Button states
    #Arrived button for testing robot arrival
    arrivedButton = 21
    GPIO.setup(arrivedButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    while True:
        green_button_state = GPIO.input(greenButton)
        if green_button_state==0:
            sleep(0.5)
            if greenFlag==0:
                greenFlag=1
                print("Calling Robot.")
                #TODO Wesocket connection for robot call.        
                print("Robot on the way.")
            
            else:
                print("Robot has already been called.")
                
                
        if greenFlag==1:
            GPIO.output(greenLED, True)
                
        else:
            GPIO.output(greenLED, False)
        
        
        
        red_button_state = GPIO.input(redButton)
        if red_button_state==0:
            sleep(0.5)
            if redFlag==0:
                # if the red button is pressed to on.
                if greenFlag==1:
                    print("Cancel Robot.")
                    greenFlag=0
                    redFlag=1
                else:
                    print("No incoming robots to cancel.")
            
    
        if redFlag==1:
            GPIO.output(redLED,GPIO.HIGH)
            print("Cancelling...")
            #TODO Websocket Connection for robot cancel.
            sleep(2.0)
            print("Robot Successfully Cancelled.")
            redFlag=0
        else:
            GPIO.output(redLED, False)
        
        #Run if blue button is pressed unprompted.
        if GPIO.event_detected(blueButton):
            if arrivedFlag==0:
                print("There are currently no robots to load.")
    
        ########## ROBOT ARRIVAL TESTING ###############
        arrived_button_state = GPIO.input(arrivedButton)
        #TODO change over to websocket connection of arrived robot.
        if arrived_button_state==0:
            sleep(0.5)
            arrivedFlag=True
            
            
            if arrivedFlag==True:
                greenFlag=0
                print("Robot has arrived.")
                print("Please load the tray on the robot then press the blue button.")
                
                while (loadedFlag is False):
                    print("Blink Loop")
                    GPIO.output(blueLED, True)
                    sleep(0.5)
                    GPIO.output(blueLED, False)
                    sleep(0.5)
                    if GPIO.event_detected(blueButton):
                        print("blue button press")
                        loadedFlag=True
                
                print("Robot loaded, thank you")
                arrivedFlag=False
                loadedFlag=False
                #TODO Websocket connection for loaded robot.      
                
                
            
            
if __name__ == "__main__":
    loadFlag=False
    main()
                


    
            