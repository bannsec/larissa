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
        for reg in self.state.ctx.getAllRegisters():
            setattr(self,reg.getName(),Reg(self.state, reg.getName()))

class Reg(PluginBase):
    """Abstract specific register"""

    def __init__(self, state, name):
        self.state = state
        self.name = name

    def __repr__(self):
        return "<Reg {0}>".format(self.name)

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

    @property
    def size(self):
        """Returns size (int) in bits of this register."""
        if self.state.project.loader.main_bin.arch == "x86":
            my_reg = triton.REG.X86
        elif self.state.project.loader.main_bin.arch == "x64":
            my_reg = triton.REG.X86_64
        else:
            logger.error("Unkown architecture for reg of {0}".format(self.state.project.loader.main_bin.arch))

        return int(
                self.state.ctx.Register(
                    getattr(my_reg,self.name.upper())
                    ).getBitSize())

import triton
