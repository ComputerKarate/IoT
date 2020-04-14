#!/usr/bin/python3

# TODO Add function to create a default config.ini if the file is missing

import paho.mqtt.client as mqtt
import time
import logging as log
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

log.basicConfig(filename=config['DEFAULT']['LOG_FILE'], level=log.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

def on_message(mqttc, obj, msg):
    localtime = time.localtime(time.time())
    # print(localtime) # Uncomment to see the structure of localtime

    date_string = str(localtime.tm_mon) + "/" + str(localtime.tm_mday) + "/" + str(localtime.tm_year)
    time_string = str(localtime.tm_hour) + ":" + str(localtime.tm_min) + ":" + str(localtime.tm_sec)

    if "TEMP=" in str(msg.payload):
        formatted_temp = str(msg.payload[5:], 'utf-8') # Capture the message after "TEMP="
        if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
            print(config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + formatted_temp + "|" + date_string + "|" + time_string + "|TEMP")
        log.info(config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + formatted_temp + "|" + date_string + "|" + time_string + "|TEMP")

    if "HUMIDITY=" in str(msg.payload):
        formatted_humidity = str(msg.payload[9:], 'utf-8') # Capture the message after "HUMIDITY="
        if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
            print(config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + formatted_humidity + "|" + date_string + "|" + time_string + "|HUMIDITY")
        log.info(config['DEFAULT']['SUBSCRIBE_CHANNEL'] + "|" + formatted_humidity + "|" + date_string + "|" + time_string + "|HUMIDITY")

def on_connect(mqttc, obj, flags, rc):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        print("Connection return code: " + str(rc))
    log.info("Connection return code: " + str(rc))

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
MQTTClient.connect(config['DEFAULT']['MQTT_HOST'], XXXX, 60)

# Subscribe request
MQTTClient.subscribe("test", 0)

# Just what it says...forever
MQTTClient.loop_forever()


