from tkinter import *
from threading import Thread

import numpy as np

import socket
import argparse
from keras.models import load_model


class AttentionFeedBack:
    on = True

    attention_x = 0.0
    attention_y = 0.0

    window = [[0,0,0,0,0,0,0,0,0,1,0,0,0,0]]

    BUFFER_SIZE = 256

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "01": 8, "02": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    def __init__(self, size=200, block_size=5, host="127.0.0.1", port=12991):
        self.master = Tk()
        self.size = size
        self.block_size = block_size
        self.host = host
        self.port = port

        self.can = Canvas(self.master, height=self.size * self.block_size, width=self.size * self.block_size,
                          bg="white")

        self.frame = Frame(self.master, height=self.size * self.block_size, width=self.size * self.block_size)

        self.can.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.__draw_center_cross()

        self.can.pack()
        self.frame.pack()


    def run(self):

        self.master.title("Attention FeedBack")
        self.animationLoop()

        self.master.mainloop()

        # If we reach this,  tkinter frame is closed and we can terminate linked thread
        self.on = False
        return 0

    def animationLoop(self):
        self.can.delete(ALL)
        self.__draw_center_cross()

        self.__draw_targets()
        self.__plot_attention()


        self.master.after(1, self.animationLoop)


    def __draw_targets(self):
        center = (int(self.size / 2))* self.block_size + 1, (int(self.size / 2) + 1)* self.block_size

        posx = center[0]-100
        posy = center[0] - 100
        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill="red")

        posx = center[0] + 100
        posy = center[0] - 100
        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill="red")

        posx = center[0] - 100
        posy = center[0] + 100
        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill="red")

        posx = center[0] + 100
        posy = center[0] + 100
        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill="red")


    def __draw_center_cross(self):
        center = int(self.size / 2) + 1, int(self.size / 2) + 1

        posx = center[0] * self.block_size - self.block_size
        posy = center[1] * self.block_size

        self.can.create_rectangle(posx, posy, posx + 3 * self.block_size, posy + self.block_size, fill="black")

        posx = center[0] * self.block_size
        posy = center[1] * self.block_size - self.block_size

        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + 3 * self.block_size, fill="black")

    def __plot_attention(self):
        posx = int(self.attention_x * self.block_size)
        posy = int(self.attention_y * self.block_size)

        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill="blue")


    def get_attention(self):
        '''
        test function
        :return:
        '''

        self.padding = 30

        self.attention_model = load_model("model-0.36.hdf5")
        while self.on:
            data = np.asarray(self.window)

            ampl = np.transpose(np.abs(np.fft.rfft(data,25, axis=0)))

            useful_freqs = [3,5,7]

            ampl = ampl[:][:, useful_freqs]
            ampl = np.reshape(ampl, (1, ampl.shape[0]*ampl.shape[1],))

            m = np.max(ampl)
            ampl = ampl / m

            corners = np.asarray([[self.size-self.padding,self.size-self.padding], [self.size-self.padding,self.padding]
                                     , [self.padding,self.padding], [self.padding,self.size-self.padding]])
            p = self.attention_model.predict(ampl)

            point = np.sum([corners[i] * p[0][i] for i in range(corners.shape[0])], axis=0)

            self.attention_x, self.attention_y = point[0], point[1]
            print(p)
            pass

        print("Terminate Attention Tracking Model")
        return 0

    def data2dic(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            return {field: float(field_list[index]) for field, index in self.FIELDS.items()}
        else:
            return -1

    def data2vector(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            return np.asarray([float(field_list[index]) for field, index in self.FIELDS.items() if
                               field != "COUNTER" and field != "DATA-TYPE" and field != "DATALINE_1" and field != "DATALINE_2"])
        else:
            return -1

    def geteegdata(self):
        TCP_IP = self.host
        TCP_PORT = self.port

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
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
            data = s.recv(self.BUFFER_SIZE, socket.MSG_WAITALL)

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
            fields = self.data2vector(buffer + msg_parts[0])

            # We setup the buffer for next step
            buffer = n_buffer

            if len(self.window) < 26:
                self.window.append(fields)
            else:
                self.window = self.window[1:] + [fields]

        s.close()

        print("Terminate EEG - TCP Client")
        return 0


if __name__ == "__main__":
    attGame = AttentionFeedBack()

    attentionmodel = Thread(target=attGame.geteegdata)
    eeg_thread = Thread(target=attGame.get_attention)

    eeg_thread.start()
    attentionmodel.start()

    target = attGame.run()
    pass
