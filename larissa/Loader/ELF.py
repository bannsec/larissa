import logging
logger = logging.getLogger("larissa.Loader.ELF")

from larissa.Loader import Loader

class ELF(Loader):
    """Abstract loading an ELF object."""

    def __init__(self, project, filename=None):
        """
        project = larissa.Project
        filename = string path to file to load (default: filename of the loaded project
        main_bin = bool, is this the main binary
        """

        self.project = project
        self.main_bin = False # This will get set by the base loader

        self.filename = filename or self.project.filename
        self.file = open(self.filename,"rb")
        self.elffile = ELFFile(self.file)

        # Image Base
        try:
            self.address = next(seg for seg in self.segments if seg['p_type'] == "PT_LOAD")['p_vaddr']
        except StopIteration:
            self.address = None

    def _find_good_load_addr(self, segment, state):
        """Find a good load address for the given segment."""

        # TODO: Check that the requested base is not already taken.
        # Non-PIE load address
        if self.address != 0:
            if segment['p_vaddr'] != 0:
                return segment['p_vaddr']
            else:
                raise Exception("Not sure how this happened. Our base address != 0 but the segment p_vaddr == 0?")

        ###################################
        # This binary is PIE of some sort #
        ###################################

        # If it's main bin, special location
        main_bin_loc = 0x56000000 + segment['p_vaddr']
        if self.main_bin:
            # Step until we find a free spot
            while state.memory[main_bin_loc].page.mapped:
                main_bin_loc += state.memory._page_size

            return main_bin_loc

        # Shared Library
        else:
            # Check if we already have a base for this library
            if os.path.basename(self.filename) in state.posix.base_addrs:
                return state.posix.base_addrs[os.path.basename(self.filename)] + segment['p_vaddr']

            # Looks like we don't have a base address for this yet, time to find one.
            # TODO: Replace this with mmap call or something once implemented.
            while state.memory[state.libc.mmap_base].page.mapped:
                state.libc.mmap_base += state.memory._page_size

            # Put a page in-between
            state.libc.mmap_base += state.memory._page_size

            # Record it
            state.posix.base_addrs[os.path.basename(self.filename)] = state.libc.mmap_base

            return state.posix.base_addrs[os.path.basename(self.filename)]

        
    def map_sections(self, state):
        """Takes in State object and attempts to map this ELF files sections into it."""

        # TODO: Triton works on a global state right now... Update this once Triton gives actual contexts to work with

        #################
        # Load sections #
        #################

        # TODO: Don't allow overlaps
        # TODO: Support loading at different address

        # TODO: Flesh out the actual appropriate way to load...
        load_segments = [seg for seg in self.elffile.iter_segments() if seg['p_type'] == "PT_LOAD"]

        for segment in load_segments:
            vaddr = self._find_good_load_addr(segment,state)
            size = segment['p_memsz'] 
            flags = segment['p_flags']
            state.memory[vaddr] = segment.data()

            # TODO: Probably not handling p_align correctly
            for i in range(0, size, state.memory._page_size) + [size-1]:
                # TODO: Check for overlapping page permissions...
                page = state.memory[vaddr+i].page
                page.mapped = True
                # Segment permission flags are backwards from normal linux...
                if flags & 1 > 0:
                    page.execute = True
                if flags & 2 > 0:
                    page.write = True
                if flags & 4 > 0:
                    page.read = True

            # Record the base address
            if load_segments.index(segment) == 0:
                state.posix.base_addrs[os.path.basename(self.filename)] = vaddr

            logger.debug("Loading segment for {0} at {1} with perms {2}".format(self.filename, hex(vaddr), page.prot_str))

        """
        # Not all sections are loadable
        loadable_sections = [section for section in self.sections if section['sh_flags'] & 2]

        for section in loadable_sections:
            size   = section.header['sh_size']
            vaddr  = section.header['sh_addr']
            name   = section.name
            logger.debug('Loading 0x%08x - 0x%08x -- %s' %(vaddr, vaddr+size, name))
            state.memory[vaddr] = section.data()

            # Mark this memory as mapped, set permissions accordingly
            for i in range(0, size, state.memory._page_size) + [vaddr+size-1]:
                # TODO: Check for overlapping page permissions...
                page = state.memory[vaddr+i].page
                page.mapped = True
                # Everything is default readable
                page.read = True

                # Section is writable
                if section['sh_flags'] & 0x1 > 0:
                    page.write = True

                # Section is executable
                if section['sh_flags'] & 0x4 > 0:
                    page.execute = True

        """

        # Fixup mmap base
        while state.memory[state.libc.mmap_base].page.mapped:
            state.libc.mmap_base += state.memory._page_size

    def _relocate_normalize_addr(self, state, addr):
        """Takes in state object and address, and returns adjusted address. For instance, if this is a non-PIE binary with base address, no change. If this is PIE, adjust the offset to the real address."""

        # Do we have a base addr?
        if self.address != 0:
            if state.posix.base_addrs[os.path.basename(self.filename)] != self.address:
                logger.error("Binary {0} was loaded at non-requested base. I don't have this handled yet.".format(self.filename))
                return

            # We've loaded it as requested, this address should be right
            return addr

        return addr + state.posix.base_addrs[os.path.basename(self.filename)]


    def _relocate_x64(self, state, rel, name):
        """Handle relocating a specific relocation entry for x64"""
        desc = describe_reloc_type(rel['r_info_type'],self.elffile)
        address = self._relocate_normalize_addr(state, rel['r_offset'])
        addend = rel['r_addend']
        rela = rel.is_RELA()

        logger.error("Unhandled relocation type of {0} for symbol {1} in {2} at 0x{3:x}".format(desc, name, self.filename, address))

    def _relocate_x86(self, state, rel, name):
        """Handle relocating a specific relocation entry for x86"""
        desc = describe_reloc_type(rel['r_info_type'],self.elffile)
        address = self._relocate_normalize_addr(state, rel['r_offset'])

        logger.error("Unhandled relocation type of {0} for symbol {1} in {2} at 0x{3:x}".format(desc, name, self.filename, address))

    def perform_relocations(self, state):
        """Performs the relocations needed for this elf. This assumes the elf and libraries have been loaded."""
        # https://docs.oracle.com/cd/E19120-01/open.solaris/819-0690/chapter6-26/index.html
        # https://docs.oracle.com/cd/E23824_01/html/819-0690/chapter6-54839.html

        def _resolve_symbol_address(state, name, exclude=None):
            # Attempt to find the symbol
            resolved = state.symbol(name, exclude=exclude)
            if resolved is None:
                logger.warn("Unable to resolve address for symbol {0}".format(name))
            resolved_address = 0 if resolved == None else resolved.addr
            return resolved_address

        # Figure our appropriate relocation function
        if self.arch == "x64":
            relocate = self._relocate_x64
        elif self.arch == "x86":
            relocate = self._relocate_x86
        else:
            logger.error("Unknown arch type for relocation.")
            return

        # Loop through relocation sections
        for rel_sec in self.elffile.iter_sections():
            if type(rel_sec) is not RelocationSection:
                continue

            # Grab the symbol table
            symtab = self.elffile.get_section(rel_sec['sh_link'])

            # Loop through all relocations in this table
            for rel in rel_sec.iter_relocations():
                desc = describe_reloc_type(rel['r_info_type'],self.elffile)
                address = self._relocate_normalize_addr(state, rel['r_offset'])
                P = address
                name = symtab.get_symbol(rel['r_info_sym']).name
                # Resolving addend
                if rel.is_RELA():
                    A = state.se.Bytes(rel['r_addend'],length=self.bits/8)
                else:
                    A = state.memory[address:address+(self.bits/8)]

                # Need to change A to signed value
                if self.bits == 32:
                    A = ctypes.c_int32(int(A)).value
                elif self.bits == 64:
                    A = ctypes.c_int64(int(A)).value
                else:
                    logger.error("Unhandled bits of {0}".format(self.bits))

                logger.debug("Attempting to relocate \"{0}\" at {1} type {2}: {3}".format(name, hex(address), desc, rel))

                if desc in ["R_386_GLOB_DAT", "R_386_JUMP_SLOT","R_X86_64_GLOB_DAT","R_X86_64_JUMP_SLOT"]:
                    resolved_address = _resolve_symbol_address(state, name)
                    # Store the result
                    b = state.se.Bytes(length=self.bits/8,value=resolved_address)
                    state.memory[address] = b

                elif desc in ["R_386_RELATIVE","R_X86_64_RELATIVE"]:
                    # Adjust it to where the library was loaded
                    b = state.se.Bytes(value=int(A)+state.posix.base_addrs[os.path.basename(self.filename)], length=self.bits/8)
                    # Store it back
                    state.memory[address] = b

                elif desc in ["R_386_PC32"]:
                    S = _resolve_symbol_address(state, name)
                    # Calculate value
                    b = state.se.Bytes(value=int(S) + A - P, length=self.bits/8)
                    # Store it
                    state.memory[address] = b

                elif desc in ["R_X86_64_64","R_386_32"]:
                    S = _resolve_symbol_address(state, name)
                    # Calculate value
                    b = state.se.Bytes(value=int(S) + A, length=int(desc.split("_")[-1])/8)
                    # Store it
                    state.memory[address] = b

                elif desc in ["R_386_TLS_TPOFF", "R_X86_64_TPOFF64", "R_X86_64_DTPMOD64", "R_X86_64_DTPOFF64"]:
                    # http://git.yoctoproject.org/cgit/cgit.cgi/prelink-cross/plain/trunk/src/arch-i386.c?h=cross_prelink_r174
                    logger.info("Ignoring Thread Local Storage relocation.")

                # Copy will need to wait until everything is loaded....
                elif desc in ["R_386_COPY","R_X86_64_COPY"]:
                    S = _resolve_symbol_address(state, name, exclude=[os.path.basename(self.filename)])
                    S = state.memory[int(S):int(S) + (self.bits/8)]
                    state.memory[address] = S

                else:
                    # Call the architecture specific relocation
                    relocate(state, rel, name)

                


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

        try:
            dt = next(self.dynamic_by_tag_iter(tag))

        except StopIteration, TypeError:
            pass

        return dt

    def dynamic_by_tag_iter(self, tag):
        """Same as dynamic_by_tag except return generator for tags"""

        dt      = None
        dynamic = self.elffile.get_section_by_name('.dynamic')

        if not dynamic:
            return None

        return (t for t in dynamic.iter_tags() if tag == t.entry.d_tag)

    def find_library(self, library):
        """Takes in string name of library and attempts to resolve the location on the current machine."""

        # TODO: Probably a better way to do all this...

        # Implement RPATH and RUNPATH: https://en.wikipedia.org/wiki/Rpath
        ld = subprocess.check_output(["ldconfig","-p"]).split("\n")

        paths = [os.path.realpath(path.split("=> ")[1]) for path in ld if path.endswith("/" + library)]

        # Try them one at a time until we get one that looks to be a winner
        for path in paths:

            with open(path,"rb") as f:

                elffile = ELFFile(f)
                
                # Check that arch, bits, and endian match up
                if elffile.get_machine_arch() == self.elffile.get_machine_arch() and \
                elffile.elfclass == self.elffile.elfclass and \
                elffile.little_endian == self.elffile.little_endian:

                    # Found it
                    del elffile
                    return path

        return None

    def symbol(self, symbol):
        """Retrieve the given symbol. Basically the same as "symbols[symbol]" """
        return self.symbols[symbol] if symbol in self.symbols else None


    def __repr__(self):
        return "<ELF filename='{0}' abi='{1}'>".format(self.filename, self.abi_desc)

    ##############
    # Properties #
    ##############

    @property
    def abi(self):
        """What ABI to use? For instance, SYSV, NetBSD, etc."""
        return self.elffile['e_ident']['EI_OSABI']

    @property
    def abi_desc(self):
        """Human readable ABI Description."""
        return describe_ei_osabi(self.abi)

    @property
    def entry(self):
        """The entry point of this file. Not-adjusted for any base changes."""
        return self.elffile['e_entry']

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        if type(filename) is not str:
            raise Exception("Attempting to set filename from invalid type of {0}".format(type(filename)))

        if not os.path.isfile(filename):
            raise Exception("File '{0}' not found.".format(filename))

        self.__filename = os.path.abspath(filename)

    @property
    def bits(self):
        """How many bits is this elf file? integer, i.e.: 32, 64"""
        return self.elffile.elfclass

    @property
    def shared_objects(self):
        """Returns an ordered dictionary of shared objects this object relies on."""

        # Order can be important when loading objects
        objects = OrderedDict()

        # Find them and add them in order
        for obj in self.dynamic_by_tag_iter("DT_NEEDED"):
            objects[obj.needed] = self.find_library(obj.needed)

        return objects

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
                symbol_obj.source = os.path.basename(self.filename)

                # Add it to the dict
                symbols[symbol_name] = symbol_obj
        
        # Cache our work
        self.__symbols = symbols

        return symbols

    #@property
    #def triton_elf(self):
    #    """Returns a Triton elf object for this binary."""
    #    return lief.parse(self.project.filename)
            


from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection
from elftools.elf.descriptions import describe_e_type
from elftools.elf.descriptions import describe_ei_osabi
from elftools.elf.descriptions import describe_reloc_type
from larissa.Project import Project
from larissa.Loader.Symbol import Symbol
import triton
#import lief
import subprocess
import os
from collections import OrderedDict
import ctypes

