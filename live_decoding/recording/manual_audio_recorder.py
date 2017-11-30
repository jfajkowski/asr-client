from recording.audio_recorder import AudioRecorder


class ManualAudioRecorder(AudioRecorder):
    def __init__(self):
        super().__init__()

    def start(self):
        self._initialize()

    def pause(self):
        self.__stream.stop_stream()
        self.__stream.close()

    def stop(self, save_filename=''):
        self.__stream.stop_stream()
        self.__stream.close()
        if save_filename:
            self._save(save_filename)
        self._reset()

    def _on_file_saved(self, filename):
        super()._on_file_saved(filename)

    def _on_chunk(self, chunk):
        super()._on_chunk(chunk)
