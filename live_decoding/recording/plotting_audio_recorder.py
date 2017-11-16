import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import time
from recording.audio_recorder import AudioRecorder

THRESHOLD = 2500   # The threshold intensity that defines silence
                   # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5   # Previous audio (in seconds) to prepend. When noise
                   # is detected, how much of previously recorded audio is
                   # prepended. This helps to prevent chopping the beggining
                   # of the phrase.


class PlottingAudioRecorder(AudioRecorder):
    def __init__(self, max_fps=120, samples_per_window=2048, window_height=10000):
        super().__init__()
        self.__min_interval = 1/max_fps
        self.__prev_time = time.time()
        self.__samples_per_window = samples_per_window
        self.__window_size = samples_per_window * self._sample_size
        self.__window_height = window_height

    @property
    def plotting(self):
        return plt.get_fignums()

    def show_plot(self):
        fig, signal_line, envelope_line = self.init_plot()
        while plt.get_fignums():
            if len(self._samples) > self.__window_size:
                self.update_plot(fig, signal_line, envelope_line, self._samples[-self.__window_size:])
            self.maintain_fps()

    def init_plot(self):
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.__samples_per_window)
        ax.set_ylim(-self.__window_height/2, self.__window_height/2)
        signal_line = ax.plot(np.arange(self.__samples_per_window), np.zeros(self.__samples_per_window), label='signal')[0]
        envelope_line = ax.plot(np.arange(self.__samples_per_window), np.zeros(self.__samples_per_window), label='envelope')[0]
        plt.ion()
        plt.legend()
        plt.show()
        return fig, signal_line, envelope_line

    def update_plot(self, fig, signal_line, envelope_line, samples):
        signal = np.fromstring(bytes(samples), 'Int16')
        analytical_signal = hilbert(signal)
        amplitude_envelope = np.abs(analytical_signal)

        signal_line.set_ydata(signal)
        envelope_line.set_ydata(amplitude_envelope)
        fig.canvas.flush_events()

    def maintain_fps(self):
        difference = self.__min_interval - (time.time() - self.__prev_time)
        self.__prev_time = time.time()
        if difference > 0:
            time.sleep(difference)


    def _on_chunk(self):
        pass

    def _on_file_saved(self, filename):
        pass
