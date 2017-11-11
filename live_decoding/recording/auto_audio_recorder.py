import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

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


class AutoAudioRecorder(AudioRecorder):
    def __init__(self):
        super().__init__()
        plt.ion()

    def _on_frames_recorded(self):
        pass
        # signal = list(self._prev_frames)
        # print(signal)
        # t = list(range(len(signal)))
        # # analytic_signal = hilbert(signal)
        # # amplitude_envelope = np.abs(analytic_signal)
        # plt.plot(t, signal, label='signal')
        # # plt.plot(t, amplitude_envelope, label='envelope')
        # plt.pause(0.05)

    def _on_file_saved(self):
        pass
