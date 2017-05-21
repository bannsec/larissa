import logging
logger = logging.getLogger("larissa.SimProcedures.Syscalls")

class Syscalls(object):
    """Abstract a syscall. Make the selection of call agnostic from calling."""

    def __init__(self, project):

        self.project = project

        self._load_syscall_table()

    def _load_syscall_table(self):
        """Determine correct syscall table to load and load it."""

        # Grab and format ABI
        abi = self.project.loader.main_bin.abi.replace("ELFOSABI_","")

        # If it's Linux, treat it as SYSV for now
        abi = abi.replace("LINUX","SYSV")

        # Determine correct module to load
        module = "larissa.SimProcedures.Syscalls.{0}.{1}_{2}".format(abi, self.project.loader.main_bin.arch, self.project.loader.main_bin.bits)
        
        try:
            module = importlib.import_module(module)
        except ImportError:
            logger.error("Unknown syscall table for current architecture.")
            return

        # Grab the table
        self.syscall_table = module.syscall_table

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

	

import importlib

from ...Project import Project
