# ################################################################
# Project Name:
# USB Bridge - Tutorial2_p1
#
# Author: rvalentine
# Date: 10/19/2023
#
#
# Project Description:
# ----------------------------------------------------------------
# This tutorial introduces the BULK interface used for high throughput
# communications. This interface supports ~6Mbit data rates using the
# USB 2.0 protocol BULK interface communication. 
#
# The tutorial steps through a simple single packet transaction from
# software to an embedded system connected to the SSI interfaces. 
# The embedded system connected to the bridge SSI ports echos the
# the data received on the SSI RX port to the SSI TX port sending 
# that data back to software. The first test case in this tutorial 
# will receive the echo'd data and print it to the console.
#
# The second test case is a benchmark showing the data rate through
# the bridge when receiving an 8k block of data from the embedded
# system connected to the SSI ports of the bridge. Test case #2
# sends a single packet to the bridge, this packet is forwarded to
# the embedded system which indicates the embedded system should 
# respond with 8k worth of data. The embedded system sends this
# 8k data block to the bridge and software, shown here, performs
# an 8k read and benchmarks the performance.
#
#
# Notes:
# ----------------------------------------------------------------
#
#
# ----------------------------------------------------------------
# Disclaimer:
# ----------------------------------------------------------------
# This library is provided strictly as example code. There is no
# expected reliablity of operation from RisingEdgeIndustries and 
# this source code is not to be sold or represented as a 3'd party
# solution for commercial use. The below code is development code
# for example use only supporting customers as they test the bridge
# products from RisingEdgeIndustries. Nothing in this file is allowed
# to be modified or sold in any way. No code below is released with 
# the intention or expectation of reliable operation.
#
# Packing this module with any 3d part code can only be done with 
# the inclusion of this disclaimer and no modifications.
# ################################################################

import ctypes as ct
import libusb as usb
import time


#
# Definitions
#
DEF_VID = 0x1cbf
DEF_PID = 0x0007
ENDPOINT_BLK2_OUT = 0x03
ENDPOINT_BLK2_IN = 0x83 

EP2IN_SIZE = 64*1
EP2IN_TIMEOUT = 1000 	# mS

EP2OUT_SIZE = 64*1
EP2OUT_TIMEOUT = 250 	# mS



#
# Libusb variables/data structures
#
dev = None
dev_found = False

dev_handle = ct.POINTER(usb.device_handle)() 	# creates device handle (not device obj)
devs = ct.POINTER(ct.POINTER(usb.device))() 	# creates device structure
ep_data_out = (ct.c_ubyte*(EP2OUT_SIZE))()
ep_data_in = (ct.c_ubyte*(EP2IN_SIZE))()
bulk_transferred = ct.POINTER(ct.c_int)()	

#
# inits
#
bulk_transferred.contents = ct.c_int(0)

def find_bridge(VID, PID):
	print('===================================')
	print('[Search and Connect to Bridge]!')
	print('Searching - Finding Bridge!')
	# open usb library
	r = usb.init(None)
	if r < 0:
		print(f'usb init failure: {r}')
		return (1, -1)

	# get list of USB devices
	cnt = usb.get_device_list(None, ct.byref(devs))
	# error check
	if cnt < 0:
		print(f'get device list failure: {cnt}')
		return (1, -1)

	# Check all USB devices for VID/PID match
	i = 0
	while devs[i]:
		dev = devs[i]

		# get device descriptor information
		desc = usb.device_descriptor()
		r = usb.get_device_descriptor(dev, ct.byref(desc))
		# error check
		if r < 0:
			print(f'failed to get device descriptor: {r}')
			return (1, -1)

		if(desc.idVendor == DEF_VID) and (desc.idProduct == DEF_PID):
			dev_found = True		
			break

		i += 1

	#
	# open device if matching vid/pid was found
	#
	if(dev_found == True):
		print('Searching - Bridge Found!')
		print('Connecting - Opening Bridge Connection!')
		r = usb.open(dev, dev_handle)
		# error check
		if r < 0:
			print(f"ret val: {r} - {usb.strerror(r)}")
			print("failed to open device!")
			return (1, -1)
		else:
			print('Connecting - Open Connection Success!')

		return (0, dev_handle)






# ------------------------------------------------------------
# Description: testcase1_exe
# ------------------------------------------------------------
# Test case 1 sends a single bulk packet from software
# to the embedded emulator. The emulator receives this 
# packet from the bridge and echo's it back as an SSI
# frame. A packet is created with a flag byte of 10d 
# indicating the embedded emulator should perform an echo
# operation and a counter with values 1-5 following. These
# values are verified in the packet received by software.
# ------------------------------------------------------------
def testcase1_exe(dev_handle):
	print('\n===================================')
	print('[Test case#1 - bulk write transaction]')

	# claim interface 2 - bulk interface
	r = usb.claim_interface(dev_handle, 2)
	# error check
	if(r != 0):
		print(f'ERROR: failed to claim interface, ret val = {r}')
		print(f"ERROR: code - {usb.strerror(r)}")

	# --------------------------------------
	# Handle Transmit Case
	# --------------------------------------
	ep_data_out[0] = 10	 	# indicates loopback operation to
							# embedded emulator

	ep_data_out[1] = 1		# dummy data to check to verify rx'd
	ep_data_out[2] = 2 		# looped back data
	ep_data_out[3] = 3
	ep_data_out[4] = 4
	ep_data_out[5] = 5

	# execute write transaction
	r = usb.bulk_transfer(dev_handle, ENDPOINT_BLK2_OUT, ep_data_out, 
							EP2OUT_SIZE, bulk_transferred, EP2OUT_TIMEOUT)	
	print(f'Transferred {bulk_transferred.contents} bytes!')


	# --------------------------------------
	# Handle Receive Case
	# --------------------------------------

	# execute write transaction	
	r = usb.bulk_transfer(dev_handle, ENDPOINT_BLK2_IN, ep_data_in, 
							EP2IN_SIZE, bulk_transferred, EP2IN_TIMEOUT)	
	# error check
	if (r < 0):
		print(f'ERROR: Total bytes transferred <{bulk_transferred.contents}> bytes!')
		print(f'ERROR: Expected to xfer <{EP2IN_SIZE}> bytes!')
		print(f'ERROR: bulk_transfer() ret code <{r}> bytes!')
		return (1, -1)
	else:	
		print(f'Received {bulk_transferred.contents} bytes!')

	# print read result
	print(f"{'rx byte[1]: ':.<30}{f'{ep_data_in[1]:#02x}':.>20}")
	print(f"{'rx byte[2]: ':.<30}{f'{ep_data_in[2]:#02x}':.>20}")
	print(f"{'rx byte[3]: ':.<30}{f'{ep_data_in[3]:#02x}':.>20}")
	print(f"{'rx byte[4]: ':.<30}{f'{ep_data_in[4]:#02x}':.>20}")
	print(f"{'rx byte[5]: ':.<30}{f'{ep_data_in[5]:#02x}':.>20}")









#
# Run module
#
r = find_bridge(DEF_VID, DEF_PID)

# check for errors
if(r[0] == 1):
	print(f"ERROR: ret val: {r}""}")
else:
	# on success - run test case #1
	testcase1_exe(r[1])


