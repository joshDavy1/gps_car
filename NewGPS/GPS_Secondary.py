import serial
import time
import re

ser = serial.Serial('/dev/ttyS0',115200)
ser.flushInput()

regex = r"(\+CGPSINFO: )[^\\]*"

gpsATBack = "+CGPSINFO: "

gpsATResponseNoSignal = "+CGPSINFO: ,,,,,,,,"

try: 
    while True:

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

                    #<lat> gpsData[0]
                    #Latitude of current position. Output format is ddmm.mmmmmm

                    #<N/S> gpsData[1]
                    #N/S Indicator, N=north or S=south

                    #<log> gpsData[2]
                    #Longitude of current position. Output format is dddmm.mmmmmm

                    #<E/W> gpsData[3]
                    #E/W Indicator, E=east or W=west

                    #<date> gpsData[4]
                    #Date. Output format is ddmmyy

                    #<UTC time> gpsData[5]
                    #UTC Time. Output format is hhmmss.s

                    #<alt> gpsData[6]
                    #MSL Altitude. Unit is meters.

                    #<speed> gpsData[7]
                    #Speed Over Ground. Unit is knots.

                    #<course> gpsData[8]
                    #Course. Degrees.


                    #----Conversion of (d)dd and mm.mmmm. format into pure degrees (Google Maps API)
                    #https://google-maps-api.narkive.com/iKF7UXxr/how-to-convert-coordinate-in-ddmm-mmmm-to-googlemaps-format

                    ddLat = float(gpsData[0][:2]) # dd of lat
                    mmLat = float(gpsData[0][2:]) # mm.mmmmmm of lat

                    dddLog = float(gpsData[2][:3]) # ddd of log
                    mmLog = float(gpsData[2][3:]) # mm.mmmmmm of log


                    pureDegLat = round(((mmLat / 60) + ddLat) * (1 if gpsData[1] == "N" else -1), 13)
                    pureDegLog = round(((mmLog / 60) + dddLog) * (1 if gpsData[3] == "E" else -1), 13)

                    positionLatLog = str(pureDegLat) + ", " + str(pureDegLog)
                    print("GPS Online, Location: " + positionLatLog)
                else: # else if there was the response of no gps signal
                    print("GPS Online, No GPS Signal Detected")             
            else:
                print("Unexpected GPS Response")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("stopping....")
    ser.close()