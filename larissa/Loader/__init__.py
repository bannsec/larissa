
class Loader(object):

    def __init__(self, project):
        self.project = project

    def initialize(self):
        """Return an init triton object for the relevant architecture."""

        # TODO: Call this smartly basied on if it's ELF or PE

        arch = self.arch

        if arch == "x86":
            setArchitecture(ARCH.X86)

        elif arch == "x64":
            setArchitecture(ARCH.X86_64)

        else:
            raise Exception("How did i get here")

        # Define symbolic optimizations
        enableMode(MODE.ALIGNED_MEMORY, True)
        enableMode(MODE.ONLY_ON_SYMBOLIZED, True)

        elf = Elf(self.project.filename)
        
        #################
        # Load sections #
        #################

        raw = elf.getRaw()
        phdrs = elf.getProgramHeaders()
        for phdr in phdrs:
            offset = phdr.getOffset()
            size   = phdr.getFilesz()
            vaddr  = phdr.getVaddr()
            #debug('Loading 0x%06x - 0x%06x' %(vaddr, vaddr+size))
            setConcreteMemoryAreaValue(vaddr, raw[offset:offset+size])

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
        

    ##############
    # Properties #
    ##############

    @property
    def arch(self):
        """Returns the arch for this file. Either x86 or x64."""
        with open(self.project.filename,"rb") as f:
            elffile = ELFFile(f)
            arch = elffile.get_machine_arch().lower()
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


from elftools.elf.elffile import ELFFile
from larissa.Project import Project
from .ELF import ELF
from triton import *
