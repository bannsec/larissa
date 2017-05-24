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
import subprocess
import re

here = os.path.abspath(os.path.dirname(__file__))

long_description = "See website for more info."

def find_file(file_name):
    """Locate the given file from our python root."""
    for root, dirs, files in os.walk(sys.prefix):
        if file_name in files:
            return root
    
    raise Exception("Cannot find file {0}".format(file_name))

def _get_boost_path():
    # Is it installed at the system level?
    if os.path.isdir("/usr/include/boost"):
        return "/usr/include"

    # Is it already installed in the virtualenv?
    if os.path.isdir(os.path.join(sys.prefix, "include", "boost")):
        return sys.prefix

    return None

def _install_boost():
    """Determine if we need to install liboost, and do so."""

    # If it's already installed, don't install it.
    if _get_boost_path() != None:
        return

    # Looks like we need to build it
    try:
        subprocess.check_output("pip install larissa_boost",shell=True)
    except Exception as e:
        raise Exception(e.output)


def _install_z3():
    # Need to build this.
    # TODO: Remove this from my package once z3-solver gets updated to install the binary

    os.chdir(os.path.join(here,"lib","z3"))

    try:
        subprocess.check_output("python scripts/mk_make.py --python",shell=True)
    except Exception as e:
        raise Exception(e.output)

    os.chdir("build")

    try:
        subprocess.check_output("make install -j{0}".format(multiprocessing.cpu_count()),shell=True)
    except Exception as e:
        raise Exception(e.output)

    os.chdir(here)

def _install_capstone():
    # Triton needs the deps that the wheel file doesn't have
    try:
        subprocess.check_output("pip install capstone==3.0.5-rc2",shell=True)
    except Exception as e:
        raise Exception(e.output)

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

    cmake_options = [
            '-DCMAKE_INSTALL_PREFIX={0}'.format(sys.prefix),
            '-DCAPSTONE_INCLUDE_DIR={0}'.format(capstone_include),
            '-DCAPSTONE_LIBRARY={0}'.format(capstone_lib)
            ]

    # Custom boost install dir
    if _get_boost_path() != "/usr/include":
        cmake_options.append("-DBoost_INCLUDE_DIR={0}".format(os.path.join(sys.prefix,"include")))
        cmake_options.append("-DBoost_LIBRARY_DIR={0}".format(os.path.join(sys.prefix,"lib")))

    try:
        subprocess.check_output("cmake {0} ..".format(' '.join(cmake_options)),shell=True)
    except Exception as e:
        raise Exception(e.output)
    
    try:
        subprocess.check_output("CPATH={1} make -j{0} install".format(multiprocessing.cpu_count(), z3_paths),shell=True)
    except Exception as e:
        raise Exception(e.output)

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

