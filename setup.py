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

here = os.path.abspath(os.path.dirname(__file__))

long_description = "See website for more info."

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
    os.system("pip install --no-binary :all: capstone")

def _install_triton():
    # Using triton version included in larissa due to triton not being in pypi
    os.chdir(os.path.join(here,"lib","triton"))
    os.mkdir("build")
    os.chdir("build")

    os.system("cmake -DCMAKE_INSTALL_PREFIX={0} ..".format(sys.prefix))
    os.system("make -j{0} install".format(multiprocessing.cpu_count()))

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
    version='0.0.2',
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
        'dev': ['ipython<6','twine'],
    },
    install_requires=["pyelftools"],
    keywords='symbolic execution triton',
    packages=find_packages(exclude=['contrib', 'docs', 'tests','lib']),
    cmdclass={
        'install': CustomInstallCommand,
    },
)

