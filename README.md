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
(larissa)$ pip install larissa
```

Be patient. This installer will compile z3 as well as triton. This will take a little while.
