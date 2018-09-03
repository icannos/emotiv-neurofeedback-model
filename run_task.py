from threading import Thread

from encephocus.genericapps import GenericFeedback, GenericTask
from encephocus.devices import EmotivTcpClient
from time import time


if __name__ == "__main__":
    eegdevice = EmotivTcpClient(format_data = "vector", window_size=50)
    attGame = GenericTask(device=eegdevice)

    attentionmodel = Thread(target=eegdevice.run)

    attentionmodel.start()

    attGame.run()
    pass