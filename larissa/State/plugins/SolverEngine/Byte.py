import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine.Byte")

class Byte(object):
    
    def __init__(self, state, address=None, symbolic=False, value = None, *args, **kwargs):
        """
        state = larissa.State object of current state.
        address = Optional address to load from.
        symbolic = Should this byte be symbolic.
        """
        self.state = state

        # Value type check
        if type(value) not in [int, long, type(None), type(state.ctx.getAstContext().bv(1,1))]:
            logger.error("Invalid value type of {0}.".format(type(value)))
            return

        # These two are mutually exclusive for now
        if address != None and symbolic:
            logger.error("Cannot specify both address and symbolic for now.")
            return

        # These two are mutually exclusive
        if address != None and value != None:
            logger.error("Cannot specify both address and value for now.")
            return

        # Concrete size check
        if value != None and not symbolic and value > 0xff:
            logger.error("Value too large to fit in Byte.")
            return

        # Symbolic size check
        if value != None and symbolic:
            # Zero extend if under a byte
            # TODO: How to know when to sign extend?
            if value.getBitvectorSize() < 8:
                ast = state.ctx.getAstContext()

                # This isn't really tested... Maybe it works tho?
                if not value.isSigned():
                    value = ast.zx( 8 - value.getBitvectorSize(), value)
                else:
                    value = ast.sx( 8 - value.getBitvectorSize(), value)
        
            if value.getBitvectorSize() != 8:
                logger.error("Symbolic value incorrect size for Byte. Got {0} expected 8".format(value.getBitvectorSize()))
                return

        self.value = value

        # If address is passed, grab it from triton
        self.address = address

        if symbolic and self.value == None:
            # Whip up a new variable byte
            self.value = self.state.ctx.getAstContext().variable(self.state.ctx.newSymbolicVariable(8))

    def pp(self):
        """Pretty prints this bytes object as assembly instructions."""
        self.state.disasm.pp(self)

    def disasm(self):
        """Return disassembly generator."""
        return self.state.disasm.disasm(self)

    def _load_from_memory(self):
        """Look at the current stored address and attempt to load it into this object."""
        if self.address is None:
            logger.error("Attempting to load address of None.")
            return

        # Check if this is a symbolic value or not
        if self.address in self.state.ctx.getSymbolicMemory():
            # TODO: Not clear yet what i should be storing... AST? FullAST? Expression? Variable?
            # Storing Full Ast For Now
            self.value = self.state.ctx.getFullAst(self.state.ctx.getSymbolicMemory()[self.address].getAst())

        else:
            # Concrete memory
            self.value = self.state.ctx.getConcreteMemoryValue(triton.MemoryAccess(self.address,1))

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


        return self.state.se.any_str(self)

    def __int__(self):
        # No value?
        if self.value is None:
            logger.error("No value to make into int.")
            return -1

        # Concrete
        if self.concrete:
            return self.value

        # Symbolic
        return self.state.se.any_int(self)

    def __hex__(self):
        return hex(int(self))

    def __len__(self):
        return 1
        

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
        if type(value) not in [int, long, type(None), type(self.state.ctx.getAstContext().bv(1,1))]:
            logger.error("Unhandled Byte value of type {0}".format(type(value)))
            return

        if type(value) is type(self.state.ctx.getAstContext().bv(1,1)):
            # Attempt simplifcation TODO: Do this somewhere else?
            try:
                value = self.state.ctx.simplify(value,True)
            except:
                pass

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

    @property
    def page(self):
        """Returns the corresponding page element for this Byte object."""
        if self.address == None:
            logger.error("This Byte is not from an address.")
            return None

        page_number = self.address / self.state.memory._page_size
        return self.state.memory.pages[page_number]

from larissa.State import State
import triton
