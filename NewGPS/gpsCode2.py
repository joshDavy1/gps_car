###############################
#
# File   : gpsCode.py
# Author : Hayden Coe
# Date   : 24/08/2020
#
##############################


import threading
from gps import *
import time
import serial
import re


class GPS(threading.Thread):
    def __init__(self, gps_data_callback = None):
        super(GPS, self).__init__()
        self.gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
        self.callback = gps_data_callback
        #               (lat, lon, epx, epy, ts)
        self.last_data = (-1, -1, -1, -1, -1)
        self.has_more_data = True
        self.stop_event = threading.Event()

        
        

    def _getPositionData(self):
            lat = -1
            lon = -1
            epx = -1
            epy = -1
            

            regex = r"(\+CGPSINFO: )[^\\]*"

            gpsATBack = "+CGPSINFO: "

            gpsATResponseNoSignal = "+CGPSINFO: ,,,,,,,,"
            
            while True:

                ser = serial.Serial('/dev/ttyS0',115200)
                ser.flushInput()        

                print("Requesting GPS Data.....")
                ser.write(("AT+CGPSINFO" + "\r\n").encode())

                if ser.inWaiting():
                    rawSerRead = ser.read(ser.inWaiting())

                    decodedSerRead = rawSerRead.decode()

                    reprDecodedSerRead = repr(decodedSerRead)

                    #print(reprDecodedSerRead)

                    match = re.search(regex, reprDecodedSerRead)

                    if match: # if the regex search method found a valid AT response for gps

                        gpsATResponse = match.group() # actual AT response given back

                        if gpsATResponse != gpsATResponseNoSignal: # if the gps AT response was not no signal
                            
                            #print(rawGPSData)
                            gpsATResponseNoBack = gpsATResponse[len(gpsATBack):] # substring the full AT command giving back just the values, no back characters
                            #print(gpsATResponseNoBack)
                            gpsData = gpsATResponseNoBack.split(",") # gps data is now represented as an array/list
                            #print(gpsData)

                            ddLat = float(gpsData[0][:2]) # dd of lat
                            mmLat = float(gpsData[0][2:]) # mm.mmmmmm of lat

                            dddLog = float(gpsData[2][:3]) # ddd of log
                            mmLog = float(gpsData[2][3:]) # mm.mmmmmm of log


                            pureDegLat = round(((mmLat / 60) + ddLat) * (1 if gpsData[1] == "N" else -1), 13)
                            pureDegLog = round(((mmLog / 60) + dddLog) * (1 if gpsData[3] == "E" else -1), 13)

                            positionLatLog = str(pureDegLat) + ", " + str(pureDegLog)
                            print("GPS Online, Location: " + positionLatLog)
                            
                            lat = pureDegLat
                            lon = pureDegLog
                            
                            return lat, lon, epx, epy, time.time()
                        
                        else: # else if there was the response of no gps signal
                            print("GPS Online, No GPS Signal Detected")             
                    else:
                        print("Unexpected GPS Response")
                
                time.sleep(1)
                
                

    def set_callback(self, cb):
        self.callback = cb        

    def get_latest_data(self):
        return self.last_data

    def has_more_data(self):
        return self.has_more_data

    def run(self):
        while not self.stop_event.is_set():
            # get latest postion
            lat, lon, epx, epy, ts = self._getPositionData() # blocking

            self.last_data = (lat, lon, epx, epy, ts)
            
            # call callback 
            if self.callback is not None:
                self.callback(lat, lon, epx, epy, ts)

    def stop(self):
        self.stop_event.set()
        
        
