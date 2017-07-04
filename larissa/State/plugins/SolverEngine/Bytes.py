import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine.Bytes")

def roundup(x,base=4096):
    return x if x % base == 0 else x + base - x % base

class Bytes(object):

    def __init__(self, state, address=None, length=1, symbolic = False, value = None, *args, **kwargs):
        """
        address = address to read bytes from (optional)
        length = number of bytes to read
        symbolic = Should it be symbolic? (exclusive from address)
        value = (optional) int value to store in this bytes object.
        """

        self.state = state

        # Actual list of loaded bytes
        self.bytes = []

        # These two are mutually exclusive for now
        if address != None and symbolic:
            logger.error("Cannot specify both address and symbolic for now.")
            return

        if address != None and value != None:
            logger.error("Cannot specify both address to load from and value.")
            return

        # Infer size of value if object is ast
        if type(value) is ast_type(self.state):
            length = roundup(value.getBitvectorSize(),base=8) / 8
            symbolic = True

        self.length = length
        self.address = address

        # If we're creating a blank symbolic Bytes object
        if symbolic and value == None:
            for _ in xrange(length):
                # Just keep adding
                self.bytes.append(self.state.se.Byte(symbolic=True))

        # If we're create a symbolic var with existing value
        elif symbolic and value != None:
            self._store_value_symbolic(value)

        elif value != None:
            self._store_value(value)

    def _store_value_symbolic(self, value):
        """Takes value (of type triton ast), break it apart and store as a larissa Bytes object."""

        # Type checks
        if type(value) not in [ast_type(self.state)]:
            logger.error("Bad symbolic value type of {0}".format(type(value)))
            return

        # Length check
        if self.length != (roundup(value.getBitvectorSize(),8) / 8):
            logger.error("Length mismatch. Stated length is {0} but discovered length is {1}".format(self.length, value.getBitvectorSize() / 8))
            return

        # Grab a temporary ast context
        ast = self.state.ctx.getAstContext()

        # TODO: This doesn't account for Big Endian
        # Loop through each byte, extract, and create a Byte object for it.
        for i in range(0,self.length):
            top = (i*8)+7
            bottom = i*8

            # Adjust if we don't have a full byte here
            if top > value.getBitvectorSize():
                top = value.getBitvectorSize() - 1

            self.bytes.append(
                self.state.se.Byte(symbolic=True, value=ast.extract(top,bottom,value))
            )


    def _store_value(self, value):
        if type(value) not in [int, long]:
            logger.error("Invalid Bytes value type of {0}".format(type(value)))
            return

        # Int
        bits = len(bin(value)[2:].strip("L"))
        if bits > self.length*8:
            logger.error("Attempting to store value {0} into bytes object of max size {1}".format(hex(value), hex(2**(self.length*8)-1)))
            return

        # TODO: This probably won't work right on Big Endian.
        for _ in xrange(self.length):
            self.bytes.append(self.state.se.Byte(value=value & 0xff))
            value = value >> 8

    def _load_from_memory(self):
        """Loads up our bytes."""

        # Heavy lifting is done at the Byte object here
        # TODO: This probably won't work right on Big Endian.
        for address in xrange(self.address, self.address+self.length):
            self.bytes.append(self.state.se.Byte(address))

    def __repr__(self):
        attribs = ["Bytes"]

        if self.symbolic:
            attribs.append("Symbolic")

        if self.address is not None:
            attribs.append("address={0}".format(hex(self.address)))

        if self.length > 0:
            attribs.append("length={0}".format(self.length))

        return "<{0}>".format(' '.join(attribs))

    def __iter__(self):
        # Iterate over our bytes
        return self.bytes.__iter__()

    def __getitem__(self,item):
        # TODO: Maybe return index slice as a Bytes object?

        # Pass through to list object
        return self.bytes[item]

    def __str__(self):
        """Return string representation of bytes object. If any bytes are symbolic, a single possibility will be returned for that byte."""
        return self.state.se.any_str(self)

    def __len__(self):
        return len(self.bytes)

    def __int__(self):

        # If we're not entirely concrete
        if not self.concrete:
            return self.state.se.any_int(self)

        # If we are entirely concrete, just calculate and return

        # Correct for architecture endianness
        if self.state.project.loader.main_bin.endianness != 'little':
            bytes = reversed(self)
        else:
            bytes = self

        out = 0

        for i, byte in enumerate(bytes):
            out += int(byte) << (8 * i)

        return out

    def __hex__(self):
        return hex(int(self))

    def pp(self):
        """Pretty prints this bytes object as assembly instructions."""
        self.state.disasm.pp(self)

    def disasm(self):
        """Return disassembly generator."""
        return self.state.disasm.disasm(self)

    ##############
    # Properties #
    ##############

    @property
    def symbolic(self):
        return not self.concrete

    @property
    def concrete(self):
        """Return true if every Byte in this Bytes object is concrete."""
        # The converse can sometimes be the faster question
        return not any(not byte.concrete for byte in self)

    @property
    def bytes(self):
        """The actual list of bytes loaded in this object."""
        return self.__bytes

    @bytes.setter
    def bytes(self, bytes):
        if type(bytes) is not list:
            logger.error("Invalid type for bytes of {0}".format(type(bytes)))
            return

        self.__bytes = bytes

    @property
    def length(self):
        """How many bytes long is this Bytes object?"""
        return self.__length

    @length.setter
    def length(self, length):
        if type(length) not in [type(None), int, long]:
            logger.error("Invalid type for length of {0}".format(type(length)))
            return

        self.__length = length

    @property
    def address(self):
        """Address of this byte in memory. None if it is not in memory."""
        return self.__address

    @address.setter
    def address(self, address):
        if type(address) not in [int, long, type(None)]:
            logger.error("Invalid type for address of {0}".format(type(address)))
            return

        # Save off the address
        self.__address = address

        # If it's not None, load it up
        if address is not None:
            self._load_from_memory()


    @property
    def state(self):
        """Current state object to track."""
        return self.__state

    @state.setter
    def state(self, state):
        if type(state) is not State:
            raise Exception("Invalid type for state of {0}".format(type(state)))

        self.__state = state

ast_type = lambda state: type(state.ctx.getAstContext().bv(1,1))
from larissa.State import State
import triton
