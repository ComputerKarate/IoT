#!/usr/bin/python3

# TODO Add function to create a default config.ini if the file is missing
# NOTE: Removing config.ini from repo temporarily

import paho.mqtt.client as mqtt
import time
import logging as log
import configparser
from io import StringIO
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')

log.basicConfig(filename=config['DEFAULT']['LOG_FILE'], level=log.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

def on_message(mqttc, obj, msg):
    FormattedPayload = str(msg.payload, 'utf-8')

    if "TEMP=" in FormattedPayload:
        rawMsg = StringIO(FormattedPayload)
        tmpMsg = np.genfromtxt(rawMsg, dtype=[('EventDate', 'S10'), ('EventTime', 'S8'), ('DeviceID', 'S20'),('TempValue', 'S20')], delimiter="|")
        FormattedEventDate = str(tmpMsg['EventDate'], 'utf-8')
        FormattedEventTime = str(tmpMsg['EventTime'], 'utf-8')
        FormattedDeviceID = str(tmpMsg['DeviceID'], 'utf-8')
        FormattedTemperature = str(tmpMsg['TempValue'], 'utf-8')
        FormattedTemperature = FormattedTemperature[5:]

        print(FormattedEventDate + "|" + FormattedEventTime + "|" + FormattedDeviceID + "|" + config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + FormattedTemperature)
        log.info(FormattedEventDate + "|" + FormattedEventTime + "|" + FormattedDeviceID + "|" + config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + FormattedTemperature)

def on_connect(mqttc, obj, flags, rc):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        print("Connection return code: " + str(rc))
    log.info("Connection return code: " + str(rc))

    # Subscribe request
    MQTTClient.subscribe("test")

def on_publish(mqttc, obj, mid):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        print("mid: " + str(mid))
    log.info("Publish return code mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))
    log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        print(string)


# Initial Client ID
MQTTClient = mqtt.Client(config['DEFAULT']['CLIENTID'])

# Function to process messages
MQTTClient.on_message = on_message

# Function to process the connection
MQTTClient.on_connect = on_connect

# Publish results
MQTTClient.on_publish = on_publish

# Results of subscribing to a channel
MQTTClient.on_subscribe = on_subscribe

# Uncomment to enable verbose debug messages
#MQTTClient.on_log = on_log

# Message broker
# TODO Investigate configparser with timeout and port
MQTT_Host = config['DEFAULT']['MQTT_HOST']
print("MQTT_Host = " + MQTT_Host)
MQTT_Port = config['DEFAULT']['MQTT_PORT']
print("MQTT_Port = " + str(MQTT_Port))
MQTT_Timeout = config['DEFAULT']['MQTT_TIMEOUT']
print("MQTT_Timeout = " + str(MQTT_Timeout))
MQTTClient.connect(config['DEFAULT']['MQTT_HOST'], 1883, 60)

# Just what it says...forever
MQTTClient.loop_forever()


