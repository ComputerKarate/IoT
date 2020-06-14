#include <SPI.h>
#include <Ethernet.h>
#include <ezTime.h>
#include <PubSubClient.h>
#include <SparkFun_RHT03.h>

// TODO Make the TZ offset a variable and save it to flash memory
// RHT03 is a dual temperature / humidity device
// https://www.sparkfun.com/products/10167

//////////////////////////////////////////////////////////////////////
// Production data capture
//////////////////////////////////////////////////////////////////////
// Phase 1:
//    Capture temperature
//    Send temperature value to MQTT server
//    Capture humidity
//    Send humidity value to MQTT server
//////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////
// Phase 2:
//    Notify errors on MQTT channel
//    Listen on MQTT channel for commands from HQ
//    Retrieve config values from network source
//    Save config values to local flash memory
//////////////////////////////////////////////////////////////////////

// NOTE: ezTime requires this modification in ezTime.h to use ethernet
//       rather than wifi:
// Arduino Ethernet shields
// #define EZTIME_ETHERNET

/////////////////////
// Pin Definitions //
/////////////////////
const int RHT03_DATA_PIN = 4; // RHT03 data pin

////////////////////////
// Object Definitions //
////////////////////////
EthernetClient ethClient;         // Network hardware Object
PubSubClient client(ethClient);   // MQTT Object
Timezone timeObject;
RHT03 rht;
IPAddress MQTT_HOST(192, 168, 20, 18);
////////////////////////


//////////////////////
// Global Variables //
//////////////////////
char DeviceID[12];      // Unique identifier for this device
const int MQTT_PORT = 1883;
const char MQTT_TEMPERATURE_CHANNEL[] = "TEMPERATURE";
const char MQTT_USERNAME[] = "user1";
const char MQTT_PASSWORD[] = "password";

// Temperature sensor frequency
const int TEMPERATURE_DELAY_PERIOD = 10000;
unsigned long saved_millis = 0;

// Substitute MAC address in case we are not running on Teensy hardware
byte mac[] = {  };
//////////////////////


/////////////////////////////////////////////////////////////////////
// Every 32-bit teensy has a unique serial number burned into the ROM
// http://forum.pjrc.com/threads/91-teensy-3-MAC-address
void read(uint8_t word, uint8_t *mac, uint8_t offset)
{
  FTFL_FCCOB0 = 0x41;             // Selects the READONCE command
  FTFL_FCCOB1 = word;             // read the given word of read once area

  // launch command and wait until complete
  FTFL_FSTAT = FTFL_FSTAT_CCIF;
  while(!(FTFL_FSTAT & FTFL_FSTAT_CCIF));

  *(mac+offset) =   FTFL_FCCOB5;       // collect only the top three bytes,
  *(mac+offset+1) = FTFL_FCCOB6;       // in the right orientation (big endian).
  *(mac+offset+2) = FTFL_FCCOB7;       // Skip FTFL_FCCOB4 as it's always 0.
}

////////////////////////////////////////////////////////////////////
void read_mac()
{
  read(0xe,mac,0);
  read(0xf,mac,3);
}

///////////////////////////////////////////////////////////////////
void print_mac()
{
  size_t count = 0;

  for(uint8_t i = 0; i < 6; ++i)
  {
    if (i!=0) count += Serial.print(":");
    count += Serial.print((*(mac+i) & 0xF0) >> 4, 16);
    count += Serial.print(*(mac+i) & 0x0F, 16);
  }
}

//////////////////////////////////////////////////////////////////////////////
// Formatted logging
// Example: "12-06-2018 17:34:00 Message Text"
// TODO Add date/time to output
void LogIt(String logmsg)
{
  Serial.println(logmsg);
}

void SetDeviceID()
{
  snprintf(DeviceID, sizeof(DeviceID), "%02X%02X%02X%02X%02X%02X",
          mac[0], mac[1], mac[2], mac[3], mac[4], mac[5] );

  Serial.printf("MAC String: %s\n", DeviceID);
}

// TODO: Add variable so we return an error when necessary
int InitNetwork()
{
  LogIt("Initializing Ethernet with DHCP:");

#if defined(TEENSYDUINO)
  read_mac();
  SetDeviceID();
#endif

  if (Ethernet.begin(mac) == 0)
  {
    LogIt("Failed to configure Ethernet using DHCP");
    if (Ethernet.hardwareStatus() == EthernetNoHardware)
    {
      LogIt("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
    }
    else if (Ethernet.linkStatus() == LinkOFF)
    {
      LogIt("Ethernet cable is not connected.");
    }
  }
  // print your local IP address:
  LogIt("My IP address: ");
  Serial.println(Ethernet.localIP());
  return 1;
}

int InitTemperatureSensor()
{
  rht.begin(RHT03_DATA_PIN);
    
  return 1;
}

void GetTemperature()
{
  // Get new humidity and temperature values from the sensor.
  int updateRet = rht.update();
  
  // If successful, the update() function will return 1.
  // If update fails, it will return a value <0
  if (updateRet == 1)
  {
    float latestHumidity = rht.humidity();
    float latestTempF = rht.tempF();

    // Now print the values:
    Serial.println("Humidity: " + String(latestHumidity, 1) + "%" + " Temp(F): " + String(latestTempF, 1));

    MQTTPublish(timeObject.dateTime("Y-m-d") + "|" + timeObject.dateTime("H:i:s") + "|" + String(DeviceID) + "|TEMP=" + String(latestTempF, 1));
    MQTTPublish(timeObject.dateTime("Y-m-d") + "|" + timeObject.dateTime("H:i:s") + "|" + String(DeviceID) + "|HUMIDITY=" + String(latestHumidity, 1));
  }
}

//////////////////////////////////////////////////////////////////////////////
// Establish an available connection for pub/sub messages
void InitMQTTClient()
{
  client.setServer(MQTT_HOST, MQTT_PORT);

  LogIt("Initializing MQTT client");

  if (1 == client.connect(DeviceID, MQTT_USERNAME, MQTT_PASSWORD))
  {
    LogIt("MQTT connection successfully made");
  }
  else
  {
    LogIt("ERROR: Unable to connect to MQTT server");
    Serial.println(client.state());
  }

  LogIt("MQTT initialization complete");

  return;
}


//////////////////////////////////////////////////////////////////////////////
// This routine connects to the publishing server and publishes a notification
// TODO: Add parm for the MQTT channel
void MQTTPublish(String msg)
{
  // Publish message to the controller
  if (true != client.publish(MQTT_TEMPERATURE_CHANNEL, msg.c_str()))
  {
    LogIt("\nERROR: Unable to publish message to MQTT server");
  }
}

//////////////////////////////////////////////////////////////////////////////
// Attempt to reconnect and subscribe to our channels
void MQTTReconnect()
{
  if (!client.connected())
  {
    LogIt("Attempting to reconnect to MQTT server");
    if (1 == client.connect(MQTT_HOST, MQTT_USERNAME, MQTT_PASSWORD))
    {
      LogIt("\tSuccessfully reconnected to MQTT server");
    }
    else
    {
      LogIt("ERROR: Unable to connect to MQTT server");
      Serial.println(client.state());
    }
  }

  return;
}

////////////////////////////////////////////////////////////////////
// Runs one time at startup
void setup() {

  // Open serial communications and wait for port to open:
  Serial.begin(9600);
//  while(!Serial);
//  delay(500);

  Serial.println("\nStartup");

  if (InitNetwork())
  {
    Serial.println("\tNetwork online");
  }

  // The next settings are ezTime related
  setDebug(INFO);
  waitForSync();
  // TODO Make the TZ offset a variable and save it to flash memory
  timeObject.setPosix("UTC+5:00");

  if (InitTemperatureSensor())
  {
    Serial.println("\tTemperature sensor online");
  }

  InitMQTTClient();
}

void loop() {

  if (millis() - saved_millis > TEMPERATURE_DELAY_PERIOD)
  {
    GetTemperature();

    if (!client.connected())
    {
      MQTTReconnect();
    }
    saved_millis = millis();
  }
}
