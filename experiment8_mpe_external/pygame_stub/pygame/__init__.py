"""Minimal pygame stub — RENDERING ONLY.

Why this exists: mpe2's SimpleEnv.__init__ constructs a drawing surface and a
font even when the environment is never rendered, so `import pygame` is required
to instantiate the environment at all.  The full pygame wheel is ~13 MB and the
sandbox's throughput (~15 KB/s) makes that impractical.

WHAT IS STUBBED: only the display surface and font objects.
WHAT IS NOT TOUCHED: the physics integrator, the reward function, the
observation function, and the action semantics -- i.e. everything that
determines the data we analyse -- all run as the unmodified mpe2 package.

Calling render() will not produce images; we never call it.
"""


class _Surface:
    def __init__(self, size=(1, 1)):
        self._size = tuple(size)

    def get_size(self):
        return self._size

    def fill(self, *a, **k):
        pass


def Surface(size, *a, **k):
    return _Surface(size)


def init(*a, **k):
    return (0, 0)


def quit(*a, **k):
    pass


class _Draw:
    @staticmethod
    def circle(*a, **k):
        pass

    @staticmethod
    def line(*a, **k):
        pass


draw = _Draw()


class _Display:
    @staticmethod
    def set_mode(size, *a, **k):
        return _Surface(size)

    @staticmethod
    def flip(*a, **k):
        pass

    @staticmethod
    def set_caption(*a, **k):
        pass


display = _Display()


class _Event:
    @staticmethod
    def pump(*a, **k):
        pass

    @staticmethod
    def get(*a, **k):
        return []


event = _Event()


class _Clock:
    def tick(self, *a, **k):
        return 0


class _Time:
    Clock = _Clock

    @staticmethod
    def get_ticks():
        return 0


time = _Time()


class _Surfarray:
    @staticmethod
    def pixels3d(surf):
        import numpy as np
        w, h = surf.get_size()
        return np.zeros((int(w), int(h), 3), dtype=np.uint8)


surfarray = _Surfarray()
