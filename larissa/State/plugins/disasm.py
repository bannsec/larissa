
from . import PluginBase

def is_int(s):
    """Silly function to check if string s represents an integer."""
    try:
        int(s,16)
        return True
    except:
        return False

class Disasm(PluginBase):
    """Plugin to handle disassembling instructions."""

    def __init__(self, state):

        # Save off the state
        self.state = state

    def pp(self, s):
        """Pretty prints the disassembly of the string/Byte/Bytes."""
        for i in self.disasm(s):
            # Add in helpful comments where possible
            comments = []

            # Fill in call target
            if i.mnemonic == "call" and is_int(i.op_str) and self.state.symbol(int(i.op_str,16)) != None:
                comments.append(self.state.symbol(int(i.op_str,16)).name)

            if comments == []:
                comments = ""
            else:
                comments = " ; " + ', '.join(comments)

            print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str + comments))

    def disasm(self, s):
        """Returns a disassembly module for the given input of type str/Byte/Bytes."""
        val = s

        if type(val) in [Byte, Bytes]:
            if not val.concrete:
                logger.warn("Bytes not entirely concrete. Selecting one possiblity to disassemble.")
            val = str(val)

        if type(val) is not str:
            logger.error("Unable to make string from type {0}".format(type(s)))
            return

        # Determine address of code
        address = s.address if hasattr(s,"address") else 0

        return self.context.disasm(val, address)


    @property
    def context(self):
        """Create a disassembly context for the current binary.
        Returns capstone disasm module."""

        # Set archecture.
        if self.state.project.loader.main_bin.arch in ["x86","x64"]:
            arch = capstone.CS_ARCH_X86
        else:
            logger.error("Unknown architecture {0}".format(self.state.project.main_bin.arch))
            return

        # Set mode
        if self.state.project.loader.main_bin.arch == "x64":
            mode = capstone.CS_MODE_64

        elif self.state.project.loader.main_bin.arch == "x86":
            mode = capstone.CS_MODE_32

        else:
            logger.error("Unknown mode for {0}".format(self.state.project.main_bin.arch))
            return

        # Instantiate and return the object
        return capstone.Cs(arch, mode)


import capstone
from .SolverEngine import Byte, Bytes
