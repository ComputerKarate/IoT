# Data Acquisition

---

## Devices
   - Consume low power
   - Have a large base of sensors available
   - Can communicate on the network for data transfer
   - Should be autonomous enough to recover from basic issues

### Temperature Sensor Components
Microcontroller:
- Teensy LC (https://www.pjrc.com/store/teensylc.html)

Temperature sensor:
- Adafruit MCP9808 (https://www.adafruit.com/product/1782)

Pinout
Teensy LC   MCP9808
5v          1
GND         2
18          4
19          3


Ethernet:
- WIZ820 Adapter (https://www.pjrc.com/store/wiz820_sd_adaptor.html)
- WIZNET 850 Ethernet shield (https://www.digikey.com/product-detail/en/wiznet/WIZ850IO/1278-1043-ND/8789619)
The ethernet module connects to the 820 adapter which seats directly onto the Teensy LC.
The ethernet library automatically detects and initializes the device.

