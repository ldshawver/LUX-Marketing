from utils import safe_count


class DummyQuery:
    def __init__(self, value=None, raise_error=False):
        self.value = value
        self.raise_error = raise_error

    def count(self):
        if self.raise_error:
            raise RuntimeError("boom")
        return self.value


def test_safe_count_returns_value():
    query = DummyQuery(value=7)
    assert safe_count(query, fallback=0) == 7


def test_safe_count_falls_back_on_error():
    query = DummyQuery(raise_error=True)
    assert safe_count(query, fallback=3, context="test") == 3
