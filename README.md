
# 1. Overview
This tutorial introduces the BULK data path for the USB 2.0 bridge. This data path is interface 2on the USB side of the bridge which interfaces to the host software application. In this tutorial we will find and connect to the USB bridge via VID/PID. Test case 1 will send a single BULK USB packet from software to the bridge which will be forwarded to an embedded emulator. The embedded emulator is a micro-controller which mimics a customer's embedded system. This single USB packet will contain a counter in the first few bytes along with a header value in the first byte position. The header value tells the embedded emulator to echo the packet back to the bridge and therefore back to software. The counter values will be verified upon reception, via software, of the echo'd packet. This is a simple 'hello world' type example.

Test case 2 is slightly more advanced where software will send a single USB packet to the bridge with a byte in position [0] denoting a specific operation requested of the embedded emulator on the other side. When the embedded emulator receives this packet it will respond with an 8k data block sent with no breaks or delays to the bridge. This data will flow through the bridge and will be received by the host software application. The intent of this test is to show a typical data burst over the high throughput data interface (BULK). The 8k read operation will be benchmarked in the host software application as well to capture what kind of performance we are getting from the brdige.

A block diagram of the data path from host application to the embedded emulator and back is shown below:
![alt text](./supplemental/tutorial2p1_datapath_bd.png)

## 1.1 Bridge Overview
The USB bridge used in this tutorial is the USB2F-SSI-0-1A which, in general, is a small module that converts native USB traffic into SPI / synchronous serial traffic for an embedded system.  This part number supports 0.1" pitch through hole headers on both sides of the SOM and can fit in a standard prototyping breadboard. Many other configurations are available so visit [RisingEdgeIndustries](https://www.risingedgeindustries.com) online for more information or to ask about a custom solution. 

Bridge Top View             | Bridge Side View
:-------------------------:|:-------------------------:
![alt text](./supplemental/pic2-top-small.png) |  ![alt text](./supplemental/pic1_side_small.png)

The USB link is USB2.0 full speed composite device with 3x interfaces.  One interface is for internal bridge register access supporting operational and configuration changes. The other two interfaces are for high and low throughput data paths.  Each data path works with native USB 2.0 64 byte packets of data. The lower datarate interface is an interrupt interface capable of 64kB/s. This interface is polled by the USB host (workstation) every 1mS supporting deterministic latency. The second data interface is a BULK interface which can operate in excess of 650kB/s (5.2Mbit/s). This datarate is dependant on how much bandwidth is available on the USB bus per USB 2.0 BULK interface protocol. A BULK interface utilizes as much free bandwidth in each USB frame as possible to transfer data.

<u>Interface Summary</u>:
-	Interface 0: Bridge register access
-	Interface 1: INTERRUPT low throughput interface
-	Interface 2: BULK high throughput interface

The embedded systems side of this bridge consists of two unidirectional SSI/SPI ports. The TX and RX data is separate to allow the customer embedded system to operate based on data frame interrupts rather than polling the bridge checking for data constantly. The polling approach eats up valuable customer embedded system bandwidth / CPU cycles.

The master SSI/SPI port forwards all USB 64 byte packets out to the target embedded system as a 68 byte frame. The frame is larger than the USB packet because 4 additional bytes of meta data are added. The meta data allows target embedded systems to know which USB interface (INT1 or BULK2) the 64 byte packet came from. This allows the embedded systems engineer to be aware of which USB interface software sent the packet over. When the embedded system assembles a frame to transmist to the USB bridge RX interface, the firmware engineer must add this meta data to the frame so the bridge knows which USB interface to forward the 64 byte payload of the 68 byte frame to.

The meta data allows the software engineer and firmware engineer on either side of the bridge to stay in sync and know which interfaces data comes from and should be sent to. This can be very valuable when users need to logically separate different types of traffic. 

An example use case may be that an embedded system needs to send low data rate telemetry information back to software which can be done over INT1 (interrupt interface 1). The software engineer can launch a thread that constantly monitors for data on the USB interface and when available, reads the data and passes it to the main software application. The BULK2 (bulk 2) interface is used specifically for large data transfers to and from the target embedded system.

The bridge module is ideal for users that need a more intelligent solution than a virtual serial port for software application to embedded system communication but also need to retain the ease and siimplicity of a simple serial link.

Some of the key features/improvements are shown below:
-	3x different USB interfaces: Internal bridge register access, 64kB/s deterministic latency data interface, 650+kB/s high throughput interface.
-	Free to use any USB user space driver or develop a custom one
-	Auto enumerates with WINUSB Windows kernel driver
-	Separate TX and RX embedded synchronous serial data interfaces for interrupt driven firmware development
-	Plug and play solution utilizing REIndustries free Python library
-	Prototype friendly, footprint compatible with standard breadboards
-	Many functional configuration options via internal bridge register space

As mentioned above, 64 byte packets are transferred over each USB interface. A block diagram of this relationship is shown below:
![alt text](./supplemental/BD1.png)

This diagram shows all 3x USB interfaces including the internal bridge register access interface (INT0). The 64 byte data packets sent over INT0 are commands that support changing bridge register settings and this data is not forwarded out of the SSI serial ports to a target embedded system.

The INT1 and BULK2 interface packets are received by the bridge, meta data capturing which USB interface they were received on is wrapped around the 64 byte data packet yielding the 68 byte frame and that frame is sent out of the master SSI port to the target embedded system.

A diagram of the SSI frame side of the transfer is shown below:
![alt text](./supplemental/BD2.png)

The traffic flow through the bridge is shown below. This block diagram describes USB packets from software on the left flowing through the bridge to a target embedded system on the right.
![alt text](./supplemental/BD3.png)

When plugged in, the bridge tells Windows to load WINUSB.sys as the kernel space driver automatically and leaves the user space driver selection up to the user. A diagram of this is shown below:
![alt text](./supplemental/BD4.png)

This means the user must select a user space driver (there are multiple available 3d party drivers) to actually talk to the USB bridge. REIndustries has selected libusb1.0 (the Python implementation is just libusb) to use for these tutorials as it is cross platform and supported as a Python library. This design and architecture choice was made to provide more advanced control to software engineers that are looking for a more robust and advanced link compared to a virtual serial port, but still want to keep things reasonably simple. For users looking for a COTS solution, a Python user space drive can be used as in this example and easily wrapped as we have shown with the associated usb library example supporting this tutorial series.

For all tutorials, the Python libusb library can be installed using "pip install libusb". This must be performed as a first step in this tutorial series.


## 1.2 Mechanical
The bridge module consists of an 0.062" thick PCB with a USB-C connector for software application connectivity and unloaded headers (via holes) supporting the embedded sysnchronous serial interfaces. Customers can load either male or female headers depending on the required interface to their PCB hardware system.

The dimensions shown below are 1.223 inches long by 0.805 inches high. These are PCB edge to edge dimensions.
![alt text](./supplemental/dimensions.png)

 

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
