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

    def set(self, value):
        """Set this register to a given value."""

        # TODO: Size check...

        # Symbolic not working yet
        if type(value) not in [int, long]:
            logger.error("Unsupported set type for register of {0}".format(type(value)))
            return

        # Concrete
        self.state.ctx.setConcreteRegisterValue(self.state.ctx.Register(getattr(self._triton_type, self.name.upper()),value))

    def __repr__(self):
        return "<Reg {0}>".format(self.name)

    def __int__(self):
        return int(self.bytes)

    def __hex__(self):
        return hex(self.bytes)

    def __str__(self):
        return str(self.bytes)

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
        return int(self._triton_class.getBitSize())

    @property
    def _triton_type(self):
        """Returns a triton type object for this object (i.e.: triton.REG.X86 or triton.REG.X86_64)"""
        if self.state.project.loader.main_bin.arch == "x86":
            return triton.REG.X86
        elif self.state.project.loader.main_bin.arch == "x64":
            return triton.REG.X86_64
        else:
            logger.error("Unkown architecture for reg of {0}".format(self.state.project.loader.main_bin.arch))

    @property
    def _triton_class(self):
        """Returns a triton register object for this register. (ctx.Register())"""
        return self.state.ctx.Register(getattr(self._triton_type, self.name.upper()))


    @property
    def bytes(self):
        """Return a bytes object representing this register."""
        me = self.state.ctx.buildSymbolicRegister(self._triton_class)

        if me.isSymbolized():
            logger.error("Not handling symbolic registers yet.")
            return

        # Concrete
        # TODO: This will fail for flags such as ZF
        return self.state.se.Bytes(length=self.size/8, value=me.evaluate())


import triton
