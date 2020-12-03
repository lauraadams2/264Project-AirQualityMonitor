#!/usr/bin/env python

from __future__ import print_function
import time
from datetime import datetime
import paho.mqtt.publish as publish
import psutil
from sds011 import *
import aqi

sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)

def get_data(n=3):
	sensor.sleep(sleep=False)
	pm25 = 0
	pm10 = 0
	time.sleep(10)
	for i in range (n):
		x = sensor.query()
		pm25 = pm25 + x[0]
		pm10 = pm10 + x[1]
		time.sleep(2)
	pm25 = round(pm25/n, 1)
	pm10 = round(pm10/n, 1)
	sensor.sleep(sleep=True)
	time.sleep(2)
	return pm25, pm10


def conv_aqi(pm25, pm10):
	aqi25 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pm25))
	aqi10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pm10))
	return aqi25, aqi10


def save_log():
	with open("/home/rambler/264/AirQualityMonitor/264Project-AirQualityMonitor/air_quality.csv", "a") as log:
		dt = datetime.now()
		log.write("{},{},{},{},{}\n".format(dt, pm25, aqi25, pm10, aqi10))
	log.close()


channelID = "1246085"
writeAPIKey = "0VGYSVMG9EURZGK6"

mqttUsername = "mwa0000020498094"
mqttAPIKey = "CF16L07FWJHRDS82"

mqttHost = "mqtt.thingspeak.com"

useUnsecuredTCP = True
useUnsecuredWebsockets = False
useSSLWebsockets = False

if useUnsecuredWebsockets:
	tTransport = "websockets"
	tPort = 80
	tTLS = None

if useUnsecuredTCP:
	tTransport = "tcp"
	tPort = 1883
	tTLS = None

topic = "channels/" + channelID + "/publish/" + writeAPIKey

"""
send data to thingspeak.com using 1 of 2 possible connection types: unsecured TCP or unsecured websockets
"""
while True:
	pm25, pm10 = get_data()
	aqi25, aqi10 = conv_aqi(pm25, pm10)

	payload = "field1=" + str(pm25) + "&field2=" + str(aqi25) + "&field3=" + str(pm10) + "&field4=" + str(aqi10)
	try:
		publish.single(topic, payload, hostname=mqttHost, transport=tTransport, port=tPort, tls=tTLS, auth={'username':mqttUsername,'password':mqttAPIKey})
		save_log()
		print ("[PM2.5] = ", pm25, "[AQI2.5] = ", aqi25, "[PM10] = ", pm10, "[AQI10] = ", aqi10)
		time.sleep(60)

	except (KeyboardInterrupt):
		break
	except:
		print ("[INFO] Failure in sending data")
		time.sleep(12)
"""
save to local csv
"""
"""
while(True):
	pmt_2_5, pmt_10 = get_data()
	aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
	try:
		save_log()
	except:
		print ("[INFO] Failure in logging data")
	time.sleep(60)
"""
