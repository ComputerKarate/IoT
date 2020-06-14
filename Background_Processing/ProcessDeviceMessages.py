#!/usr/bin/python3

import mysql.connector as mariadb
from mysql.connector import errorcode
import paho.mqtt.client as mqtt
import time
import logging as log
import configparser
from io import StringIO
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')
DEBUG = 0 # Set to 1 for verbose output
RecordList = []

log.basicConfig(
    filename=config['DEFAULT']['LOG_FILE'],
    level=log.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S')

def logit(message):
    if (1 == DEBUG):
        print(message)
    log.info(message)

def write_data(record):
    connection = mariadb.connect(host=config['DB']['DB_HOST'],
                                 user=config['DB']['DB_USERNAME'],
                                 password=config['DB']['DB_PASSWORD'],
                                 charset='utf8',
                                 use_unicode=True)

    sql_insert_query = """INSERT INTO data_log (name,data_type,data_payload,created_at)
                        VALUES (%s,%s,%s,%s)"""

    try:
        if (1 == DEBUG):
            logit("Inserting record: " + str(record))
            print(record)
        cursor = connection.cursor()
        if (1 == DEBUG):
            logit("USE DB:")
            logit(config['DB']['DB'])
        cursor.execute("USE {}".format(config['DB']['DB']))
        cursor.execute(sql_insert_query, record)
    except mariadb.Error as err:
        logit(err)
    else:
        if (1 == DEBUG):
            logit("INSERT OK")

    connection.commit()
    cursor.close()
    connection.close()

def process_message(DeviceMessage):
    rawMsg = StringIO(DeviceMessage)
    tmpMsg = np.genfromtxt(rawMsg, dtype=[
        ('EventDate', 'S10'),
        ('EventTime', 'S8'),
        ('DeviceID', 'S20'),
        ('DataValue', 'S20')
    ], delimiter="|")
    FormattedEventDate = str(tmpMsg['EventDate'], 'utf-8')
    FormattedEventTime = str(tmpMsg['EventTime'], 'utf-8')
    CombinedDateTime = FormattedEventDate + ' ' + FormattedEventTime
    FormattedDeviceID = str(tmpMsg['DeviceID'], 'utf-8')
    TempData = str(tmpMsg['DataValue'], 'utf-8')
    FormattedData = TempData.split('=', 1)

    data_tuple = (FormattedDeviceID.strip("\x00"), FormattedData[0], FormattedData[1].strip("\x00"), CombinedDateTime)
    logit("Record: " + str(data_tuple))
    write_data(data_tuple)

def on_message(mqttc, obj, msg):
    FormattedPayload = str(msg.payload, 'utf-8')
    process_message(FormattedPayload)

def on_connect(mqttc, obj, flags, rc):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        logit("Connection return code: " + str(rc))
    log.info("Connection return code: " + str(rc))

    # Subscribe request
    MQTTClient.subscribe(config['MQTT']['SUBSCRIBE_CHANNEL'])

def on_publish(mqttc, obj, mid):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        logit("mid: " + str(mid))
    log.info("Publish return code mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        logit("Subscribed: " + str(mid) + " " + str(granted_qos))
    log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    if ( 'TRUE' == config['DEFAULT']['DEBUG'] ):
        logit(string)


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
MQTT_Host = config['MQTT']['MQTT_HOST']
logit("MQTT_Host = " + MQTT_Host)
MQTT_Port = config['MQTT']['MQTT_PORT']
logit("MQTT_Port = " + str(MQTT_Port))
MQTT_Timeout = config['MQTT']['MQTT_TIMEOUT']
logit("MQTT_Timeout = " + str(MQTT_Timeout))
MQTTClient.connect(config['MQTT']['MQTT_HOST'], 1883, 60)

# Just what it says...forever
MQTTClient.loop_forever()


