#!/usr/bin/python3

from __future__ import print_function

import mysql.connector as mariadb
from mysql.connector import errorcode

DB_NAME='companies'
DB_HOST='<Insert DB hostname or IP here>'
USER_NAME='<DB Username>'
PASSWORD='<DB Password>'

TABLES = {}
TABLES['organization'] = (
    "CREATE TABLE `organization` ("
    "  `organization_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `organization_name` varchar(50) NULL COMMENT 'Org Name',"
    "  `location` varchar(250) NULL COMMENT 'Location',"
    "  `active` tinyint NOT NULL DEFAULT '1' COMMENT 'Active?',"
    "  `created_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date created',"
    "  `updated_at` datetime NOT NULL DEFAULT current_timestamp() COMMENT 'Date last updated' ON UPDATE CURRENT_TIMESTAMP(),"
    "  PRIMARY KEY (`organization_id`)"
    ") ENGINE=InnoDB")

TABLES['building'] = (
    "CREATE TABLE `buildings` ("
    "  `building_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `building_name` varchar(50) NULL COMMENT 'Building Reference',"
    "  `building_location` varchar(250) NULL COMMENT 'Building location',"
    "  `organization_id` int(11) NOT NULL,"
    "  `building_type` varchar(250) NOT NULL COMMENT 'Building Purpose',"
    "  `active` tinyint NOT NULL DEFAULT '1' COMMENT 'Active?',"
    "  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Date created',"
    "  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP() COMMENT 'Date last updated',"
    "  PRIMARY KEY (`building_id`), UNIQUE KEY `building_name` (`building_name`),"
    "  CONSTRAINT `buildings_ibfk_1` FOREIGN KEY (`organization_id`)"
    "    REFERENCES `organization` (`organization_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

TABLES['device'] = (
    "CREATE TABLE `device` ("
    "  `device_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `device_name` varchar(50) NULL COMMENT 'Device Reference',"
    "  `building_id` int(11) NOT NULL,"
    "  `device_type` varchar(50) NOT NULL COMMENT 'Device Features',"
    "  `device_role` varchar(50) NOT NULL COMMENT 'Device Purpose',"
    "  `active` tinyint NOT NULL DEFAULT '1' COMMENT 'Active?',"
    "  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Date created',"
    "  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP() COMMENT 'Date last updated',"
    "  PRIMARY KEY (`device_id`), UNIQUE KEY `device_name` (`device_name`),"
    "  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`building_id`) "
    "    REFERENCES `buildings` (`building_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

TABLES['data_log'] = (
    "CREATE TABLE `data_log` ("
    "  `device_name` varchar(50) NOT NULL COMMENT 'Device Reference',"
    "  `data_type` varchar(50) NOT NULL,"
    "  `data_payload` varchar(250) NULL,"
    "  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT 'Date created',"
    "  PRIMARY KEY (`data_type`, `created_at`)"
    ") ENGINE=InnoDB")


# Initial DB connection
connection = mysql.connector.connect(user=USER_NAME,
                              password=PASSWORD,
                              host=DB_HOST)

cursor = connection.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


##########################################################
# Make tentative connection to the DB
# Create DB if necessary
try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        # If the DB does not exist, and the user has permissions, go ahead and create it
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        connection.database = DB_NAME
    else:
        print(err)
        exit(1)


##########################################################
# At this point the DB should be in place and we are ready to start adding tables
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
connection.close()

