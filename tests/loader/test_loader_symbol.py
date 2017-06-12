import os
import larissa
import pytest

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

def test_symbol_first_option():
    proj = larissa.Project(os.path.join(bin_path,"amd64","symbol_collide"))

    # We define gets as a symbol both in the main bin and libc. Main bin will normally be searched first.
    # Specifying libc here should cause the symbol from libc to be returned.
    assert 'libc' in proj.loader.symbol('gets', u'libc.so.6').source

def test_symbol_repr():
    # Just making sure it doesn't crash anything...
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))

    repr(proj.loader.symbol('main'))

def test_symbol_source_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))

    sym = larissa.Loader.Symbol.Symbol()

    # This should fail
    with pytest.raises(Exception):
        sym.source = 12345

def test_symbol_name_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))

    sym = larissa.Loader.Symbol.Symbol()

    # This should fail
    with pytest.raises(Exception):
        sym.name = 12345

def test_symbol_addr_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))

    sym = larissa.Loader.Symbol.Symbol()

    # This should fail
    with pytest.raises(Exception):
        sym.addr = "0x1234"

