[ ![Codeship Status for Owlz/larissa](https://codeship.com/projects/580bce60-22a0-0135-eb40-52028c1190b7/status?branch=master)](https://app.codeship.com/projects/221744)
[![Coverage Status](https://coveralls.io/repos/github/Owlz/larissa/badge.svg?branch=HEAD)](https://coveralls.io/github/Owlz/larissa?branch=HEAD)

# About
This is basically a toy project for the moment. I'm curious if I can make Triton be a little more user friendly. I'm planning on modeling interactions after how you would interact through angr and attempt to make the interactions more pythonic.

# Install
Be sure you have lib boost, cmake, and python2.7 installed. On Ubuntu, that's:

```bash
$ sudo apt-get install libboost-dev cmake python2.7-dev
```

Installation has only been tested into a virtual environment.

```bash
$ virtualenv larissa
$ source larissa/bin/activate
```

## Pypi Install
Installing from pypi (i.e.: "normal" pip install) is:

```bash
(larissa)$ pip install larissa
```

## Repo install
If you want to install from the repo, you will need to clone it. Given larissa's current reliance on submodules, you will want to recursively clone it.

```bash
(larissa)$ git clone --recursive https://github.com/Owlz/larissa.git
(larissa)$ cd larissa
(larissa)$ pip install .
```

Be patient. This installer will compile z3 as well as triton. This will take a little while.

# Unit Tests
You can run the unit tests with the following command from the root of the git repo:

```bash
$ pytest --boxed -n 8 --cov=larissa --cov-config=.coveragerc tests/
$ pytest --boxed -n 8 --cov=larissa --cov-config=.coveragerc --cov-report=html tests/ # For pretty html output
```
