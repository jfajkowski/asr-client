from abc import abstractmethod
from queue import Queue


class Decoder:
    def __init__(self):
        self._decoding_queue = Queue()

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def decode(self, wav_file):
        pass

    @property
    def queue_length(self):
        return self._decoding_queue.qsize()