## @package maker_bus
#
# MakerBus serial communication package
#
# This package provides the software needed to send and receive
# MakerBus protocol packets.

import serial

## @class Maker_Bus_Base
#
# Provide the shared interface to the MakerBus.
#
# *Maker_Bus_Base* provides an interface to the serial port that
# talks the 8-bit to 9-bit protocol needed to communicate packets
# back and forth from the Makerbus

class Maker_Bus_Base:

    def __init__(self, serial):
        """ {Maker_Bus}: Initialize a Maker_Bus object. """

        self.address = -1
        self.auto_flush = True
        self.request = []
        self.request_safe = 0
        self.response = []
        self.serial = serial
        self.trace = True
        self.trace_pad = ""

	#FIXME: Only open serial if it is not already open:
        #serial.open()
        serial.flushInput()
        serial.setTimeout(1)
        
    def auto_flush_set(self, flush_mode):
        """ {Maker_Bus}: This routine will set the auto flush mode for {self}
            to {flush_mode}.  When {flush_mode} is set to {True}, it will
            automatically flush each command sequence as it soon as possible.
            When {flush_mode} is {False}, the command sequences are queued
            up until they are explicitly flushed by calling {flush}(). """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.auto_flush({1})". \
              format(trace_pad, flush_mode))

        self.auto_flush = flush_mode
        if flush_mode:
            self.flush()

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.auto_flush({1})".
              format(trace_pad, flush_mode))

    def flush(self):
        """ {Maker_Bus}: Flush out current request. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.flush()".format(trace_pad))

        # Do not do anything unless we have something to send:
        request = self.request
        request_length = len(request)
        while request_length != 0:
            # Make sure that the correct module is selected:
            if request_length >= 16:
                request_length = self.request_safe
            assert request_length < 16, \
              "Request is {0} bytes >= 16".format(request_length)

            # Compute checksum:
            checksum = 0
            for index in range(0, request_length):
                checksum += request[index]
            checksum = (checksum + (checksum >> 4)) & 0xf

            # Compute request header and send it out:
            request_header = (request_length << 4) | checksum
            serial = self.serial
            self.frame_put(request_header)
        
            # Send out the rest of the request:
            for index in range(0, request_length):
                ubyte = request[index]
                self.frame_put(ubyte)
            del request[0: request_length]
            request_length = len(request)
            self.request_safe -= request_length

	    # Flush the serial output buffer:
            if trace:
                print("{0}Maker_Bus.flush:serial.flush()".format(trace_pad))
            serial.flush()

            # Now get a response:
            response = self.response
            response_header = self.frame_get()
            if response_header < 0:
                # We had a time-out:
                print("Response header timeout")
            else:
                response_length = response_header >> 4
                response_checksum = response_header & 0xf
        
                # Get the rest of the response:
                del response[:]
                while response_length != 0:
                    response_frame = self.frame_get()
                    if response_frame < 0:
                        # We have a timeout:
                        print("Response byte timeout")
                        break
                    response.append(response_frame)
                    response_length -= 1

                # Compute checksum:
                checksum = 0
                for ubyte in response:
                    checksum += ubyte
                checksum = (checksum + (checksum >>4)) & 0xf

                if trace:
                    print("{0}response={1}, checksum=0x{2:x}". \
                      format(trace_pad, response, checksum))

                if checksum != response_checksum:
                    print("Got checksum of 0x{0:x} instead of 0x{1:x}". \
                      format(checksum, response_checksum))
                    del response[:]

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.flush() response={1}". \
              format(trace_pad, self.response))

    def bus_reset(self):
	""" Maker_Bus_Base: Reset the bus. """

	trace = self.trace
	if trace:
	    print("=>bus_reset()")

	# Shove a 0xc5 out there to force a bus reset:
	serial = self.serial
	serial.write(chr(0xc5))
	serial.flush()

	# Wait for a response:
	byte = serial.read(1)
	if len(byte) == 0:
	    print("Bus reset failed with no response")
	elif ord(byte) != 0xa5:
	    print("Bus reset failed 0x{0:x}".format(ord(byte)))
	else:
	    if trace:
		print("Bus reset succeeded")

	if trace:
	    print("<=bus_reset()")

    def discovery_mode(self):
        """ Maker_Bus_Base: Perform discovery mode """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "


        serial = self.serial
        serial.write(chr(0xc4))
        if trace:
            print("{0}write(0xc4)".format(trace_pad))

        serial.flush()
        line = []
        ids = []
        done = False
        while not done:
            byte = serial.read(1)

            if trace:
                print("{0}read() => 0x{1:x}".format(trace_pad, ord(byte)))

            if byte == '\n':
                ids.append("".join(line[1:]))
                done = len(line) != 0 and line[0] == '!'
                del line[:]
            else:
                line.append(byte)

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.discovery_mode() =>{1}". \
              format(trace_pad, ids))

        return ids

    def frame_get(self):
        """ {Maker_Bus}: Return the next frame from the bus connected
            to {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.frame_get()".format(trace_pad))

        frame = -10;
        serial = self.serial
        result = serial.read(1)
        if len(result) != 0:
            frame = ord(result[0])
        else:
            print("Timeout1")
            frame = -1
            self.address = -1

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.frame_get()=>0x{1:x}". \
	      format(trace_pad, frame))
        return frame

    def frame_put(self, frame):
        """ {Maker_Bus}: Send frame to the bus connected to {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.frame_put(0x{1:x})".format(trace_pad, frame))

        serial = self.serial
        if (frame > 0xff or (0xc1 <= frame and frame <= 0xc5)):
            # Send {frame} as two bytes:
            byte1 = 0xc0 | ((frame >> 7) & 3)
            byte2 = frame & 0x7f
            serial.write(chr(byte1))
            serial.write(chr(byte2))

            if trace:
                print("{0}write(0x{1:x});write(0x{2:x})". \
                  format(trace_pad, byte1, byte2))
        else:
            # Send {frame} as one byte:
            serial.write(chr(frame))

            if trace:
                print("{0}write(0x{1:x})".format(trace_pad, frame))
            
        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.frame_put(0x{1:x})".format(trace_pad, frame))


    def request_begin(self, address, command):
        """ {Maker_Bus}: Append {command} to self.request. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            print("{0}=>Maker_Bus.request_begin(0x{1:x}, 0x{2:x})". \
              format(trace_pad, address, command))
            self.trace_pad = trace_pad + " "

        request = self.request
        request_length = len(request)
        self.request_safe = request_length
        if self.auto_flush and request_length != 0:
            self.flush()

        if address != self.address:
            self.frame_put(address | 0x100)
            self.address = address
            if (address & 0x80) == 0:
                self.frame_get()

        request.append(command)

        if trace:
            print("{0}<=Maker_Bus.request_begin(0x{1:x}, 0x{2:x})". \
              format(trace_pad, address, command))
            self.trace_pad = trace_pad

    def request_byte_put(self, byte):
        """ {Maker_Bus}: Append {byte} to current request in {self}. """

	self.request_ubyte_put(self, byte & 0xff);

    def request_end(self):
        """ Maker_Bus: Indicate that current command is complete. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.request_end()".format(trace_pad))

        request = self.request
        request_length = len(request)
        if request_length >= 16:
            self.flush()
        self.request_safe = len(request)
        if self.auto_flush:
            self.flush()

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.request_end() response={1}". \
              format(trace_pad, self.response))

    def request_int_put(self, int32):
        """ {Maker_Bus}: Append {int32} to current request in {self}. """

	self.request_uint_put(int32);

    def request_short_put(self, int16):
        """ {Maker_Bus}: Append {int16} to current request in {self}. """

	self.request_ushort_put(int16);

    def request_ubyte_put(self, ubyte):
        """ {Maker_Bus}: Append {ubyte} to current request in {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.request_ubyte_put({0})". \
              format(trace_pad, ubyte))

        request = self.request
        request.append(ubyte & 0xff)

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.request_ubyte_put({1}) request={2}". \
              format(trace_pad, ubyte, request))

    def request_uint_put(self, uint32):
        """ {Maker_Bus}: Append {int32} to current request in {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.request_int_put({1})". \
	      format(trace_pad, uint32))

	self.request_ubyte_put(uint32 >> 24)
	self.request_ubyte_put(uint32 >> 16)
	self.request_ubyte_put(uint32 >> 8)
	self.request_ubyte_put(uint32)

        if trace:
            print("{0}<=Maker_Bus.request_int_put({1})". \
	      format(trace_pad, uint32))

    def request_ushort_put(self, uint16):
        """ {Maker_Bus}: Append {uint16} to current request in {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.request_ushort_put({1})". \
              format(trace_pad, uint16))

	self.request_ubyte_put(uint16 >> 8)
	self.request_ubyte_put(uint16)

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.request_ushort_put({1})". \
              format(trace_pad, uint16))

    def response_begin(self):
        """ {Maker_Bus}: Begin a response sequence. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_begin() response={1}". \
              format(trace_pad, self.response))

        self.flush()

        if trace:
            print("{0}<=Maker_Bus.response_begin()".format(trace_pad))
            self.trace_pad = trace_pad

    def response_byte_get(self):
        """ {Maker_Bus}: Return next unsigned byte from response in {self}. """

	ubyte = self.response_ubyte_get()
	if ubyte & 0x80 != 0:
	    ubyte |= 0xffffff00
	return ubyte

    def response_end(self):
        """ {Maker_Bus}: End a response sequence. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_end() response={1}". \
              format(trace_pad, self.response))

        response = self.response
        response_length = len(response)
        assert len(response) == 0, \
          "{0} bytes left over from response".format(response_length)

        if trace:
            print("{0}<=Maker_Bus.response_end()".format(trace_pad))
            self.trace_pad = trace_pad


    def response_byte_get(self):
        """ {Maker_Bus}: Return next unsigned byte from response in {self}. """

	byte = self.response_ubyte_get()
	if byte & 0x80 != 0:
	    byte |= 0xffffff00
        return byte

    def response_short_get(self):
        """ {Maker_Bus}: Return next unsigned byte from response in {self}. """

	short= self.response_ushort_get()
	if short & 0x8000 != 0:
	    short |= 0xffff0000
        return short

    def response_int_get(self):
        """ {Maker_Bus}: Return next unsigned integer from response in
	    {self}. """

	byte0 = self.response_ubyte_get()
	byte1 = self.response_ubyte_get()
	byte2 = self.response_ubyte_get()
	byte3 = self.response_ubyte_get()
	result = (byte0 << 24) | (byte1 << 16) | (byte2 << 8) | byte3

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_int_get() result={1}". \
              format(trace_pad, result))

	return result

    def response_ubyte_get(self):
        """ {Maker_Bus}: Return next unsigned byte from response in {self}. """

        response = self.response

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_ubyte_get() response={1}". \
              format(trace_pad, response))

        ubyte = response[0]
        del response[0]

        if trace:
            print("{0}<=Maker_Bus.response_ubyte_get()=>{1}". \
              format(trace_pad, ubyte))
            self.trace_pad = trace_pad

        return ubyte

    def response_ushort_get(self):
        """ {Maker_Bus}: Return next unsigned short from response in {self}. """

        response = self.response

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_ushort_get() response={1}". \
              format(trace_pad, response))

        high_ubyte = self.response_ubyte_get()
        low_ubyte = self.response_ubyte_get()
        ushort = (high_ubyte << 8) | low_ubyte

        if trace:
            print("{0}<=Maker_Bus.response_ushort_get()=>{1}". \
              format(trace_pad, ushort))
            self.trace_pad = trace_pad

        return ushort

    def response_uint_get(self):
        """ {Maker_Bus}: Return next unsigned integer from response in {self}. """

        response = self.response

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.response_uint_get() response={1}". \
              format(trace_pad, response))

	byte3 = self.response_ubyte_get()
	byte2 = self.response_ubyte_get()
	byte1 = self.response_ubyte_get()
	byte0 = self.response_ubyte_get()
	
        uint = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | byte0

        if trace:
            print("{0}<=Maker_Bus.response_uint_get()=>{1}". \
              format(trace_pad, uint))
            self.trace_pad = trace_pad

        return uint

## @class Maker_Bus_Module
#
# Per module base class to interface with MakerBus modules.
#
# *Maker_Bus_Module* provides a base class from which sub-classes
# can be specialized.  The base class provides common communication
# methods.  The specialized sub-class provides the module specific
# register and function access to the module.

class Maker_Bus_Module:
    """ This represents a single module on the bus: """

    def __init__(self, maker_bus_base, address, offset):
        """ {Maker_Bus_Module}: Initialize {self} to contain {maker_bus_base}
            and {address}."""

        assert isinstance(maker_bus_base, Maker_Bus_Base)
        assert isinstance(address, int)
        assert isinstance(offset, int)

        self.maker_bus_base = maker_bus_base
        self.address = address
        self.offset = offset

    def auto_flush_set(self, flush_mode):
        """ {Maker_Bus_Module}:  This routine will set the auto flush mode for
            {self} to {flush_mode}.  When {flush_mode} is {True},
            each operation is immediately sent to the selected module.
            When {flush_mode} is {False}, the commands queue up until
            the request buffer is full or until {flush}() is explicitly
            called. """

        self.maker_bus_base.auto_flush_set(flush_mode)

    def flush(self):
        """ {Maker_Bus_Module}: This routine will cause any queued commands
            to be flushed.  """

        self.maker_bus_base.flush()

    def request_begin(self, command):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_begin(self.address, self.offset + command)

    def request_byte_put(self, byte):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_ubyte_put(byte)

    def request_character_put(self, character):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_ubyte_put(ord(character))

    def request_end(self):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_end()

    def request_int_put(self, int32):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_int_put(int32)

    def request_logical_put(self, logical):
	""" {Maker_Bus_Module}: """

        value = 0
        if logical:
            value = 1
        self.maker_bus_base.request_ubyte_put(value)

    def request_short_put(self, int16):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_short_put(int16)

    def request_ubyte_put(self, ubyte):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.request_ubyte_put(ubyte & 0xff)

    def request_uint_put(self, uint32):
	""" {Maker_Bus_Module}: """

        # High byte first, followed by low byte:
        self.request_uint_put(uint32)

    def request_ushort_put(self, uint16):
	""" {Maker_Bus_Module}: """

        # High byte first, followed by low byte:
        self.request_ushort_put(uint16)

    def response_begin(self):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.response_begin()

    def response_byte_get(self):
	""" {Maker_Bus_Module}: """

        return self.maker_bus_base.response_byte_get()

    def response_character_get(self):
	""" {Maker_Bus_Module}: """

        return chr(self.maker_bus_base.response_ubyte_get())

    def response_logical_get(self):
	""" {Maker_Bus_Module}: """

        return self.maker_bus_base.response_ubyte_get() != 0

    def response_byte_get(self):
	""" {Maker_Bus_Module}: """

        return self.maker_bus_base.response_byte_get()

    def response_short_get(self):
	""" {Maker_Bus_Module}: """

	return self.maker_bus_base.response_short_get()

    def response_int_get(self):
	""" {Maker_Bus_Module}: """

	return self.maker_bus_base.response_int_get()

    def response_ubyte_get(self):
	""" {Maker_Bus_Module}: """

        return self.maker_bus_base.response_ubyte_get()

    def response_ushort_get(self):
	""" {Maker_Bus_Module}: """

	return self.maker_bus_base.response_ushort_get()

    def response_uint_get(self):
	""" {Maker_Bus_Module}: """

	return self.maker_bus_base.response_uint_get()

    def response_end(self):
	""" {Maker_Bus_Module}: """

        self.maker_bus_base.response_end()
