from datetime import datetime
from time import time
from os.path import realpath

import webrtcvad

from recording.audio_recorder import AudioRecorder

SPEECH_THRESHOLD = 500  # Time in milliseconds since last frame containing potential speech to classify sound as speech

class AutoAudioRecorder(AudioRecorder):
    def __init__(self, speaker_name, decoder=None):
        super().__init__()
        self.__threads = []
        self.__decoder = decoder
        self.__voice_activity_detector = webrtcvad.Vad()
        self.__speaker_name = speaker_name
        self.__prev_is_speech = False
        self.__is_speech_time = time()

    def _on_chunk(self):
        is_speech = self.__voice_activity_detector.is_speech(self._chunk, self._sample_rate)

        if self.__prev_is_speech != is_speech:
            if is_speech:
                self.__is_speech_time = time()

            if (time() - self.__is_speech_time) * 1000 > SPEECH_THRESHOLD:
                filename = '_'.join([self.__speaker_name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')]) + '.wav'
                filename = realpath(filename)
                self._save(filename)
            else:
                self._reset()
        self.__prev_is_speech = is_speech

    def _on_file_saved(self, filename):
        if self.__decoder:
            print(self.__decoder.decode(filename))
