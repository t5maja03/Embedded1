# -*- coding: utf-8 -*-
# Title:       MQTT driver script
# Author:      Jarno Mattila (t5maja03)
# Date:        2017-11-07
# Description: Script reads 1-wire temperature sensor value 
#              (connected in GPIO) and publish Celsiue & Farenheit
#              converted values on MQTT subscription named as "testi"  
import os
import time
import subprocess

# GPIO and sensor drivers
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# sensor path
temp_sensor = '/sys/bus/w1/devices/28-00000828c929/w1_slave'

# function temp_raw())
# reads and returns raw lines from sensor file
def temp_raw():

   f = open(temp_sensor, 'r')
   lines = f.readlines()
   f.close()
   return lines

# function read_temp()
# Parses raw data line by line and 
# converts sensor value to Celsius and Farenheit degrees
def read_temp():

   # get raw data
   lines = temp_raw()
   
   # check trigger from the end of line 1 (0)
   # while it's YES
   while lines[0].strip()[-3:] != 'YES':
      
      # if not YES, sleep a momen and read again
      time.sleep(0.2)
      lines = temp_raw()
      
   # parse sensor valer from line 2 (1)
   temp_output = lines[1].find('t=')
   
   # convert value to Celcius and Farenhetis
   if temp_output != -1:
      temp_string = lines[1].strip()[temp_output+2:]
      temp_c = float(temp_string) / 1000.0
      temp_f = temp_c * 9.0 / 5.0 + 32.0
      
      # return values as array of floats
      return [temp_c, temp_f]

# main program (infinitive loop)      
while True:
   
   # read temperatures
   mqttstring = read_temp()
   
   # print out 
   # values rounded to 2 decimals and converted to string
   subprocess.call(["/usr/bin/mosquitto_pub", 
			"-t", "testi", 
			"-h", "mqtt.datakolmio.net", 
			"-p", "1883", 
			"-u", "t5maja03", 
			"-P", "tvt15smo", 
			"-m", str(round(mqttstring[0],2))+"°C "+ str(round(mqttstring[1],2))+"F"])
   # polling time 1 sec
   time.sleep(1)
