from tkinter import *
import numpy as np

from keras.models import load_model
from time import sleep, time
from scipy.io import savemat


class GenericFeedback:
    on = True

    attention_x = 0.0
    attention_y = 0.0

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "01": 8, "02": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    def __init__(self, size=300, block_size=5, device=None, model_path="model-0.38.hdf5"):
        self.size = size
        self.block_size = block_size
        self.device = device
        self.model_path = model_path

        self.fen_init()

    def fen_init(self):
        '''
        Used in the __init__ to define the window
        :return:
        '''
        self.master = Tk()
        self.can = Canvas(self.master, height=self.size * self.block_size, width=self.size * self.block_size,
                          bg="white")

        self.frame = Frame(self.master, height=self.size * self.block_size, width=self.size * self.block_size)

        self.can.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.__draw_center_cross()

        self.can.pack()
        self.frame.pack()

    def run(self):
        '''
        Create the window and start the animation thread
        :return: None
        '''
        self.master.title("Attention FeedBack")
        self.animationLoop()

        self.master.mainloop()

        # If we reach this,  tkinter frame is closed and we can terminate linked thread
        self.on = False
        # Close the device
        self.device.on = False
        return

    def animationLoop(self):
        '''
        Animation loop body this is called at each screen refresh
        :return: None
        '''
        self.can.delete(ALL)
        self.__draw_center_cross()

        self.__draw_targets()
        self.__plot_attention()

        self.master.after(1, self.animationLoop)

        return

    def get_attention(self):
        '''
        Get data from the device, compute fft etc... and use a model to predict attention, that's the default function.
        Just set the attention_x, attention_y values
        This sould be run in a separate thread.
        :return:
        '''

        self.padding = 30

        self.attention_model = load_model(self.model_path)

        while self.on:
            # Do nothing if no available data
            if len(self.device.data) == 0:
                sleep(0.1)
                continue
            # Get data from the more recent to the oldest
            data = np.asarray(reversed(self.device.data))

            ampl = np.transpose(np.abs(np.fft.rfft(data, 50, axis=0)))

            # Best freqs to use
            useful_freqs = [3, 5, 7]

            ampl = ampl[:][:, useful_freqs]
            ampl = np.reshape(ampl, (1, ampl.shape[0] * ampl.shape[1],))

            m = np.max(ampl)
            ampl = ampl / m

            corners = np.asarray(
                [[self.size - self.padding, self.size - self.padding], [self.size - self.padding, self.padding]
                    , [self.padding, self.padding], [self.padding, self.size - self.padding]])
            p = self.attention_model.predict(ampl)

            point = np.sum([corners[i] * p[0][i] for i in range(corners.shape[0])], axis=0)

            self.attention_x, self.attention_y = point[0], point[1]

            pass

        print("Terminate Attention Tracking Model")
        return 0

    def __draw_targets(self):
        center = (int(self.size / 2)) * self.block_size + 1, (int(self.size / 2) + 1) * self.block_size

        posx = center[0] - 100
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

class GenericTask:
    on = True

    BUFFER_SIZE = 256

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "01": 8, "02": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    POS_TARGET = []
    DATES_TARGET = []
    DATES_CLUE = []
    POS_CLUE = []
    ANSWERS = []

    answer = None

    def __init__(self, size=250, block_size=5, device=None, model_path="model-0.38.hdf5", path_save_data="data"):
        self.size = size
        self.block_size = block_size
        self.device = device
        self.model_path = model_path
        self.target_size = 2
        self.path_save_data = path_save_data

        self.begin = time()

        self.fen_init()

    def fen_init(self):
        '''
        Used in the __init__ to define the window
        :return:
        '''

        self.master = Tk()

        self.master.attributes('-fullscreen', True)

        self.can = Canvas(self.master, height=self.size * self.block_size, width=self.size * self.block_size,
                          bg="white")

        self.frame = Frame(self.master, height=self.size * self.block_size, width=self.size * self.block_size)

        self.can.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.__draw_center_cross()

        self.master.bind("q", self.answer_different)
        self.master.bind("d", self.answer_same)

        self.can.pack()
        self.frame.pack()

    def answer_different(self, d):
        self.answer = -1

    def answer_same(self, d):
        self.answer = 1

    def run(self):
        '''
        Create the window and start the animation thread
        :return: None
        '''
        self.master.title("Attention Task")
        self.animationLoop(0)

        self.master.mainloop()

        # dump data

        savemat(self.path_save_data, {"EEG": np.asarray(self.device.data) - self.begin,
                                      "POS_TARGET": self.POS_TARGET,
                                      "POS_CLUE": self.POS_CLUE,
                                      "DATES_TARGET": self.DATES_TARGET,
                                      "DATES_CLUE": self.DATES_CLUE,
                                      "ANSWERS": self.ANSWERS
                                      })

        # If we reach this,  tkinter frame is closed and we can terminate linked thread
        self.on = False
        # Close the device
        self.device.on = False
        return

    def animationLoop(self, state):
        '''
        Animation loop body this is called at each screen refresh
        :return: None
        '''



        if state == 0:
            print(self.ANSWERS)
            self.can.delete(ALL)
            self.__draw_center_cross()

            self.answer = 0

            self.rst_time = np.random.randint(1, 5 + 1)

            self.target_pos = np.random.randint(1, 4 + 1)
            self.clue_pos = np.random.randint(1, 4 + 1)

            self.target_sleeptime = np.random.randint(1, 5 + 1)

            self.master.after(self.rst_time*1000, self.animationLoop, 1)

        elif state == 1:
            self.__draw_clue(self.clue_pos)
            self.POS_CLUE.append(self.clue_pos)
            self.DATES_CLUE.append(time()-self.begin)

            self.master.after(500, self.animationLoop, 2)

        elif state == 2:
            self.can.delete(ALL)
            self.__draw_center_cross()

            self.master.after(self.target_sleeptime*1000, self.animationLoop, 3)

        elif state == 3:
            self.__draw_target(self.target_pos, color="#f7f6ef", distance=300)
            self.POS_TARGET.append(self.clue_pos)
            self.DATES_TARGET.append(time()-self.begin)

            self.master.after(200, self.animationLoop, 4)

        elif state == 4:
            self.can.delete(ALL)
            self.__draw_center_cross()

            self.master.after(1000, self.animationLoop, 5)

        elif state == 5:
            self.ANSWERS.append(self.answer)
            self.master.after(10, self.animationLoop, 0)


    def __draw_clue(self, pos, color="red", distance=100):
        center = (int(self.size / 2)) * self.block_size + 1, (int(self.size / 2) + 1) * self.block_size
        posx, posy = 0, 0

        if pos == 1:
            posx = center[0] + distance
            posy = center[0] + distance

        elif pos == 2:
            posx = center[0] - distance
            posy = center[0] + distance

        elif pos == 3:
            posx = center[0] - distance
            posy = center[0] - distance

        elif pos == 4:
            posx = center[0] + distance
            posy = center[0] - distance

        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + self.block_size, fill=color)
        
    def __draw_target(self, pos, color="red", distance=100):
        center = (int(self.size / 2)) * self.block_size + 1, (int(self.size / 2) + 1) * self.block_size
        posx, posy = 0, 0

        if pos == 1:
            posx = center[0] + distance
            posy = center[0] + distance

        elif pos == 2:
            posx = center[0] - distance
            posy = center[0] + distance

        elif pos == 3:
            posx = center[0] - distance
            posy = center[0] - distance

        elif pos == 4:
            posx = center[0] + distance
            posy = center[0] - distance

        self.can.create_rectangle(posx, posy, posx + self.target_size, posy + self.target_size, fill=color)

    def __draw_targets(self):
        center = (int(self.size / 2)) * self.block_size + 1, (int(self.size / 2) + 1) * self.block_size

        posx = center[0] - 100
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
