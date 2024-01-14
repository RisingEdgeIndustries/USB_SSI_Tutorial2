#
# Project Name:
# USB Bridge - Tutorial 2
#
# Author: rvalentine
# Date: 10/19/2023
#
# Project Description:
# ----------------------
# 
#
# Disclaimer:
# ----------------------
# This code is provided as is and is not supported
# by RisingEdgeIndsutreis in any way. The user
# accepts all risk when running all or some of 
# this python module.
#

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
# to the embedded emulator. The emulator echos this packet
# back to the bridge with a BULK interface SSI frame
# (byte[0] of 10d denotes an echo operation in our emulator)
# and software attempts a read operation from the bridge USB
# BULK interface. Upon success, this echo packet is read
# before the timeout limit and the first 5 bytes of the 
# packet are checked to verify data sent is preserveda and
# echo'd back correctly
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







# ------------------------------------------------------------
# Description: testcase2_exe
# ------------------------------------------------------------
# Test case 2 sends a single BULK packet to the bridge which
# is forwaded on to the embedded emulator. The byte[0] value
# of the transmit operation tells the embedded emulator to
# respond with an 8k (SSI - serial) data burst. This 8k data
# transmission flows through the bridge and is received by
# host software during the 8k read (endpoint in) operation.
# ------------------------------------------------------------
def testcase2_exe(dev_handle):
	print('\n===================================')
	print('[Test case#2 - bulk write transaction]')

	# claim interface 2 - bulk interface
	r = usb.claim_interface(dev_handle, 2)
	# error check
	if(r != 0):
		print(f'ERROR: failed to claim interface, ret val = {r}')
		print(f"ERROR: code - {usb.strerror(r)}")

	
	# reconfigure endpoint buffers for 8k readback
	EP2IN_SIZE = 64*128
	ep_data_in = (ct.c_ubyte*(EP2IN_SIZE))()
	print("USB read buffer upadted to 8k!")


	# --------------------------------------
	# Handle Transmit Case
	# --------------------------------------
	ep_data_out[0] = 12	 	# indicates 8k readback operation
							# to embedded emulator


	# execute write transaction
	r = usb.bulk_transfer(dev_handle, ENDPOINT_BLK2_OUT, ep_data_out, 
							EP2OUT_SIZE, bulk_transferred, EP2OUT_TIMEOUT)	
	print(f'Transferred {bulk_transferred.contents} bytes!')



	# --------------------------------------
	# Handle Receive Case
	# --------------------------------------

	# execute write transaction
	start = time.time()
	r = usb.bulk_transfer(dev_handle, ENDPOINT_BLK2_IN, ep_data_in, 
							EP2IN_SIZE, bulk_transferred, EP2IN_TIMEOUT)
	stop = time.time()
	# error check
	if (r < 0):
		print(f'ERROR: Total bytes transferred <{bulk_transferred.contents}> bytes!')
		print(f'ERROR: Expected to xfer <{EP2IN_SIZE}> bytes!')
		print(f'ERROR: bulk_transfer() ret code <{r}> bytes!')
		return (1, -1)
	else:	
		print(f'Received {bulk_transferred.contents} bytes!')

	# print out time for 8k benchmark
	print("\nBenchmark Results:")
	dt = stop - start
	print(f"dt: {dt}S")
	print(f"Benchmark time: {round(dt*1000, 3)}mS")
	val = round((8192/dt)/1000, 2)
	#print(f"Throughput: {round((8192/dt)/1000, 2)}kB/S")
	print(f"Throughput: {val}kB/S")
	print(f"Throughput: {round(val*8/1000, 2)}Mb/S")



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
	testcase2_exe(r[1])	

