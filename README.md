
# 1. Overview
This tutorial introduces the BULK data path for the USB 2.0 bridge. This data path is interface 2on the USB side of the bridge which interfaces to the host software application. In this tutorial we will find and connect to the USB bridge via VID/PID. Test case 1 will send a single BULK USB packet from software to the bridge which will be forwarded to an embedded emulator. The embedded emulator is a micro-controller which mimics a customer's embedded system. This single USB packet will contain a counter in the first few bytes along with a header value in the first byte position. The header value tells the embedded emulator to echo the packet back to the bridge and therefore back to software. The counter values will be verified upon reception, via software, of the echo'd packet. This is a simple 'hello world' type example.

Test case 2 is slightly more advanced where software will send a single USB packet to the bridge with a byte in position [0] denoting a specific operation requested of the embedded emulator on the other side. When the embedded emulator receives this packet it will respond with an 8k data block sent with no breaks or delays to the bridge. This data will flow through the bridge and will be received by the host software application. The intent of this test is to show a typical data burst over the high throughput data interface (BULK). The 8k read operation will be benchmarked in the host software application as well to capture what kind of performance we are getting from the brdige.

A block diagram of the data path from host application to the embedded emulator and back is shown below:
![alt text](./supplemental/tutorial2p1_datapath_bd.png)

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
