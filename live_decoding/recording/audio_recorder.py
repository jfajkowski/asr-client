from abc import abstractmethod
import pyaudio
import wave

# Microphone stream config.
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 10      # in ms



class AudioRecorder:
    def __init__(self, format=FORMAT, channels=CHANNELS, sample_rate=SAMPLE_RATE, sample_width=SAMPLE_WIDTH,
                 on_chunk_listener=None, on_file_saved_listener=None):
        self.__engine = pyaudio.PyAudio()
        self.__stream = None

        self._channels = channels
        self._format = format
        self._sample_rate = sample_rate
        self._sample_size = self.__engine.get_sample_size(format)
        self._sample_width = sample_width
        self._samples = bytearray()
        self._chunk_size = int(sample_rate * sample_width / 1000)
        self._on_chunk_listener = on_chunk_listener
        self._on_file_saved_listener = on_file_saved_listener

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__stream:
            self.__stream.close()

    @property
    def is_recording(self):
        return not self.__stream.is_stopped()

    @abstractmethod
    def _on_chunk(self, chunk):
        if self._on_chunk_listener:
            self._on_chunk_listener(chunk)

    @abstractmethod
    def _on_file_saved(self, filename):
        if self._on_file_saved_listener:
            self._on_file_saved_listener(filename)

    def _initialize(self):
        self.__stream = self.__engine.open(format=self._format,
                                           channels=self._channels,
                                           rate=self._sample_rate,
                                           frames_per_buffer=self._chunk_size,
                                           input=True,
                                           stream_callback=self._record_callback)

    def _record_callback(self, in_data, sample_count, time_info, status):
        self._samples += in_data
        self._on_chunk(in_data)
        return None, pyaudio.paContinue

    def _save(self, filename):
        with wave.open(filename, mode='wb') as f_out:
            f_out.setnchannels(CHANNELS)
            f_out.setsampwidth(pyaudio.get_sample_size(FORMAT))
            f_out.setframerate(SAMPLE_RATE)
            f_out.writeframes(self._samples)
        self._on_file_saved(filename)

    def _reset(self):
        self._samples = bytearray()
        self._chunk = bytearray()
