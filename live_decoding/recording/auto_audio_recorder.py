from datetime import datetime
from time import time
from os.path import realpath

import webrtcvad

from recording.audio_recorder import AudioRecorder

SPEECH_THRESHOLD = 1000  # Time in milliseconds since last frame containing potential speech to classify sound as speech


class AutoAudioRecorder(AudioRecorder):
    def __init__(self, speaker_name):
        super().__init__()
        self.__threads = []
        self.__voice_activity_detector = webrtcvad.Vad()
        self.__speaker_name = speaker_name
        self.__prev_is_speech = False
        self.__is_speech_time = time()
        self._initialize()

    def _on_chunk(self, chunk):
        super()._on_chunk(chunk)
        is_speech = self.__voice_activity_detector.is_speech(chunk, self._sample_rate)

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
        super()._on_file_saved(filename)

    def register_on_file_saved_listener(self, on_file_saved_listener):
        self._on_file_saved_listener = on_file_saved_listener