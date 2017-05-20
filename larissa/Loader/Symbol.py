class Symbol(object):
    """Simple class to abstract a binary symbol."""

    def __init__(self):
        self.name = None
        self.addr = None

    def __repr__(self):
        return "<Symbol name={0}>".format(self.name)

    ##############
    # Properties #
    ##############

    @property
    def source(self):
        """String reprenstation of file name that this symbol is from. For instance "libc.so.6"."""
        return self.__source

    @source.setter
    def source(self, source):
        if type(source) not in [str, unicode]:
            raise Exception("Invalid type for source of {0}".format(type(source)))

        self.__source = source

    @property
    def name(self):
        """Unicode representation of the symbol's name."""
        return self.__name

    @name.setter
    def name(self, name):
        if type(name) not in [unicode, type(None)]:
            raise Exception("Invalid type for name of {0}".format(type(name)))

        self.__name = name

    @property
    def addr(self):
        """Address (int) of this symbol in the binary"""
        return self.__addr

    @addr.setter
    def addr(self, addr):
        if type(addr) not in [type(None), int]:
            raise Exception("Invalid type for addr of {0}".format(type(addr)))

        self.__addr = addr
