#include <SPI.h>
#include <Ethernet.h>
#include <ezTime.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "Adafruit_MCP9808.h"

// TODO: Remove references to delay()
// Replace with elapsedmillis() or something similar


/////////////////////
// Pin Definitions //
/////////////////////


////////////////////////
// Object Definitions //
////////////////////////
// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
EthernetClient ethClient;         // Network hardware Object
PubSubClient client(ethClient);   // MQTT Object
Timezone timeObject;

//////////////////////
// Global Variables //
//////////////////////
float temperature;
char DeviceID[12];                          // Unique identifier for this device

// Substitute MAC address in case we are not running on Teensy hardware
byte mac[] = { 0x02, 0xAA, 0xBB, 0xCC, 0xDE, 0x02 };

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
  // TODO: On error, scan the I2C bus for the device at a different address
  if (!tempsensor.begin(0x18))
  {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
  }
    
  return 1;
}

void GetTemperature()
{
  tempsensor.wake();   // wake up, ready to read!
  temperature = tempsensor.readTempF();
  tempsensor.shutdown_wake(1); // shutdown MSP9808 - power consumption ~0.1 mikro Ampere, stops temperature sampling
  LogIt("Temp=" + String(temperature));
  Serial.println("Temp=" + String(temperature));

  MQTTPublish(timeObject.dateTime("m-d-Y") + "|" + timeObject.dateTime("H:i:s") + "|" + String(DeviceID) + "|TEMP=" + String(temperature));
}

//////////////////////////////////////////////////////////////////////////////
// Establish an available connection for pub/sub messages
void InitMQTTClient()
{
  String formattedText;

  client.setServer("192.168.20.18", 1883);
//  client.setCallback(MQTTCallback);

  LogIt("Initializing MQTT client");

  // NOTE: Since we have not introduced security to the MQTT transaction yet
  //      these credentials can be anything
  if (1 == client.connect("TUX_TEMP1", "user1", "football"))
  {
    LogIt("MQTT connection successfully made");
    MQTTSubscribe(); // This actually subscribes to our topics
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
// Initial subscription to our pub/sub messages
void MQTTSubscribe()
{
  bool subscribeTopicResult;
  String subTopic = "test"; // This topic will change to something real as the
                            // process matures

  subscribeTopicResult = client.subscribe(subTopic.c_str());
  if (subscribeTopicResult)
  {
    LogIt("Subscription successful");
  }
  else
  {
    LogIt("Subscription failed");
  }
  return;
}

//////////////////////////////////////////////////////////////////////////////
// This routine connects to the publishing server and publishes a notification
void MQTTPublish(String msg)
{
  // Publish message to the controller
  // TODO The channel needs to be a variable
  if (true != client.publish("test", msg.c_str()))
  {
    LogIt("\nERROR: Unable to publish message to MQTT server");
  }
//  else
//  {
//    LogIt("Published successfully");
//  }
}

//////////////////////////////////////////////////////////////////////////////
// This function receives MQTT messages that are waiting for us
// Not implemented yet
void MQTTCallback(char* topic, byte* payload, unsigned int length)
{
  String commandText = String((char *)payload);
  commandText[length] = '\0';

//  Serial.println("Topic: [");
//  Serial.println(topic);
//  Serial.println("] ");
  
//  Serial.println("Payload length: ");
//  Serial.println(length);
//  Serial.println(commandText.c_str());

//  if (commandText.toUpperCase() == "HOWDY")
//  {
//    Serial.println("\tReceived command: HOWDY");
//  }

  return;
}

//////////////////////////////////////////////////////////////////////////////
// Attempt to reconnect and subscribe to our channels
void MQTTReconnect()
{
  if (!client.connected())
  {
    LogIt("Attempting to reconnect to MQTT server");
    if (1 == client.connect("192.168.XX.XX", "XXXX", "XXXXXXXX"))
    {
      LogIt("\tSuccessfully reconnected to MQTT server");
      MQTTSubscribe();
    }
    else
    {
      LogIt("ERROR: Unable to connect to MQTT server");
      Serial.println(client.state());
    }
  }

  return;
}


void setup() {

  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial);

  Serial.println("\nStartup");

  if (InitNetwork())
  {
    Serial.println("\tNetwork online");
  }

  // The next settings are time related
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
  GetTemperature();
  
  if (!client.connected())
  {
    MQTTReconnect();
  }

  delay(10000);

}
