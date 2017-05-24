# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os, sys
from setuptools.command.install import install
import tempfile
import shutil
import urllib2
import tarfile
from glob import glob
import multiprocessing
import re

here = os.path.abspath(os.path.dirname(__file__))

long_description = "See website for more info."

def find_file(file_name):
    """Locate the given file from our python root."""
    for root, dirs, files in os.walk(sys.prefix):
        if file_name in files:
            return root
    
    raise Exception("Cannot find file {0}".format(file_name))

def _install_z3():
    # Need to build this.
    # TODO: Remove this from my package once z3-solver gets updated to install the binary

    os.chdir(os.path.join(here,"lib","z3"))

    os.system("python scripts/mk_make.py --python")
    os.chdir("build")
    os.system("make install -j{0}".format(multiprocessing.cpu_count()))

    os.chdir(here)

def _install_capstone():
    # Triton needs the deps that the wheel file doesn't have
    os.system("pip install capstone==3.0.5-rc2")

def _install_triton():
    # Locate the needed libraries
    capstone_include = re.match("(.*)/capstone$", find_file("capstone.h")).group(1)
    capstone_lib = os.path.join(find_file("libcapstone.so"),"libcapstone.so")
    z3_paths = find_file("z3++.h")
    z3_paths += ":" + find_file("z3.h")
    z3_paths += ":" + find_file("z3_ast_containers.h")


    # Using triton version included in larissa due to triton not being in pypi
    os.chdir(os.path.join(here,"lib","triton"))
    os.mkdir("build")
    os.chdir("build")

    os.system("cmake -DCMAKE_INSTALL_PREFIX={0} -DCAPSTONE_INCLUDE_DIR={1} -DCAPSTONE_LIBRARY={2} ..".format(sys.prefix, capstone_include, capstone_lib))
    os.system("CPATH={1} make -j{0} install".format(multiprocessing.cpu_count(), z3_paths))

    os.chdir(here)

class CustomInstallCommand(install):
    """Need to custom compile some things."""
    def run(self):
        # Save off our dir
        cwd = os.getcwd()
        self.execute(_install_z3, (), msg='Compiling/Installing z3')
        self.execute(_install_capstone, (), msg='Compiling/Installing capstone')
        self.execute(_install_triton, (), msg='Compiling/Installing triton')

        # Make sure we're in the right place
        os.chdir(cwd)
        install.run(self)

setup(
    name='larissa',
    version='0.0.4',
    description='Tool to automate working with Triton',
    long_description=long_description,
    url='https://github.com/owlz/larissa',
    author='Michael Bann',
    author_email='self@bannsecurity.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console'
    ],
    extras_require={
        'dev': ['ipython<6','twine','pytest','python-coveralls','coverage','pytest-cov','pytest-xdist'],
    },
    install_requires=["pyelftools"],
    keywords='symbolic execution triton',
    packages=find_packages(exclude=['contrib', 'docs', 'tests','lib']),
    cmdclass={
        'install': CustomInstallCommand,
    },
)

