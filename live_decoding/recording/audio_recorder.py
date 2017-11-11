from abc import abstractmethod
import pyaudio
import wave

# Microphone stream config.
CHUNK = 1024      # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class AudioRecorder:
    def __init__(self):
        self._frames = bytearray()
        self._prev_frames = bytearray()

        self.__engine = pyaudio.PyAudio()
        self.__stream = self.__engine.open(format=FORMAT,
                                           channels=CHANNELS,
                                           rate=RATE,
                                           input=True,
                                           stream_callback=self._record_callback)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__stream.is_stopped():
            self.stop()
        self.__stream.close()

    @property
    def is_recording(self):
        return not self.__stream.is_stopped()

    def _record_callback(self, in_data, frame_count, time_info, status):
        self._prev_frames = in_data
        self._frames += in_data
        self._on_frames_recorded()
        return None, pyaudio.paContinue

    @abstractmethod
    def _on_frames_recorded(self):
        pass

    @abstractmethod
    def _on_file_saved(self):
        pass

    def start(self):
        self.__stream.start_stream()

    def pause(self):
        self.__stream.stop_stream()

    def stop(self, save_filename=''):
        self.__stream.stop_stream()
        if save_filename:
            self._save(save_filename)
        self.__reset()

    def _save(self, filename):
        with wave.open(filename, mode='wb') as f_out:
            f_out.setnchannels(CHANNELS)
            f_out.setsampwidth(pyaudio.get_sample_size(FORMAT))
            f_out.setframerate(RATE)
            f_out.writeframes(self._frames)
        self._on_file_saved()

    def __reset(self):
        self._frames = bytearray()
        self._prev_frames = bytearray()
