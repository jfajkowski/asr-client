import subprocess
from datetime import datetime
from threading import Thread
from time import time

import re

import multiprocessing

from recording.audio_recorder import AudioRecorder
import webrtcvad


SPEECH_THRESHOLD = 500  # Time in milliseconds since last frame containing potential speech to classify sound as speech

class AutoAudioRecorder(AudioRecorder):
    def __init__(self, speaker_name):
        super().__init__()
        self._threads = []
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
                filename = '_'.join([self.__speaker_name, datetime.now().strftime('%Y-%m-%d_%H-%M-%S')])
                self._save(filename)
                thread = Thread(target=self._recognize_speech, args=[filename])
                self._threads.append(thread)
                thread.start()
            else:
                self._reset()
        self.__prev_is_speech = is_speech

    def _recognize_speech(self, filename):
        speech_recognition = subprocess.run(['/home/fajqa/kaldi/src/online2bin/online2-wav-gmm-latgen-faster',
                                             '--config=/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/conf/online_decoding.conf',
                                             '--word-symbol-table=/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/graph/words.txt',
                                             '/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/graph/HCLG.fst',
                                             'ark:echo SPEAKER UTTERANCE|',
                                             'scp:echo UTTERANCE {}|'.format(filename),
                                             'ark:/dev/null'], stderr=subprocess.PIPE)
        result = speech_recognition.stderr.decode('utf-8')
        match = re.findall(r'UTTERANCE (.+)', result)
        if match and len(match) > 1:
            print(match[1].capitalize().strip() + '.')

    def _on_file_saved(self):
        pass
