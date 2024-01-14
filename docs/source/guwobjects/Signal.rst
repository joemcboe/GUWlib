Signal
=======

``Signal``
-----------

.. toggle::

    .. autoclass:: guwlib.guw_objects.Signal

        **Methods:**

        .. automethod:: guwlib.guw_objects.Signal.get_value_at
        .. automethod:: guwlib.guw_objects.Signal.get_duration

----------------------------------------------------------

``Burst``
----------
.. autoclass:: guwlib.guw_objects.Burst
    :show-inheritance:

    **Figures:**

    .. svgoverlay:: _static/signal_burst.svg
        :path: ..
        :width: 100%
        :font-size: 0.70em

    *4-cycle Burst signal with Hanning window, left: time domain, right: FFT*

..
    **Methods:**

    .. automethod:: guwlib.guw_objects.Burst.get_value_at
    .. automethod:: guwlib.guw_objects.Burst.get_duration



-----------------------------------------------------------

``DiracImpulse``
-----------------

.. autoclass:: guwlib.guw_objects.DiracImpulse
    :show-inheritance:

    **Figures:**

    .. svgoverlay:: _static/signal_impulse.svg
        :path: ..
        :width: 100%
        :font-size: 0.70em

    *Dirac impulse and its FFT (maximum frequency will depend on the sampling rate)*

..
    **Methods:**

    .. automethod:: guwlib.guw_objects.DiracImpulse.get_value_at
    .. automethod:: guwlib.guw_objects.DiracImpulse.get_duration





