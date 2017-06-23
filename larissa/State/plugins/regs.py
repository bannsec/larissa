import logging
logger = logging.getLogger("larissa.State.plugin.Regs")
from . import PluginBase

class Regs(PluginBase):
    """Interacting with registers"""

    def __init__(self, state):

        # Save off the state
        self.state = state

        self._init_registers()

    def _init_registers(self):
        for reg in triton.getAllRegisters():
            setattr(self,reg.getName(),Reg(self.state, reg.getName()))

class Reg(PluginBase):
    """Abstract specific register"""

    def __init__(self, state, name):
        self.state = state
        self.name = name

    @property
    def name(self):
        """String representation of this register's name."""
        return self.__name

    @name.setter
    def name(self, name):
        if type(name) is not str:
            logger.error("Bad register name type of {0}".format(type(name)))
            return

        self.__name = name 

import triton
