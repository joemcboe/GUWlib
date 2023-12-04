import math
import numpy as np

PI = math.pi


class Signal(object):
    """
    Base class for signals.
    """

    def __init__(self, magnitude=1):
        """
        Initialize the Signal object.

        :param magnitude: Magnitude of the signal.
        """
        self.magnitude = magnitude

    def get_value_at(self, t):
        """
        Abstract method to get the value of the signal at a specific time.

        :param t: Time at which to evaluate the signal.
        :return: Signal value at time t.
        """
        pass


# BURST ----------------------------------------------------------------------------------------------------------------
class Burst(Signal):
    """
    Class representing a burst signal.
    """

    def __init__(self, center_frequency, n_cycles, magnitude=1, delta_t=0, window='hanning'):
        """
        Initialize the Burst object.

        :param center_frequency: Center frequency of the burst.
        :param n_cycles: Number of cycles in the burst.
        :param magnitude: Magnitude of the burst.
        :param delta_t: Time delay of the burst.
        :param window: Type of window function ('hanning' by default).
        """
        super(Burst, self).__init__(magnitude=magnitude)
        self.center_frequency = center_frequency
        self.n_cycles = n_cycles
        self.window = window
        self.delta_t = delta_t

    def get_value_at(self, t):
        """
        Get the value of the burst signal at a specific time.

        :param t: Time at which to evaluate the burst signal.
        :return: Signal value at time t.
        """
        f = self.center_frequency
        n_cycles = self.n_cycles
        dt = self.delta_t

        if self.window == 'hanning':
            length = n_cycles * (1 / f)
            y = math.cos(2 * PI * f * (t - dt))
            hanning = math.sin(PI * (t - dt) / length) ** 2 if (dt <= t <= length + dt) else 0
            return y * hanning
        else:
            raise ValueError("Unsupported window type: {}".format(self.window))


# DIRAC IMPULSE --------------------------------------------------------------------------------------------------------
class DiracImpulse(Signal):
    """
    Class representing a Dirac impulse signal.
    """

    def __init__(self, magnitude=1):
        """
        Initialize the DiracImpulse object.

        :param magnitude: Magnitude of the Dirac impulse.
        """
        super(DiracImpulse, self).__init__(magnitude=magnitude)

    def get_value_at(self, t):
        """
        Get the value of the Dirac impulse signal at a specific time.

        :param t: Time at which to evaluate the Dirac impulse signal.
        :return: Signal value at time t.
        """
        return self.magnitude if (t == 0) else 0
