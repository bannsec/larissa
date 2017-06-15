import logging
logger = logging.getLogger("larissa.State.plugins.memory")

from . import PluginBase
from .SolverEngine import Byte, Bytes

class Memory(PluginBase):

    def __init__(self, state, *args, **kwargs):

        self.state = state
        self._page_size = 4096
        self.pages = Pages()

    def store(self, address, object):
        """Store object at memory address."""

        def _store_byte_concrete(self,b,address):
            """Stores byte assuming that it's concrete."""
            triton.setConcreteMemoryAreaValue(address,[b.value])

        def _store_byte_symbolic(self,b,address,ast=False):
            """Stores a byte assuming it is symbolic."""
            triton.assignSymbolicExpressionToMemory(
                    triton.newSymbolicExpression(b.value if not ast else b),
                    triton.MemoryAccess(address, 1)
                    )

        if type(object) is unicode:
            logger.warn("Input data as unicode. Converting it to string as ASCII.")
            object = object.encode('ascii')
        
        if type(object) is str:
            triton.setConcreteMemoryAreaValue(address, object)
            return

        if type(object) is Byte:
            if object.concrete:
                _store_byte_concrete(self, object, address)

            else:
                _store_byte_symbolic(self, object, address)

            return

        if type(object) is Bytes:
            for i, b in enumerate(object):
                if b.concrete:
                    _store_byte_concrete(self, b, address+i)

                else:
                    _store_byte_symbolic(self, b, address+i)

            return

        # TODO: Handle store of int (need to add optional size option)

        logger.error("Unhandled memory store type of {0}".format(type(object)))

    def __getitem__(self, item):
        if type(item) in [int, long]:
            return self.state.se.Byte(item)

        elif type(item) is not slice:
            logger.error("Unknown getitem type for memory of {0}".format(type(item)))
            return

        if item.start is None:
            logger.error("Must specify starting address for memory.")
            return

        if item.stop is None:
            logger.error("Must specify stopping address for memory.")
            return

        if item.step is not None:
            logger.error("Not handling stride.")
            return

        return self.state.se.Bytes(address=item.start, length=item.stop - item.start)

    def __setitem__(self, key, value):
        if type(key) not in [int, long]:
            logger.error("Unhandled key type of {0}".format(type(key)))
            return

        self.store(key, value)

    ############
    # Property #
    ############

    @property
    def pages(self):
        """Dictionary of page objects. Dictionary index is the page. For instance, page 6 would be memory.page[5]."""
        return self.__pages

    @pages.setter
    def pages(self, pages):
        if type(pages) is not Pages:
            logger.error("Invalid type for pages of {0}".format(type(pages)))
            return

        self.__pages = pages

    @property
    def map(self):
        """Prints a string representation of the memory map of this state."""

        def roundup(x,base=4096):
            return x if x % base == 0 else x + base - x % base

        # Setup the table
        table = prettytable.PrettyTable(["Start","End","Prot","File"])
        table.align = 'l'
        table.border = False
        
        for name, base in sorted(self.state.posix.base_addrs.items(), key=operator.itemgetter(1)):
            # Grab the object
            obj = self.state.project.loader._lookup_obj_by_name(name)

            # Loop through the segments
            for seg in self.state.project.loader.main_bin.segments:
                if seg['p_type'] != "PT_LOAD":
                    continue

                map_base = base
                start = map_base + seg['p_vaddr']
                end = start + seg['p_memsz']

                table.add_row([hex(start), hex(end), self[start].page.prot_str, obj.filename])

        print(str(table))


class Pages(object):
    """Silly abstraction for pages to allow pages to be created on the fly."""
    def __init__(self):
        self.pages = {}

    def __getitem__(self, item):
        if type(item) not in [int, long]:
            logger.error("Not handling this getter of {0}".format(type(item)))
            return

        # Create new page on the fly
        if item not in self.pages:
            # Default to zero prot and unmapped
            p = Page(prot=0, mapped=False)
            self.pages[item] = p

        return self.pages[item]

    def __setitem__(self,key,value):
        # Just passing through for now
        self.pages[key] = value

    def __len__(self):
        return len(self.pages)

    def __iter__(self):
        return self.pages.__iter__()

    def __repr__(self):
        return "<Pages {0}>".format(len(self.pages))

class Page(object):
    """Simple object abstracting a memory page."""
    
    PROT_READ  = 0x1
    PROT_WRITE = 0x2
    PROT_EXEC  = 0x4
    PROT_NONE  = 0x0

    def __init__(self, prot, mapped=False):
        """prot = int protection for this memory page (0-7)
        mapped = bool, is this page mapped?
        """
        self.prot = prot
        self.mapped = mapped

    def __repr__(self):
        return "<Page permissions={0} mapped={1}>".format(self.prot_str,self.mapped)

    @property
    def prot_str(self):
        """String representation of the protection for this page."""
        prot = ""
        if self.read:
            prot += "r"
        else:
            prot += "-"
        if self.write:
            prot += "w"
        else:
            prot += "-"
        if self.execute:
            prot += "x"
        else:
            prot += "-"
        return prot

    @property
    def read(self):
        """Boolean does page have read permission."""
        return self.prot & self.PROT_READ > 0

    @read.setter
    def read(self, read):
        if type(read) is not bool:
            logger.error("Invalid type for read of {0}".format(type(read)))
            return

        if read:
            self.prot = self.prot | self.PROT_READ
        else:
            self.prot = self.prot ^ (self.prot & self.PROT_READ)

    @property
    def write(self):
        """Boolean does page have write permission."""
        return self.prot & self.PROT_WRITE > 0

    @write.setter
    def write(self, write):
        if type(write) is not bool:
            logger.error("Invalid type for write of {0}".format(type(write)))
            return

        if write:
            self.prot = self.prot | self.PROT_WRITE
        else:
            self.prot = self.prot ^ (self.prot & self.PROT_WRITE)

    @property
    def execute(self):
        """Boolean does page have execute permission."""
        return self.prot & self.PROT_EXEC > 0

    @execute.setter
    def execute(self, execute):
        if type(execute) is not bool:
            logger.error("Invalid type for execute of {0}".format(type(execute)))
            return

        if execute:
            self.prot = self.prot | self.PROT_EXEC
        else:
            self.prot = self.prot ^ (self.prot & self.PROT_EXEC)

    @property
    def prot(self):
        """Protection (int)."""
        return self.__prot

    @prot.setter
    def prot(self, prot):
        if type(prot) not in [int, long]:
            logger.error("Invalid type for prot of {0}".format(type(prot)))
            return

        if prot > 7 or prot < 0:
            logger.error("Invalid prot value of {0}".format(prot))
            return

        self.__prot = int(prot)

    @property
    def mapped(self):
        """Is this page file mapped?"""
        return self.__mapped

    @mapped.setter
    def mapped(self, mapped):
        if type(mapped) is not bool:
            logger.error("Invalid mapped type of {0}".format(type(mapped)))
            return

        self.__mapped = mapped

import triton
import prettytable
import operator
