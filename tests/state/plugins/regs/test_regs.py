import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")


def test_regs_ia32_names():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # Just make sure we have some basics
    regs = ["eax","ebx","ecx","edx","esi","edi","ebp","esi","esp"]
    assert all( hasattr(state.regs,reg) and getattr(state.regs,reg).name == reg for reg in regs)

def test_regs_amd64_names():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # Just make sure we have some basics
    regs = ["eax","ebx","ecx","edx","esi","edi","rax","rbx","rcx","rdx","rdi","rsi","rip","rbp","rsp"]
    assert all( hasattr(state.regs,reg) and getattr(state.regs,reg).name == reg for reg in regs)
