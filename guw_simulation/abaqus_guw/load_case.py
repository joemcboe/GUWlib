class LoadCase:
    def __init__(self, name, propagation_distance, piezo_signals, output_request='history'):
        self.name = name
        self.propagation_distance = propagation_distance
        self.piezo_signals = piezo_signals
        self.output_request = output_request
