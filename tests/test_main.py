from tc2100.__main__ import version_string, get_arg_parser, \
    _make_stdout_linebuffered


def test_version_string():
    assert isinstance(version_string(), str)


def test_arg_parser():
    get_arg_parser()


def test_make_stdout_unbuffered():
    _make_stdout_linebuffered()
