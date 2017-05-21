
class SimProcedures(object):
    
    def __init__(self, project):

        self.project = project

        # Setup a Syscall resolver
        self.syscalls = Syscalls(self.project)


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

from ..Project import Project
from .Syscalls import Syscalls

