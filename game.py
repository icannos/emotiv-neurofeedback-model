from tkinter import *
import argparse
from threading import Thread

import numpy as np
from time import sleep

class AttentionFeedBack():
    on = True

    attention_x = 0.0
    attention_y = 0.0

    def __init__(self, size=150, block_size=5):
        self.master =  Tk()
        self.size = size
        self.block_size = block_size

        self.can = Canvas(self.master, height=self.size * self.block_size, width=self.size * self.block_size, bg="white")



        self.frame = Frame(self.master, height=self.size * self.block_size, width=self.size * self.block_size)

        self.can.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.__draw_center_cross()

        self.can.pack()
        self.frame.pack()

    def run(self):

        self.master.title("Attention FeedBack")
        self.animationLoop()

        self.master.mainloop()

        return 0


    def animationLoop(self):
        self.can.delete(ALL)
        self.__draw_center_cross()
        self.__plot_attention()

        self.master.after(500, self.animationLoop)



    def __draw_center_cross(self):
        center = int(self.size / 2) + 1, int(self.size / 2) + 1

        posx = center[0] * self.block_size - self.block_size
        posy = center[1] * self.block_size

        self.can.create_rectangle(posx, posy, posx + 3 * self.block_size, posy+ self.block_size, fill="black")

        posx = center[0] * self.block_size
        posy = center[1] * self.block_size - self.block_size

        self.can.create_rectangle(posx, posy, posx + self.block_size, posy + 3* self.block_size, fill="black")

    def __plot_attention(self):
        posx = int(self.attention_x*self.block_size)
        posy = int(self.attention_y*self.block_size)

        self.can.create_rectangle(posx, posy, posx+ self.block_size, posy + self.block_size, fill="red")


    def get_attention(self):
        while True:
            x,y = np.random.uniform(-1, 1)+2, np.random.uniform(-1, 1)+2
            x = int(10*x)*self.block_size
            y =  int(10*y)*self.block_size

            self.attention_x = x
            self.attention_y = y
            sleep(0.200)



if __name__ == "__main__":
    attGame = AttentionFeedBack()



    eeg_thread = Thread(target=attGame.get_attention)
    eeg_thread.start()

    target = attGame.run()
    pass
