import logging
logger = logging.getLogger("Loader")

class Loader(object):

    def __init__(self, project):
        self.project = project
        self.file = open(self.project.filename,"rb")
        self._load_main_bin()

    def _load_main_bin(self):
        """Attempt to determine file type and load sub-class appropriately."""

        # Is it an ELF?
        try:
            self.elffile = ELFFile(self.file)
            del self.elffile
            self.main_bin = larissa.Loader.ELF.ELF(self.project)

        except ELFError:
            logger.error("Unknown or unsupported file type.")
            return


    ##############
    # Properties #
    ##############

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



from elftools.elf.elffile import ELFFile
from elftools.elf.elffile import ELFError
from larissa.Project import Project
import larissa.Loader.ELF
