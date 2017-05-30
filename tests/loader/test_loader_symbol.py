import os
import larissa

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_symbol_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    assert proj.loader.symbol('main').source == "simple_pic_pie"
    assert "libc" in proj.loader.symbol('stdout').source

def test_symbol_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    assert proj.loader.symbol('main').source == "simple_nopic_nopie"
    assert "libc" in proj.loader.symbol('stdout').source

def test_symbol_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    assert proj.loader.symbol('main').source == "simple_nopic_nopie"
    assert "libc" in proj.loader.symbol('stdout').source

def test_symbol_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_pie"))
    assert proj.loader.symbol('main').source == "simple_nopic_pie"
    assert "libc" in proj.loader.symbol('stdout').source

def test_symbol_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    assert proj.loader.symbol('main').source == "simple_pic_pie"
    assert "libc" in proj.loader.symbol('stdout').source

def test_symbol_not_found():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    assert proj.loader.symbol('doesnt_exist') == None

"""
# TODO: Build binary to test this.

def test_symbol_first_option():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))

    # We expect to find the .text symbol for libc first given this argument.
    assert 'libc' in proj.loader.symbol('.text', u'libc.so.6').source
"""
