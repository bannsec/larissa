
from . import PluginBase

class Libc(PluginBase):
    """Abstracts libc stuff."""

    def __init__(self, state):

        # Save off the state
        self.state = state

        # TODO: Change this based on arch?
        self.mmap_base = 0xf7000000


