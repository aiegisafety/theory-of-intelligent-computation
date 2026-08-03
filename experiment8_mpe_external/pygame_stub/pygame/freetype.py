"""Font stub — rendering only (see pygame/__init__.py for rationale)."""


class Font:
    def __init__(self, *a, **k):
        pass

    def render_to(self, *a, **k):
        pass

    def render(self, *a, **k):
        return None, None


def init(*a, **k):
    pass


def get_default_font():
    return "stub"
