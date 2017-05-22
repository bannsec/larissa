from .. import PluginBase

class SolverEngine(PluginBase):

    def __init__(self, state, *args, **kwargs):

        self.state = state

    def Byte(self, *args, **kwargs):
        """Instantiate a Byte object for the current state."""
        return Byte(self.state, *args, **kwargs)

    def Bytes(self, *args, **kwargs):
        """Instantiate a Bytes object for the current state."""
        return Bytes(self.state, *args, **kwargs)

    def __repr__(self):
        return "<SolverEngine>"

    ##############
    # Properties #
    ##############

from .Byte import Byte
from .Bytes import Bytes
