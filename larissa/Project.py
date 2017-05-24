
class Project(object):

    def __init__(self, filename):
        """
        filename = file to load up
        """

        self.filename = filename
        self.factory = Factory(self)
        self.loader = Loader(self)

        self.simprocedures = SimProcedures(self)

        triton.setAstRepresentationMode(triton.AST_REPRESENTATION.PYTHON)

    def __repr__(self):
        return "<Project filename={0}>".format(self.filename)

    ##############
    # Properties #
    ##############

    @property
    def loader(self):
        return self.__loader

    @loader.setter
    def loader(self, loader):
        if type(loader) is not Loader:
            raise Exception("Invalid type for loader of {0}".format(type(loader)))

        self.__loader = loader

    @property
    def factory(self):
        return self.__factory

    @factory.setter
    def factory(self, factory):
        if type(factory) is not Factory:
            raise Exception("Invalid type for factory of {0}".format(type(factory)))

        self.__factory = factory

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        if type(filename) is not str:
            raise Exception("Attempting to set filename from invalid type of {0}".format(type(filename)))

        if not os.path.isfile(filename):
            raise Exception("File '{0}' not found.".format(filename))

        self.__filename = filename

import os
from larissa.Factory import Factory
from larissa.Loader import Loader
from .SimProcedures import SimProcedures
import triton
