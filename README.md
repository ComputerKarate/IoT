# IoT
Embedded devices are your friend

---

## Overview
Project goal is to measure, quantify, and succinctly display the resources consumed during
a production run.  
After gathering details of resources consumed during a production cycle, we can begin comparing
the details of many production runs looking for which conditions give us the best
efficiencies. 

Some of the criteria used in selecting devices and software include: 
   - Framework to use IoT devices to monitor and respond to your production environment
   - The devices will communicate with a message broker (MQTT or WebSockets)
   - The message will be captured by a background process and written to the DB
   - A web dashboard will display the status of the systems

Because of the power, compatibility with Arduino hardware and low cost, POC will be with teensyduino devices (https://pjrc.com).  
The background process is currently a python script monitoring the MQTT channels used by the configured devices.  
Most buildings will have multiples of the same sensor type in fairly close proxmity so we can use machine learning to validate whether a sensor is out of spec and alert or recover.  

### Phase 1:
Monitor devices:
- Temperature
- Humidity

Data capture:
- Devices will publish data to an MQTT server on a specific channel
- The data captured will be saved to a DB for future analysis
- Current MQTT server being use is Mosquitto

Display data:
- Data will be displayed in chart format
- The user will be able to filter the data for analysis

Example sensor message: 
DATE|TIME|DEVICEID|MQTT Queue|Sensor value  
04-17-2020|23:32:31|04E9E50B4F5|test|74.30

