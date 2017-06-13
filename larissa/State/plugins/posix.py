
from . import PluginBase

class Posix(PluginBase):
    """Abstracts posix stuff."""

    def __init__(self, state):

        # Save off the state
        self.state = state

        # Name->base dictionary for loaded libraries
        self.base_addrs = {}



