import os
import larissa
from larissa.Loader.ELF import ELF

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")


"""
def test_shared_objects_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    assert len(proj.loader.shared_objects) == 1
    assert type(proj.loader.shared_objects[u'libc.so.6']) == ELF
    
def test_shared_objects_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    assert len(proj.loader.shared_objects) == 1
    assert type(proj.loader.shared_objects[u'libc.so.6']) == ELF

def test_shared_objects_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    assert len(proj.loader.shared_objects) == 1
    assert type(proj.loader.shared_objects[u'libc.so.6']) == ELF

def test_shared_objects_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_pie"))
    assert len(proj.loader.shared_objects) == 1
    assert type(proj.loader.shared_objects[u'libc.so.6']) == ELF

def test_shared_objects_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    assert len(proj.loader.shared_objects) == 1
    assert type(proj.loader.shared_objects[u'libc.so.6']) == ELF
"""
