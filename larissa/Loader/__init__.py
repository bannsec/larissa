import logging
logger = logging.getLogger("Loader")

class Loader(object):

    def __init__(self, project):
        self.project = project

        self.file = open(self.project.filename,"rb")
        self.elffile = ELFFile(self.file)


    def initialize(self, state):
        """Return an init triton object for the relevant architecture."""

        # TODO: Triton works on a global state right now... Update this once Triton gives actual contexts to work with

        # TODO: Call this smartly basied on if it's ELF or PE

        arch = self.arch

        if arch == "x86":
            setArchitecture(ARCH.X86)

        elif arch == "x64":
            setArchitecture(ARCH.X86_64)

        else:
            raise Exception("How did i get here")

        # Define symbolic optimizations
        enableMode(MODE.ALIGNED_MEMORY, False) # TODO: Apparently True is faster? Makes memory access irritating though...
        enableMode(MODE.ONLY_ON_SYMBOLIZED, True)

        elf = Elf(self.project.filename)
        
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
            setConcreteMemoryAreaValue(vaddr, section.data())

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
        

    def get_section(self, section):
        """Returns the section object for the given section name or number or None if not found."""

        if type(section) is str:
            return self.elffile.get_section_by_name(section)

        elif type(section) is int:
            return self.elffile.get_section(section)

        else:
            raise Exception("Unknown section type of {0}".format(type(section)))


    ##############
    # Properties #
    ##############

    @property
    def elffile(self):
        """pyelftools elf file object."""
        return self.__elffile

    @elffile.setter
    def elffile(self, elffile):
        self.__elffile = elffile

    @property
    def arch(self):
        """Returns the arch for this file. Either x86 or x64."""

        arch = self.elffile.get_machine_arch().lower()
        assert arch in ["x86","x64"]
        return arch

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        if type(project) is not Project:
            raise Exception("Invalid project of type {0}".format(type(project)))

        self.__project = project

    @property
    def file(self):
        """Python file object for the binary opened in read-only mode."""
        return self.__file

    @file.setter
    def file(self, f):
        if type(f) is not file:
            raise Exception("Invalid file property of type {0}".format(type(f)))

        self.__file = f

    @property
    def sections(self):
        """Returns generator of section information."""

        return self.elffile.iter_sections()


from elftools.elf.elffile import ELFFile
from larissa.Project import Project
from .ELF import ELF
from triton import *
