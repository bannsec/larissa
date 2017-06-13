import os
import larissa
import pytest
import larissa.State.plugins.memory

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")

# TODO: Really should have better tests than this...

def test_disasm_basic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    main = state.symbol('main')
    b = state.memory[main.addr:main.addr+32]
    b.pp()
    b = state.memory[main.addr]
    b.pp()

