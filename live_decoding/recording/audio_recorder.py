from abc import abstractmethod
import pyaudio
import wave

# Microphone stream config.
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 10      # in ms

class AudioRecorder:
    def __init__(self, format=FORMAT, channels=CHANNELS, sample_rate=SAMPLE_RATE, sample_width=SAMPLE_WIDTH):
        self.__engine = pyaudio.PyAudio()
        self.__stream = None

        self._channels = channels
        self._format = format
        self._sample_rate = sample_rate
        self._sample_size = self.__engine.get_sample_size(format)
        self._sample_width = sample_width
        self._samples = bytearray()
        self._chunk = bytearray()
        self._chunk_size = int(sample_rate * sample_width / 1000)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__stream.is_stopped():
            self.stop()
        self.__stream.close()

    @property
    def is_recording(self):
        return not self.__stream.is_stopped()

    def _record_callback(self, in_data, sample_count, time_info, status):
        self._chunk = in_data
        self._samples += in_data
        self._on_chunk()
        return None, pyaudio.paContinue

    @abstractmethod
    def _on_chunk(self):
        pass

    @abstractmethod
    def _on_file_saved(self, filename):
        pass

    def start(self):
        self.__stream = self.__engine.open(format=self._format,
                                           channels=self._channels,
                                           rate=self._sample_rate,
                                           frames_per_buffer=self._chunk_size,
                                           input=True,
                                           stream_callback=self._record_callback)

    def pause(self):
        self.__stream.stop_stream()
        self.__stream.close()

    def stop(self, save_filename=''):
        self.__stream.stop_stream()
        self.__stream.close()
        if save_filename:
            self._save(save_filename)
        self._reset()

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
