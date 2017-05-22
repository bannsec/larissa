import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine.Byte")

class Byte(object):
    
    def __init__(self, state, address=None, *args, **kwargs):

        self.state = state

        self.value = None

        # If address is passed, grab it from triton
        self.address = address

    def _load_from_memory(self):
        """Look at the current stored address and attempt to load it into this object."""
        if self.address is None:
            logger.error("Attempting to load address of None.")
            return

        # Check if this is a symbolic value or not
        if self.address in triton.getSymbolicMemory():
            # TODO: Not clear yet what i should be storing... AST? FullAST? Expression? Variable?
            # Storing Full Ast For Now
            self.value = triton.getFullAst(triton.getSymbolicMemory()[self.address].getAst())

        else:
            # Concrete memory
            self.value = triton.getConcreteMemoryValue(triton.MemoryAccess(self.address,1))

    def __repr__(self):
        attribs = ["Byte"]

        if self.value is not None:
            attribs.append("value={0}".format(self.value))

        return "<{0}>".format(" ".join(attrib for attrib in attribs))

    def __str__(self):

        # No value?
        if self.value is None:
            logger.error("No value to make into str.")
            return ""

        # Symbolic
        if not self.concrete:
            logger.error("Cannot handle symbolic byte yet. Attempting to resolve anyway...")
            # TODO: Secretly try to evaluate anyway. Not sure if this is correct functionality atm.
            # TODO: This likely won't take some constraints into consideration....
            #       Likely want to switch this for a state.se.any_str type call once i have that figured out.
            return chr(self.value.evaluate())

        # Concrete
        return chr(self.value)

    ##############
    # Properties #
    ##############

    @property
    def concrete(self):
        """Boolean indicating if the value of this byte is concrete as opposed to symbolic."""
        return type(self.value) in [int, long]

    @property
    def value(self):
        """Returns the value. If this is concrete, it will be an integer. If it is symbolic, it will be an ast."""
        return self.__value

    @value.setter
    def value(self, value):
        if type(value) not in [int, long, type(None), Ast]:
            logger.error("Unhandled Byte value of type {0}".format(type(value)))
            return

        self.__value = value

    @property
    def state(self):
        """Current state object to track."""
        return self.__state

    @state.setter
    def state(self, state):
        if type(state) is not State:
            raise Exception("Invalid type for state of {0}".format(type(state)))

        self.__state = state

    @property
    def address(self):
        """Address of this byte in memory. None if it is not in memory."""
        return self.__address

    @address.setter
    def address(self, address):
        if type(address) not in [int, type(None)]:
            logger.error("Invalid type for address of {0}".format(type(address)))
            return

        # Save off the address
        self.__address = address

        # If it's not None, load it up
        if address is not None:
            self._load_from_memory()

from larissa.State import State
import triton

# Hack.. Not sure where Ast type is directly defined.
Ast = type(triton.ast.bv(1,1))
