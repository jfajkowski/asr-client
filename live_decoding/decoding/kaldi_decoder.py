import subprocess

import re
from queue import Queue
from threading import Thread

from decoder import Decoder


class KaldiDecoder(Decoder):
    def __init__(self, model_dir):
        self._reading_queue = Queue()
        self._decoding_queue = Queue()
        self._model_dir = model_dir
        self._process = None
        self._running = False

    def initialize(self):
        self._running = True
        self._process = subprocess.Popen(['./decoding/kaldi-gmm-live-decoder',
                                         '--config=/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/conf/online_decoding.conf',
                                         '--word-symbol-table=/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/graph/words.txt',
                                         '/home/fajqa/PycharmProjects/asr-system/pipeline/builds/pl-PL/0.0.1/exp/mono/graph/HCLG.fst',
                                         'ark:echo SPEAKER UTTERANCE|',
                                         'scp:-',
                                         'ark:/dev/null'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self._reading_thread = Thread(target=self._read)
        self._reading_thread.start()

    def decode(self, wav_file):
        self._process.stdin.write('{}\t{}\n'.format(wav_file, wav_file).encode('UTF-8'))
        self._process.stdin.flush()
        self._reading_queue.put(wav_file)
        return self._decoding_queue.get(block=True)

    def _read(self):
        while self._running:
            wav_file = self._reading_queue.get(block=True)

            while True:
                result = self._process.stderr.readline().decode('UTF-8')
                match = re.findall(r'^{} (.+)'.format(wav_file), result)
                if match:
                    self._decoding_queue.put(match[0].capitalize().strip() + '.')
                    break