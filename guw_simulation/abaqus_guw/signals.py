import math
import numpy as np

PI = math.pi


class Burst:
    def __init__(self, carrier_frequency, n_cycles, dt=0, window='hanning'):
        self.carrier_frequency = carrier_frequency
        self.n_cycles = n_cycles
        self.dt = dt
        self.window = window
        pass

    def get_value_at(self, t):
        """
        Returns the value of the signal at time t.
        """
        f = self.carrier_frequency
        dt = self.dt
        n_cycles = self.n_cycles

        if self.window == 'hanning':
            length = n_cycles * (1 / f)
            y = math.cos(2 * PI * f * (t - dt))
            hanning = math.sin(PI * (t - dt) / length) ** 2 if (dt <= t <= length + dt) else 0
            return y * hanning
        else:
            pass

    def get_duration(self):
        """
        Returns the duration of the signal (equivalent to the width of window-function).
        """
        f = self.carrier_frequency
        dt = self.dt
        n_cycles = self.n_cycles
        length = n_cycles * (1 / f)
        return length

    def get_max_contained_frequency(self):
        """
        Inspects the frequency spectrum of the signal and returns the highest frequency
        at which the normalized amplitude is >= 0.1.
        """
        duration = self.get_duration()
        n_samples = int(self.carrier_frequency * 3 * 2 * duration * 20)
        t_values = np.linspace(0, duration * 20, n_samples)
        y_values = [self.get_value_at(t=t) for t in t_values]

        # Calculate the FFT of the signal
        fft_result = np.fft.fft(y_values)
        fft_result = fft_result / np.max(fft_result)
        amplitude = np.abs(fft_result[:n_samples // 2])

        # Determine the sampling frequency and create a frequency vector
        sampling_frequency = 1 / (t_values[1] - t_values[0])
        frequencies = np.fft.fftfreq(n_samples, d=1 / sampling_frequency)
        frequencies = frequencies[:n_samples // 2]

        # Find the highest frequency where the amplitude is greater than 0.1
        indices = np.where(amplitude > 0.1)[0]
        if len(indices) > 0:
            last_index = indices[-1]
            highest_contained_frequency = frequencies[last_index]
        else:
            highest_contained_frequency = self.carrier_frequency

        return highest_contained_frequency

    # def plot(self):
    #     """
    #     Plots the signal.
    #     """
    #     dt = self.dt
    #     length = self.get_duration()
    #     t_values = np.linspace(dt - length * 2, dt + length * 3, num=1000)
    #     y_values = [self.get_value_at(t=t) for t in t_values]
    #     plt.plot(t_values, y_values, linestyle='-')
    #     plt.xlabel('t')
    #     plt.ylabel('y')
    #     plt.grid(True)
    #     plt.show()
