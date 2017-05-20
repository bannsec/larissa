import logging
logger = logging.getLogger("larissa.Loader")

class Loader(object):

    def __init__(self, project):

        self.shared_objects = OrderedDict()

        self.project = project
        self.file = open(self.project.filename,"rb")
        
        self._load_all_bins()

    def _load_all_bins(self):
        """Load all the bins! Start with the initial main binary. Then load all the deps."""

        # Try to load the main binary
        self.main_bin = self._load_bin(self.project.filename)

        # Sanity check
        if self.main_bin == None:
            logger.error("Something went wrong. Unable to load specified file.")
            return

        # Now try to load the deps
        for name in self.main_bin.shared_objects:
            
            path = self.main_bin.shared_objects[name]

            # If we couldn't find the dll, note it and move on
            if path == None:
                logger.warn("Could not find shared object for {0}".format(name))
                continue

            # Load it
            self.shared_objects[name] = self._load_bin(path)


    def _load_bin(self, path):
        """Attempt to determine file type and load sub-class appropriately.
            NOTE: This does NOT initialize any memory. Simply loads the object.
            
            Returns larissa object if successful, or None otherwise.
        """

        with open(path, "rb") as f:

            # Is it an ELF?
            try:
                self.elffile = ELFFile(self.file)
                del self.elffile
                return larissa.Loader.ELF.ELF(self.project, filename=path)

            except ELFError:
                logger.error("Unknown or unsupported file type.")
                return None

            # TODO: Support PE


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

from collections import OrderedDict

from elftools.elf.elffile import ELFFile
from elftools.elf.elffile import ELFError
from larissa.Project import Project
import larissa.Loader.ELF
