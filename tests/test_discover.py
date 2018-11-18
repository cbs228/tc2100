from tc2100.discover import discover, PRODUCT_ID, VENDOR_ID

from collections import namedtuple

FakePort = namedtuple('FakePort', field_names=('vid', 'pid'))
FakeNotUsb = namedtuple('FakeNotUsb', field_names=('com',))


def test_discover():
    out = discover(list())
    assert len(out) == 0

    mockports = [FakePort(vid=VENDOR_ID[0], pid=PRODUCT_ID[0]),
                 FakePort(vid=0, pid=0),
                 FakeNotUsb(com='/dev/ttyACM0')]
    out = discover(mockports)
    assert len(out) == 1
    assert out[0].vid == VENDOR_ID[0]

    out = discover((mockports[1], ))
    assert len(out) == 0
