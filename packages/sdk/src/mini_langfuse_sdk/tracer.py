from typing import Any


class InMemoryTracer:
    records: list[dict[str, Any]]

    def __init__(self) -> None:
        self.records = []

    def capture(self, record: dict[str, Any]) -> None:
        self.records.append(record)


default_tracer = InMemoryTracer()