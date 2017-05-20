
class State(object):

    def __init__(self, project):
        self.project = project
        
        # Init the state
        self.binary = self.project.loader.main_bin.map_sections(None)

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
    def binary(self):
        """The triton binary object for this state."""
        return self.__binary

    @binary.setter
    def binary(self, binary):
        self.__binary = binary

import triton
from larissa.Project import Project

