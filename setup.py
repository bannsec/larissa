# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os
from setuptools.command.install import install
import tempfile
import shutil
import urllib2
import tarfile
from glob import glob

here = os.path.abspath(os.path.dirname(__file__))

long_description = "See website for more info."

def _install_z3():
    # Wheel files don't come with the z3 executable. Need to build.
    os.system("pip install --no-binary :all: z3-solver")

def _install_capstone():
    # Triton needs the deps that the wheel file doesn't have
    os.system("pip install --no-binary :all: capstone")

def _install_triton():
    # Triton isn't quite a package yet.
    dirpath = tempfile.mkdtemp()

    tgz_name = os.path.join(dirpath,"master.tar.gz")

    with open(tgz_name,"wb") as f:
        # Grab the current version
        response = urllib2.urlopen("https://github.com/JonathanSalwan/Triton/archive/master.tar.gz")
        f.write(response.read())
        response.close()

    os.chdir(dirpath)

    # Extract it
    tar = tarfile.open(tgz_name)
    tar.extractall()
    tar.close()

    # Move into dir and compile stuff
    os.chdir(glob("Triton*")[0])
    os.mkdir("build")
    os.chdir("build")

    os.system("cmake -DCMAKE_INSTALL_PREFIX={0} ..".format(os.environ['VIRTUAL_ENV']))
    os.system("make -j2 install")

    shutil.rmtree(dirpath)


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

