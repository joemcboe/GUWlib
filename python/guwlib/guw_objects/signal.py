import math


class Signal(object):
    """
    Base class for signals.
    """

    def __init__(self, magnitude=1):
        """
        :param float magnitude: Magnitude of the signal.

        :ivar float magnitude: Magnitude of the signal.
        """
        self.magnitude = magnitude

    def get_value_at(self, t):
        """
        Returns the value of the signal at a specific time.

        :param float t: Time at which to evaluate the signal.

        :return: (float) Signal value at time t.
        """
        pass

    def get_duration(self):
        """
        Returns the duration for which the signal is non-zero.

        :return: (float) Signal duration.
        """
        pass


# BURST ----------------------------------------------------------------------------------------------------------------
class Burst(Signal):
    """
    Class representing a burst signal.

    A burst consists of a concise number of cycles of a sinusoidal signal, multiplied by a window function.
    """

    def __init__(self, center_frequency, n_cycles, magnitude=1, delta_t=0, window='hanning'):
        """
        :param float center_frequency: Center frequency of the burst.
        :param int n_cycles: Number of cycles in the burst.
        :param float magnitude: Magnitude of the burst.
        :param float delta_t: Time delay of the burst.
        :param str window: Type of window function, either ``rectangle``, ``hanning``,
            ``hamming`` or ``blackmann`` (default: ``hanning``).

        :ivar float center_frequency: Center frequency of the burst.
        :ivar int n_cycles: Number of cycles in the burst.
        :ivar float delta_t: Time delay of the burst.
        :ivar str window: Type of window function.
        """
        super(Burst, self).__init__(magnitude=magnitude)
        self.center_frequency = center_frequency
        self.n_cycles = n_cycles
        self.window = window
        self.delta_t = delta_t

    def get_value_at(self, t):
        """
        Returns the value of the signal at a specific time.

        :param float t: Time at which to evaluate the signal.

        :return: (float) Signal value at time t.
        """
        f = self.center_frequency
        n_cycles = self.n_cycles
        dt = self.delta_t

        length = n_cycles * (1 / f)
        y = math.cos(2 * math.pi * f * (t - dt))

        if self.window == 'rectangle':
            rectangle = 1 if (dt <= t <= length + dt) else 0
            return y * rectangle

        if self.window == 'hanning':
            hanning = math.sin(math.pi * (t - dt) / length) ** 2 if (dt <= t <= length + dt) else 0
            return y * hanning

        if self.window == 'hamming':
            hamming = 0.54 - 0.46 * math.cos(2*math.pi * (t - dt) / length) if (dt <= t <= length + dt) else 0
            return y * hamming

        if self.window == 'blackmann':
            alpha = 0.16
            a0 = (1-alpha)/2
            a1 = 1/2
            a2 = alpha/2
            blackmann = (a0 - a1 * math.cos(2*math.pi * (t - dt) / length) +
                         a2 * math.cos(4*math.pi * (t - dt) / length)) if (dt <= t <= length + dt) else 0
            return y * blackmann

        else:
            raise ValueError("Unsupported window type: {}".format(self.window))

    def get_duration(self):
        """
        Returns the duration for which the signal is non-zero.

        :return: (float) Signal duration.
        """
        return self.n_cycles * (1/self.center_frequency)


# DIRAC IMPULSE --------------------------------------------------------------------------------------------------------
class DiracImpulse(Signal):
    """
    Class representing a Dirac impulse signal.

    The discrete dirac impulse is 1 * ``magnitude`` for exactly one sample at ``t`` = 0 and 0 elsewhere.
    """

    def __init__(self, magnitude=1):
        """
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

