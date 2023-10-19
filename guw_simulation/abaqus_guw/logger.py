import sys


class OutputToFile:
    def __init__(self, filename):
        self.filename = filename
        self.original_stdout = sys.stdout

    def __enter__(self):
        self.file = open('{}.txt'.format(self.filename), 'w')
        sys.stdout = self.file

    def __exit__(self, *args):
        sys.stdout = self.original_stdout
        self.file.close()
