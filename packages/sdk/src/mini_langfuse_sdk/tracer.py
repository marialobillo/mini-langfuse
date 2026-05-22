

class InMemoryTracer:
    def __init__(self):
        self.records = []

    def capture(self, record):
        self.records.append(record)


default_tracer = InMemoryTracer()