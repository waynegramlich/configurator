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

        serial.open()
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

            if trace:
                print("{0}serial.flush()".format(trace_pad))

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
                    print("{0}response={1}, checksum={2:x}". \
                      format(trace_pad, response, checksum))

                if checksum != response_checksum:
                    print("Got checksum of {0:x} instead of {1:x}". \
                      format(checksum, response_checksum))
                    del response[:]

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.flush() response={1}". \
              format(trace_pad, self.response))

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
            print("{0}<=Maker_Bus.frame_get()=>{1:x}".format(trace_pad, frame))
        return frame

    def frame_put(self, frame):
        """ {Maker_Bus}: Send frame to the bus connected to {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.frame_put({1:x})".format(trace_pad, frame))

        serial = self.serial
        if (frame > 0xff or (0xc1 <= frame and frame <= 0xc4)):
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
            print("{0}<=Maker_Bus.frame_put({1:x})".format(trace_pad, frame))


    def request_begin(self, address, command):
        """ {Maker_Bus}: Append {command} to self.request. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            print("{0}=>Maker_Bus.request_begin({1:x})". \
              format(trace_pad, command))
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
            print("{0}<=Maker_Bus.request_begin({1:x})". \
              format(trace_pad, command))
            self.trace_pad = trace_pad

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

    def request_ubyte_put(self, ubyte):
        """ {Maker_Bus}: Append {ubyte} to current request in {self}. """

        trace = self.trace
        if trace:
            trace_pad = self.trace_pad
            self.trace_pad = trace_pad + " "
            print("{0}=>Maker_Bus.request_ubyte_get({0})". \
              format(trace_pad, ubyte))

        request = self.request
        request.append(ubyte)

        if trace:
            self.trace_pad = trace_pad
            print("{0}<=Maker_Bus.request_ubyte_get({1}) request={2}". \
              format(trace_pad, ubyte, request))

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
            print("{0}=>Maker_Bus.response_ubyte_get() response={1}". \
              format(trace_pad, response))

        high_ubyte = self.response_ubyte_get()
        low_ubyte = self.response_ubyte_get()
        ushort = (high_ubyte << 8) | low_ubyte

        if trace:
            print("{0}<=Maker_Bus.response_ubyte_get()=>{1}". \
              format(trace_pad, ushort))
            self.trace_pad = trace_pad

        return ushort

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
        """ """

        self.maker_bus_base.request_begin(self.address, self.offset + command)

    def request_character_put(self, character):
        """ """

        self.maker_bus_base.request_ubyte_put(ord(character))

    def request_end(self):
        """ """

        self.maker_bus_base.request_end()

    def request_logical_put(self, logical):
        """ """

        value = 0
        if logical:
            value = 1
        self.maker_bus_base.request_ubyte_put(value)

    def request_ubyte_put(self, ubyte):
        """ """

        self.maker_bus_base.request_ubyte_put(ubyte & 0xff)

    def request_ushort_put(self, ushort):
        """ """

        # High byte first, followed by low byte:
        self.request_ubyte_put(ushort >> 8)
        self.request_ubyte_put(ushort)

    def response_begin(self):
        """ """

        self.maker_bus_base.response_begin()

    def response_character_get(self):
        """ """

        return chr(self.maker_bus_base.response_ubyte_get())

    def response_logical_get(self):
        """ """

        return self.maker_bus_base.response_ubyte_get() != 0

    def response_ubyte_get(self):
        """ """

        return self.maker_bus_base.response_ubyte_get()

    def response_ushort_get(self):
        """ """

        high_byte = self.response_ubyte_get()
        low_byte = self.response_ubyte_get()
        return (high_byte << 8) | low_byte

    def response_end(self):
        """ """

        self.maker_bus_base.response_end()
