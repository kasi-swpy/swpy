class All:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def __repr__(self):
        return f"All(header={self.header}, data={self.data})"
