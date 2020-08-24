import RPi.GPIO as GPIO
from time import sleep
import logging
import threading

#Set warnings off (optional)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

try:
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
	
	    while True:
	        green_button_state = GPIO.input(greenButton)
	        if green_button_state==0:
	            sleep(0.5)
	            if greenFlag==False:
	                greenFlag=True
	                print("Calling Robot.")
	                #TODO Wesocket connection for robot call.        
	                print("Robot on the way.")
	            else:
	                print("Robot has already been called.")
	                
	        if greenFlag==1:
	            GPIO.output(greenLED, True)
	        else:
	            GPIO.output(greenLED, False)
	        
	        if GPIO.event_detected(redButton):
	            sleep(0.5)
	            if redFlag==False:
	                # if the red button is pressed to on.
	                if greenFlag==True:
	                    print("Cancel Robot.")
	                    greenFlag=False
	                    redFlag=True
	                else:
	                    print("No incoming robots to cancel.")
	            
	        if redFlag==True:
	            GPIO.output(redLED, True)
	            print("Cancelling...")
	            #TODO Websocket Connection for robot cancel.
	            sleep(2.0)
	            print("Robot Successfully Cancelled.")
	            redFlag=False
	        else:
	            GPIO.output(redLED, False)
	        
	        #Run if blue button is pressed unprompted.
	        if GPIO.event_detected(blueButton):
	            if arrivedFlag==False:
	                print("There are currently no robots to load.")
	    
	        ########## ROBOT ARRIVAL TESTING ###############
	        arrived_button_state = GPIO.input(arrivedButton)
	        #TODO change over to websocket connection of arrived robot.
	        if arrived_button_state==0:
	            sleep(0.5)
	            arrivedFlag=True
	            
	            if arrivedFlag==True:
	                greenFlag=False
	                print("Robot has arrived.")
	                print("Please load the tray on the robot then press the blue button.")
	                
	                while (loadedFlag is False):
	                    GPIO.output(blueLED, True)
	                    sleep(0.5)
	                    GPIO.output(blueLED, False)
	                    sleep(0.5)
	                    if GPIO.event_detected(blueButton):
	                        #blue button press
	                        loadOnFlag=True 
	                        loadedFlag=True
	                    
	                    if GPIO.event_detected(redButton):
	                        #red button press
	                        loadCanceledFlag=True
	                        loadedFlag=True 
	                
	                if loadOnFlag==True:
	                    print("Robot loaded, thank you")
	                    #TODO Websocket connection for loaded robot.   
	                    loadOnFlag=False 
	                
	                if loadCanceledFlag==True:
	                    GPIO.output(redLED, True)
	                    print("Loading cancelling...")
	                    #TODO Websocket Connection for robot cancel.
	                    sleep(2.0)
	                    print("Robot loading cancelled.")
	                    loadCanceledFlag=False 
	                
	                #Reset flags after the robot has left after loading is finished.
	                arrivedFlag=False
	                loadedFlag=False
	                   
	                
	if __name__ == "__main__":
	    main()
 
except KeyboardInterrupt:    
    #Exits with CTRL+C  
    print "Exiting"
  
except:  
    #Catches all exceptions and errors. 
    print "An error or exception occurred!"  
  
finally:  
    GPIO.cleanup() #clean exit  
