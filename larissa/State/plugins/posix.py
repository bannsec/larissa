
from . import PluginBase

class Posix(PluginBase):
    """Abstracts posix stuff."""

    def __init__(self, state):

        # Save off the state
        self.state = state



