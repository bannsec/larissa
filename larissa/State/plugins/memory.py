import logging
logger = logging.getLogger("larissa.State.plugins.memory")

from . import PluginBase


class Memory(PluginBase):

    def __init__(self, state, *args, **kwargs):

        self.state = state

    def __getitem__(self, item):
        if type(item) in [int, long]:
            return self.state.se.Byte(item)

        elif type(item) is not slice:
            logger.error("Unknown getitem type for memory of {0}".format(type(item)))
            return

        if item.start is None:
            logger.error("Must specify starting address for memory.")
            return

        if item.stop is None:
            logger.error("Must specify stopping address for memory.")
            return

        if item.step is not None:
            logger.error("Not handling stride.")
            return

        return self.state.se.Bytes(address=item.start, length=item.stop - item.start)


