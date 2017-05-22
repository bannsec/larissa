from .. import PluginBase

class SolverEngine(PluginBase):

    def __init__(self, state, *args, **kwargs):

        self.state = state

    def __repr__(self):
        return "<SolverEngine>"

    ##############
    # Properties #
    ##############

