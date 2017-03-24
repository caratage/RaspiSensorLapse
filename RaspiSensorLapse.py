 # Import some frameworks
import os
import sys
import time
import RPi.GPIO as GPIO
from datetime import datetime
# BME280 sensor lib
from Adafruit_BME280 import *
sensor = BME280(mode=BME280_OSAMPLE_8)

# Set timelapse interval in seconds
interval = 60

# Set Raspistill capture options
flags = "-n" # -n nopreview
imgWidth = 1440 # Max = 3280
imgHeight = 1080 # Max = 2464
sharpness = 10 # -sh     Set image sharpness (-100 - 100)
saturation = 20 # -sa   Set image saturation (-100 - 100)
contrast = 10 # -co      Set image contrast (-100 - 100)
brightness = 50 # -br Set image brightness (0 - 100)
iso = 100 # Set capture ISO (100 - 800)
quality = 100 # 0 - 100
rotation = 180
drc = "high" # off / low / medium / high // DRC changes the images by increasing the range of dark areas, and decreasing the brighter areas. This can improve the image in low light areas. 
evComp = 1 # Set EV compensation (-10 - 10)
whiteBalance = "sun" # off / auto / sun / cloud / shade / tungsten / fluorescent / incandescent / flash / horizon
meteringMode = "matrix" # average / spot / backlit / matrix

# Set log directory
logDir = "/home/pi/shares/log/"
# Set output directory
outputDir = "/home/pi/shares/timelapse/"
# Set output prefix
outputPrefix = "timelapse-"
# Get sunwait info file
sunwaitInfo = "/home/pi/var/lightordark"
# Set file serial
fileSerial = 1

# Run indefinite loop
while True:

   # Get current time, set format
   d = datetime.now()
   year = "%04d" % (d.year)
   day = "%02d" % (d.day)
   month = "%02d" % (d.month)
   hour = "%02d" % (d.hour)
   mins = "%02d" % (d.minute)
   sec = "%02d" % (d.second)
   datestamp = str(year) + str(month) + str(day)
   timestamp = str(hour) + ":" + str(mins) + ":" + str(sec)

   # Set output folder
   folderToSave = str(outputDir) + str(outputPrefix) + str(datestamp)
   # Create new folder if needed, usually once per day
   if not os.path.exists(folderToSave):
      os.makedirs(folderToSave)
      # Reset the initial serial for saved images to 1
      fileSerial = 1

   # Set FileSerialNumber to 000X using four digits
   fileSerialNumber = "%04d" % (fileSerial)

   # Set log file
   logToWrite = str(logDir) + str(outputPrefix)  + str(datestamp) + ".log"
   # Create new file if needed
   if not os.path.exists(logToWrite):
      open(logToWrite, 'w').close()
   # Open log file in 'append' mode to start writing to EOF
   saveout = sys.stdout
   fsock = open(logToWrite, 'a')
   sys.stdout = fsock 

   # Get sensor data, set format
   degrees = sensor.read_temperature()
   degrees = '{0:0.1f}\'C'.format(degrees)
   pascals = sensor.read_pressure()
   hectopascals = pascals / 100
   pascals = '{0:0.0f}hPa'.format(hectopascals)
   humidity = sensor.read_humidity()
   humidity  = '{0:0.0f}%'.format(humidity)

   # Print sensor data info
   print str(fileSerialNumber) + " " + str(timestamp) + " *** DATA: " + str(degrees) + " " + str(pascals) + " " + str(humidity)

   # Check for light. Open file written by sunwait in crontab -e
   f = open(sunwaitInfo)
   # Read status
   status = f.readline()

   # Check status and take picture
   if 'light' in status:

      # Get current time, set format
      d = datetime.now()
      year = "%04d" % (d.year)
      day = "%02d" % (d.day)
      month = "%02d" % (d.month)
      hour = "%02d" % (d.hour)
      mins = "%02d" % (d.minute)
      sec = "%02d" % (d.second)
      datestamp = str(year) + str(month) + str(day)
      timestamp = str(hour) + ":" + str(mins) + ":" + str(sec)

      # Camera status
      print str(fileSerialNumber) + " " + str(timestamp) + " *** Camera: ON"

      try:
         # Capture the image 
         os.system("raspistill " + str(flags) + " -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(folderToSave) + "/" + str(datestamp) + "_" + str(hour) + str(mins) + "_" + str(fileSerialNumber) + ".jpg  -sh " + str(sharpness) + " -sa " + str(saturation) + " -co " + str(contrast) + " -br " + str(brightness) + " -q " + str(quality) + " -rot " + str(rotation) + " -ev " + str(evComp) + " -awb " + str(whiteBalance) + " -mm " + str(meteringMode) + " -drc " + str(drc) + " -ae 24,0x80808080,0x8080FF80 -a 4 -a \"%a %d.%m.%Y %H:%M " + str(degrees) + " " + str(pascals) + " " + str(humidity) + "\"")
      
      except:
         # Error
         print str(fileSerialNumber) + " " + str(timestamp) + " *** ERROR: " + sys.exc_info()[0]

      else:
         # Get current time, set format
         d = datetime.now()
         year = "%04d" % (d.year)
         day = "%02d" % (d.day)
         month = "%02d" % (d.month)
         hour = "%02d" % (d.hour)
         mins = "%02d" % (d.minute)
         sec = "%02d" % (d.second)
         datestamp = str(year) + str(month) + str(day)
          timestamp = str(hour) + ":" + str(mins) + ":" + str(sec) 

         # Capture status
         print str(fileSerialNumber) + " " + str(timestamp) + " *** Capture: OK"

   # if 'dark'
   else:

      # Camera status
      print str(fileSerialNumber) + " " + str(timestamp) + " *** Camera: OFF"

   # Save and close log file
   sys.stdout = saveout
   fsock.close()
   f.close()

   # Update serial
   fileSerial += 1

   # Wait before it loops again
   time.sleep(int(interval)) 