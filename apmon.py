#!/usr/bin/env python3

import socket
import struct
import time

def main():
	ping('192.168.1.10')

def ping(destination):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('icmp'))
	sock.settimeout(10.0)
	start_time = time.time_ns() # python 3.7+ only

	payload = struct.pack('L', start_time)
	sock.sendto(encode(payload), (destination, 0))
	while (time.time_ns() - start_time) // 1_000_000_000 < 10:
		try:
			data, source = sock.recvfrom(256)
		except socket.timeout:
			print('timed out')
			return
		message_type, message_code, check, identifier, sequence_number = struct.unpack('bbHHh', data[:8])
		if source == (destination, 0) and message_type == ICMP.ECHO_REPLY and data[8:] == payload:
			print((time.time_ns() - start_time) // 1_000_000, 'ms')
			break
		else:
			print('got unexpected packet from %s:' % source[0], message_type, data[8:])
	else:
		print('timed out')

def encode(payload: bytes):
	# calculate checksum with check set to 0
	checksum = calc_checksum(icmp_header(ICMP.ECHO_REQUEST, 0, 0, 1, 1) + payload)
	# craft the packet again with the checksum set
	return icmp_header(ICMP.ECHO_REQUEST, 0, checksum, 1, 1) + payload

def icmp_header(message_type, message_code, check, identifier, sequence_number) -> bytes:
	return struct.pack('bbHHh', message_type, message_code, check, identifier, sequence_number)

def calc_checksum(data: bytes) -> int:
	'''RFC 1071'''
	# code stolen from https://github.com/alessandromaggio/pythonping/blob/a59ce65a/pythonping/icmp.py#L8
	'''
	MIT License

	Copyright (c) 2018 Alessandro Maggio

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
	'''
	subtotal = 0
	for i in range(0, len(data)-1, 2):
		subtotal += (data[i] << 8) + data[i+1]
	if len(data) % 2:
		subtotal += (data[len(data)-1] << 8)
	while subtotal >> 16:
		subtotal = (subtotal & 0xFFFF) + (subtotal >> 16)
	check = ~subtotal
	return ((check << 8) & 0xFF00) | ((check >> 8) & 0x00FF)

class ICMP:
	ECHO_REPLY = 0
	ECHO_REQUEST = 8

if __name__ == '__main__':
	main()
