# -*- coding: utf8 -*-
#
# Cykit Example TCP - Client
# Icannos
#

import socket
import numpy as np
import argparse
from time import time


class EmotivTcpClient():
    __BUFFER_SIZE = 256

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "01": 8, "02": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    # Store data gathered through the TCP connection, can be only the last N point or everything the begining
    data = []

    # When turn down to False stop the run loop
    on = True

    def __init__(self, format_data=None, host="127.0.0.1", port=12991, mode="window", window_size=50, timer=False):
        self.TCP_IP = host
        self.TCP_PORT = port

        self.SAMPLE_RATE = 256

        self.mode = mode
        self.window_size = window_size

        if format_data is None or format_data == "dic":
            self.format_data = self.data2dic
        elif format_data == "vector":
            self.format_data = self.data2vector
        else:
            self.format_data = format_data

        self.timer = timer

    def data2dic(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            return {field: float(field_list[index]) for field, index in self.FIELDS.items()}
        else:
            return -1

    def data2vector(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            # First element is the time
            if self.timer:
                return np.asarray([time()] + [float(field_list[index]) for field, index in self.FIELDS.items()
                                              if field != "COUNTER"
                                              and field != "DATA-TYPE"
                                              and field != "DATALINE_1"
                                              and field != "DATALINE_2"
                                              ])
            else: # No time, only data
                return np.asarray([float(field_list[index]) for field, index in self.FIELDS.items()
                                              if field != "COUNTER"
                                              and field != "DATA-TYPE"
                                              and field != "DATALINE_1"
                                              and field != "DATALINE_2"
                                              ])
        else:
            return -1

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.TCP_IP, self.TCP_PORT))
        s.send(b"\r\n")

        # To read the header msgs about cykit etc...
        s.recv(168, socket.MSG_WAITALL)

        # Local buffer to store parts of the messages
        buffer = b''

        # If when when split by \r, \r was the last character of the message, we know that we have to remove \n from
        # the begining of the next message
        remove_newline = False

        while self.on:
            # We read a chunk
            data = s.recv(self.__BUFFER_SIZE, socket.MSG_WAITALL)

            # If we have to remove \n at the begining
            if remove_newline:
                data = data[1:]
                remove_newline = False

            # Splitting the chunk into the end of the previous message and the begining of the next message
            msg_parts = data.split(b'\r')

            # If the second part ends with nothing when splitted we will have to remove \n next time
            if msg_parts[-1] == b'':
                remove_newline = True
                # Therefore the buffer for the next step is empty
                n_buffer = b''
            else:
                # otherwise we store the begining of the next message as the next buffer
                n_buffer = msg_parts[-1][1:]

            # We interprete a whole message (begining from the previous step + the end
            fields = self.format_data(buffer + msg_parts[0])

            # We setup the buffer for next step
            buffer = n_buffer

            if self.mode == "all":
                self.data.append(fields)
            elif self.mode == "window":

                if len(self.data) < self.window_size:
                    self.data.append(fields)
                else:
                    self.data = self.data[1:] + [fields]

        s.close()

        print("Terminate EEG - TCP Client")
        return 0
