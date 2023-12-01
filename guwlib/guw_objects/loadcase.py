class LoadCase:
    def __init__(self, name, duration, transducer_signals, output_request='history'):
        self.name = name
        self.duration = duration
        self.transducer_signals = transducer_signals
        self.output_request = output_request
