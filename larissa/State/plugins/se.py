
from .SolverEngine import SolverEngine

class Se(SolverEngine):
    """Shim to get submodule"""

    def __init__(self, *args, **kwargs):
        # Just toss it up
        super(type(self), self).__init__(*args, **kwargs)
