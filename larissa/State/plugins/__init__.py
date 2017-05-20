
class PluginBase(object):
    """Expose base functionality for all plugins."""

    ##############
    # Properties #
    ##############

    @property
    def state(self):
        """Current state object to track."""
        return self.__state

    @state.setter
    def state(self, state):
        if type(state) is not State:
            raise Exception("Invalid type for state of {0}".format(type(state)))

        self.__state = state

from .. import State
