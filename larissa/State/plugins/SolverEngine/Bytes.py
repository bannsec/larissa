import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine.Bytes")

class Bytes(object):

    def __init__(self, state, address=None, length=1, symbolic = False, *args, **kwargs):
        """
        address = address to read bytes from (optional)
        length = number of bytes to read
        symbolic = Should it be symbolic? (exclusive from address)
        """

        self.state = state

        # Actual list of loaded bytes
        self.bytes = []

        # These two are mutually exclusive for now
        if address and symbolic:
            logger.error("Cannot specify both address and symbolic for now.")
            return

        self.length = length
        self.address = address

        if symbolic:
            for _ in xrange(length):
                # Just keep adding
                self.bytes.append(self.state.se.Byte(symbolic=True))


    def _load_from_memory(self):
        """Loads up our bytes."""

        # Heavy lifting is done at the Byte object here
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
        if type(address) not in [int, type(None)]:
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

from larissa.State import State
import triton
