"""Ensure shared state across all instances of a class
"""

# Alex Martelli's 'Borg': http://www.aleax.it/Python/5ep.html


class Borg:
    _shared_state = {}
    _exists = False
    def __init__(self):
        if not self._exists:
            self.__dict__ = self._shared_state
            self._exists = True
        else:
            raise AttributeError("Another instance of this Borg already exists, skip initialisation")