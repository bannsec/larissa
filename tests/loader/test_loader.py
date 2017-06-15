import os
import larissa

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_loader_lookup_obj_by_name():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    assert os.path.basename(proj.loader._lookup_obj_by_name("simple_pic_pie").filename) == "simple_pic_pie"
    assert "libc" in os.path.basename(proj.loader._lookup_obj_by_name("libc.so.6").filename)

    # Little dance here because we don't know what version of libc will be on our unit testing machine
    name = os.path.basename(proj.loader._lookup_obj_by_name("libc.so.6").filename)
    assert os.path.basename(proj.loader._lookup_obj_by_name(name).filename) == name
