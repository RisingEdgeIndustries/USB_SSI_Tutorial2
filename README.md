
# 1. Overview
This tutorial introduces the USB to SSI/SPI bridge. In this tutorial we focuse on transmitting and receiving data over the bulk interface.  The example steps through the software side only (not the embedded SPI / SSI side interfaces) illustrating how a software engineer can get up and running quickly with Python and libusb1.0.  

## 1.1 USB to SSI Bridge
The USB bridge used in this tutorial is the USB2F-SSI-0-1A which, in general, is a small module that converts native USB traffic into SPI / synchronous serial traffic for an embedded system.  This part number supports 0.05" pitch through hole headers on both sides of the SOM. Many other configurations are available so visit [RisingEdgeIndustries](https://www.risingedgeindustries.com) online for more information or to ask about a custom solution. 

The USB link is USB2.0 full speed with 3x interfaces.  One interface is for internal bridge register configuration and the other two interfaces are for high and low throughput data paths.  The module converts this USB traffic to/from embedded synchronous serial traffic. The embedded side consists of two interfaces, one for data transmission to an embedded system and the other for data reception from an embedded system. These two embedded interfaces are unidirectional.

The value and novel approach of this product architecture provides a more sophisticated solution for software to embedded system communication when compared to virtual com. ports (VCP).  Some of the key bullet points are shown below:
-	3x different USB interfaces: Internal bridge register access, 64kB/s deterministic latency data interface, 600+kB/s high throughput interface.
-	Free to use any USB user space driver or develop a custom one
-	Auto enumerates with WINUSB Windows kernel driver
-	Separate TX and RX embedded synchronous serial data interfaces

 

# 2. Details
This tutorial uses a software application to send a command via the USB bulk interface to
an embedded emulator (through the bridge). The embedded emulator returns 8k of data 
(128 frames) upon receiving the command from software. The command is a single packet 
transfer with the first byte in the packet being a 12d. Upon receiving this, the embedded 
emulator response is triggered.

A benchmark is taken during the 128 frame transfer (read operation in software) to get a rough
estimate of throughput.


# 3. Conclusion
The average throughput for this test was ~750kB/S showing a robust mid range data link with improved
logical interfacing, multiple data channels and plug-and-play driver availabtility.
