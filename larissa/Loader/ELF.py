import logging
logger = logging.getLogger("larissa.Loader.ELF")

from larissa.Loader import Loader

class ELF(Loader):
    """Abstract loading an ELF object."""

    def __init__(self, project):
        self.project = project

        self.file = open(self.project.filename,"rb")
        self.elffile = ELFFile(self.file)

        # Image Base
        try:
            self.address = next(seg for seg in self.segments if seg['p_type'] == "PT_LOAD")['p_vaddr']
        except StopIteration:
            self.address = None

        
    def initialize(self, state):
        """Return an init triton object for the relevant architecture."""

        # TODO: Triton works on a global state right now... Update this once Triton gives actual contexts to work with

        # TODO: Call this smartly basied on if it's ELF or PE

        arch = self.arch

        if arch == "x86":
            triton.setArchitecture(triton.ARCH.X86)

        elif arch == "x64":
            triton.setArchitecture(triton.ARCH.X86_64)

        else:
            raise Exception("How did i get here")

        # Define symbolic optimizations
        triton.enableMode(triton.MODE.ALIGNED_MEMORY, False) # TODO: Apparently True is faster? Makes memory access irritating though...
        triton.enableMode(triton.MODE.ONLY_ON_SYMBOLIZED, True)

        elf = triton.Elf(self.project.filename)
        
        #################
        # Load sections #
        #################

        # TODO: Incorporate map permissions
        # TODO: Integrate with page objects
        # TODO: Don't allow overlaps
        # TODO: Support loading at different address
        
        # Not all sections are loadable
        loadable_sections = [section for section in self.sections if section['sh_flags'] & 2]

        for section in loadable_sections:
            size   = section.header['sh_size']
            vaddr  = section.header['sh_addr']
            name   = section.name
            logger.debug('Loading 0x%08x - 0x%08x -- %s' %(vaddr, vaddr+size, name))
            triton.setConcreteMemoryAreaValue(vaddr, section.data())

        ###############
        # Relocations #
        ###############

        # Setup plt
        #for pltIndex in range(len(customRelocation)):
        #    customRelocation[pltIndex][2] = BASE_PLT + pltIndex

        # Perform our own relocations
        symbols = elf.getSymbolsTable()
        relocations = elf.getRelocationTable()
        for rel in relocations:
            symbolName = symbols[rel.getSymidx()].getName()
            symbolRelo = rel.getOffset()
            # TODO: Implement hooking...
            #
            #for crel in customRelocation:
            #    if symbolName == crel[0]:
            #        debug('Hooking %s' %(symbolName))
            #        setConcreteMemoryValue(MemoryAccess(symbolRelo, CPUSIZE.QWORD, crel[2]))
            #        break

        return elf
        

    def section(self, section):
        """Returns the section object for the given section name or number or None if not found."""

        if type(section) is str:
            return self.elffile.get_section_by_name(section)

        elif type(section) is int:
            return self.elffile.get_section(section)

        else:
            raise Exception("Unknown section type of {0}".format(type(section)))


    def dynamic_by_tag(self, tag):
        """dynamic_by_tag(tag) -> tag

        Arguments:
            tag(str): Named ``DT_XXX`` tag (e.g. ``'DT_STRTAB'``).

        Returns:
            :class:`elftools.elf.dynamic.DynamicTag`
        """
        dt      = None
        dynamic = self.elffile.get_section_by_name('.dynamic')

        if not dynamic:
            return None

        try:
            dt = next(t for t in dynamic.iter_tags() if tag == t.entry.d_tag)
        except StopIteration:
            pass

        return dt


    ##############
    # Properties #
    ##############

    @property
    def type(self):
        """Binary type (for example: "ET_EXEC")"""
        return self.elffile['e_type']

    @property
    def type_desc(self):
        """String description of the type of binary. i.e.: 'EXEC (Executable file)'"""
        return describe_e_type(self.type)

    @property
    def address(self):
        """The base address of this loaded elf."""
        return self.__address

    @address.setter
    def address(self, address):
        if type(address) not in [int, type(None)]:
            raise Exception("Invalid type for address of {0}".format(type(address)))

        self.__address = address
    
    @property
    def endianness(self):
        """Returns either 'little' or 'big'."""
        if self.elffile.little_endian:
            return "little"

        return "big"

    @property
    def elffile(self):
        """pyelftools elf file object."""
        return self.__elffile

    @elffile.setter
    def elffile(self, elffile):
        self.__elffile = elffile

    @property
    def segments(self):
        """Returns generator of segment information."""
        return self.elffile.iter_segments()

    @property
    def sections(self):
        """Returns generator of section information."""

        return self.elffile.iter_sections()

    @property
    def arch(self):
        """Returns the arch for this file. Either x86 or x64."""

        arch = self.elffile.get_machine_arch().lower()
        assert arch in ["x86","x64"]
        return arch

    @property
    def symbols(self):
        """Returns dictionary of symbols discovered in this binary."""

        # Caching results
        if hasattr(self,"_ELF__symbols"):
            return self.__symbols

        def symbol_resolve(self,symbol):
            # If this symbol is a section name, look it up
            if symbol['st_name'] == 0:

                # Skipping undefined symbols
                if type(symbol['st_shndx']) is str:
                    return None

                symsec = self.section(symbol['st_shndx'])
                return symsec.name

            else:
                return symbol.name
        
        symbols = {}

        # Populate the symbols themselves
        for section in self.elffile.iter_sections():

            # Only care about the Symbol Tables
            if type(section) is not SymbolTableSection:
                continue

            # Iterate through all discovered symbols
            for symbol in section.iter_symbols():

                symbol_name = symbol_resolve(self, symbol)

                # If lookup failed
                if symbol_name is None:
                    continue
                
                # Create a symbol object
                symbol_obj = Symbol()
                symbol_obj.name = symbol_name
                symbol_obj.elf = symbol
                symbol_obj.addr = symbol['st_value'] if symbol['st_value'] is not 0 else None

                # Add it to the dict
                symbols[symbol_name] = symbol_obj

        """
        # Iterate through relocations to give symbols addresses if possible
        for section in self.elffile.iter_sections():

            # Looking at relocations
            if type(section) is not RelocationSection:
                continue

            symtable = self.elffile.section(section['sh_link'])

            # Loop through this relocation section
            for rel in section.iter_relocations():

                # What's the symbol
                symbol = symtable.get_symbol(rel['r_info_sym'])

                # Resolve it
                symbol_name = symbol_resolve(self, symbol)

                # If lookup failed
                if symbol_name is None:
                    continue

                # Sanity check
                if symbols[symbol_name].addr is not None:
                    logger.info("Found symbol {2} already. Old = {0}, New = {1} ... Ignoring and leaving old in place.".format(symbols[symbol_name].addr, rel['r_offset'], symbol_name))
                    continue

                # Add known address
                symbols[symbol_name].addr = rel['r_offset']
        """
        
        # Cache our work
        self.__symbols = symbols

        return symbols
            


from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection
from elftools.elf.descriptions import describe_e_type
from larissa.Project import Project
from larissa.Loader.Symbol import Symbol
import triton

