from abc import abstractmethod


class Decoder:
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def decode(self, wav_file):
        pass
