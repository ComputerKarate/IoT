# Data Acquisition

---

## Device requirements
   - Consume low power
   - Have a large base of inexpensive sensors available
   - Network communications
   - Should be autonomous enough to recover from basic issues

---

### Sensor Components
#### Teensy LC
- Teensy LC (https://www.pjrc.com/store/teensylc.html)  
- Adafruit MCP9808 temperature only (https://www.adafruit.com/product/1782)  
- WIZNET 850 Ethernet shield (https://www.digikey.com/product-detail/en/wiznet/WIZ850IO/1278-1043-ND/8789619)  
- WIZ820 Adapter (https://www.pjrc.com/store/wiz820_sd_adaptor.html)  
|Teensy LC|MCP9808|
| -------- | ------ |
|5v   |1|
|GND  |2|
|18   |4|
|19   |3|

Sketch location:  
IoT/DataAcquisition/Manufacturing_MCP9808/Manufacturing_MCP9808.ino  


#### Teensy 3.2
- Teensy 3.2 (https://www.pjrc.com/store/teensylc.html)  
- Sparkfun RHT03 dual temperature and humidity (https://www.sparkfun.com/products/10167)  
- WIZNET 850 Ethernet shield (https://www.digikey.com/product-detail/en/wiznet/WIZ850IO/1278-1043-ND/8789619)  
|Teensy 3.2|RHT03|
| -------- | ------ |
|5v  |1|
|GND |4|
|4   |2|

Ethernet WIZNET 850 pinout  
With RJ45 facing upward and pins facing away, left side pins 1-6, right side pins 7-12  
|Teensy 3.2|Wiz820|
| -------- | ------ |
|GND       |1|
|GND       |2|
|11 (DOUT) |3 (MOSI)|
|13 (SCK)  |4 (SCLK)|
|10 (CS)   |5 (SCN)|
|GND       |7|
|3.3v      |8|
|3.3v      |9|
|12 (DIN)  |12 (MISO)|

Sketch location:  
IoT/DataAcquisition/Manufacturing_RHT03/Manufacturing_RHT03.ino 

