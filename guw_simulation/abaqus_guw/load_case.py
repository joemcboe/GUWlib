class LoadCase:
    def __init__(self, name, duration, piezo_signals, output_request='history'):
        self.name = name
        self.duration = duration
        self.piezo_signals = piezo_signals
        self.output_request = output_request
