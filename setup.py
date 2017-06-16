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
import multiprocessing
import subprocess
import re
from version import version

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
        # Is it new enough?
        if _is_boost_new_enough("/usr/include"):
            return "/usr/include"

    # Is it already installed in the virtualenv?
    # Alternate location
    if os.path.isdir(os.path.join(sys.prefix, "boost", "include", "boost")):
        print("Path 1")
        # Is it new enough?
        if _is_boost_new_enough(os.path.join(sys.prefix,"boost", "include")):
            print("New enough")
            return os.path.join(sys.prefix, "boost")

    # Is it already installed in the virtualenv?
    if os.path.isdir(os.path.join(sys.prefix, "include", "boost")):
        print("Path 2")
        # Is it new enough?
        if _is_boost_new_enough(os.path.join(sys.prefix,"include")):
            print("New enough")
            return sys.prefix

    print("Nothing")

    return None

def _get_boost_version(boost_path):
    # Assuming the path exists here
    # Return (major, minor, patch)

    with open(os.path.join(boost_path,"boost","version.hpp"),"r") as f:
        data = f.read()

    version = int(re.findall("#define +BOOST_VERSION +([0-9]+)",data)[0])

    return version / 100000, version / 100 % 1000, version % 100

def _is_boost_new_enough(boost_path):
    # Caveat, it has to be a high enough version...
    major, minor, patch = _get_boost_version(boost_path)

    if major > 1:
        return True

    if major == 1 and minor >= 55:
        return True

    return False

def _install_boost():
    """Determine if we need to install liboost, and do so."""

    # If it's already installed, don't install it.
    if _get_boost_path() != None:

        # Caveat, it has to be a high enough version...
        major, minor, patch = _get_boost_version(_get_boost_path())

        if major > 1:
            return

        if major == 1 and minor >= 55:
            return

    print("Installing boost.")

    # Looks like we need to build it
    try:
        #out = subprocess.check_output("pip install -vvv larissa_boost",shell=True)
        # No idea why setup.py correctly installs larissa_boost in this case where pip does not.
        os.system("pip download larissa_boost")
        os.system("tar xf larissa_boost*")
        _, names, _ = next(os.walk("."))
        os.chdir([name for name in names if "larissa_boost" in name][0])
        out = subprocess.check_output("python setup.py install",shell=True)
    except Exception as e:
        raise Exception(e.output)

    print(out)
    print(os.system("ls -la $VIRTUAL_ENV/"))
    print(os.system("ls -la $VIRTUAL_ENV/include/"))
    print(os.system("ls -la $VIRTUAL_ENV/boost/"))
    print(os.system("ls -la $VIRTUAL_ENV/boost/include"))


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

    # Sym-link it into lib
    os.symlink(os.path.join(find_file("libcapstone.so"),"libcapstone.so"), os.path.join(sys.prefix,"lib","libcapstone.so.3"))

def _install_triton():
    # Locate the needed libraries
    capstone_include = re.match("(.*)/capstone$", find_file("capstone.h")).group(1)
    capstone_lib = os.path.join(find_file("libcapstone.so"),"libcapstone.so")
    cpath = [find_file("z3++.h")]
    cpath.append(find_file("z3.h"))
    cpath.append(find_file("z3_ast_containers.h"))

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
        cmake_options.append("-DBoost_INCLUDE_DIR={0}".format(os.path.join(_get_boost_path(),"include")))
        cmake_options.append("-DBoost_LIBRARY_DIR={0}".format(os.path.join(_get_boost_path(),"lib")))

        cpath = ["/usr/include"] + cpath
        cpath.append(os.path.join(_get_boost_path(),"include"))

    try:
        print("cmake {0} ..".format(' '.join(cmake_options)))
        subprocess.check_output("cmake {0} ..".format(' '.join(cmake_options)),shell=True)
    except Exception as e:
        raise Exception(e.output)
    
    try:
        print("CPATH={1} make -j{0} install".format(multiprocessing.cpu_count(), ':'.join(cpath)))
        subprocess.check_output("CPATH={1} make -j{0} install".format(multiprocessing.cpu_count(), ':'.join(cpath)),shell=True)
    except Exception as e:
        raise Exception(e.output)

    os.chdir(here)

class CustomInstallCommand(install):
    """Need to custom compile some things."""
    def run(self):
        # Save off our dir
        cwd = os.getcwd()
        self.execute(_install_boost, (), msg='Compiling/Installing Boost')
        self.execute(_install_z3, (), msg='Compiling/Installing z3')
        self.execute(_install_capstone, (), msg='Compiling/Installing capstone')
        self.execute(_install_triton, (), msg='Compiling/Installing triton')

        # Make sure we're in the right place
        os.chdir(cwd)
        install.run(self)

setup(
    name='larissa',
    version=version,
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
        'dev': ['six','ipython<6','twine','pytest','python-coveralls','coverage','pytest-cov','pytest-xdist'],
    },
    install_requires=["pyelftools","prettytable"],
    keywords='symbolic execution triton',
    packages=find_packages(exclude=['contrib', 'docs', 'tests','lib']),
    cmdclass={
        'install': CustomInstallCommand,
    },
)

