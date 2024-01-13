class LoadCase:
    """
    Container for loading data / transducer excitation signals.

    Each load case represents one independent ABAQUS simulation. Multiple load cases can be defined for one GUWlib
    model. A ``LoadCase`` instance contains the excitation signals applied to each transducer.
    """
    def __init__(self, name, duration, transducer_signals, output_request='history'):
        """
        :param str name: Name of this load case.
        :param float duration: Total ABAQUS simulation duration for this load case.
        :param list[Signal, None] transducer_signals: A list, containing the excitation signal for each transducer, in
            the same order as the transducers in ``FEModel.transducers``. The length of this list must be equal to the
            number of transducers used in the model, i.e. ``len(LoadCase.transducer_signals)`` !=
            ``len(FEModel.transducers)``. If a transducer is not excited in this load case, set the corresponding list
            item to ``None``.
        :param str output_request: The output to be requested in ABAQUS for this load case. If set to
            ``history``, history output is requested for all transducer signals. If set to ``field``, an additional
            field output is requested for the nodes contained in the  plates' field output set (i.e. the plates top
            surface) in time intervals of 10 * ``FEModel.get_max_time_increment()``.

        :ivar str name: Name of this load case.
        :ivar float duration: Total ABAQUS simulation duration for this load case.
        :ivar list[Signal] transducer_signals: A list, containing the excitation signal for each transducer.
        :ivar str output_request: The output to be requested in ABAQUS for this load case.
        """
        self.name = name
        self.duration = duration
        self.transducer_signals = transducer_signals
        self.output_request = output_request

        valid_output_requests = ['history', 'field']
        if output_request not in valid_output_requests:
            raise ValueError("Invalid value for output_request. "
                             "Accepted values are: {}".format(valid_output_requests))

