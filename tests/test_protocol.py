import io

from tc2100.protocol import ThermometerProtocol, ThermometerToCSVProtocol
from tc2100.observation import Observation

from . import datastrings


class BufferingThermProto(ThermometerProtocol):
    def __init__(self):
        super().__init__()
        self.messages = []

    def observation_received(self, observation: Observation):
        self.messages.append(observation)


def test_framing_empty():
    buf = BufferingThermProto()
    buf.dataReceived(b"")

    assert len(buf.messages) == 0
    assert len(buf._buf) == 0


def test_framing_leadingzeros():
    buf = BufferingThermProto()
    buf.dataReceived(datastrings.FRAMING_LEADZERO)

    assert len(buf.messages) == 1
    assert len(buf._buf) == 0
    assert buf.messages[0].temperatures[0] == datastrings.BOTH_K_CH1
    assert buf.messages[0].temperatures[1] == datastrings.BOTH_K_CH2


def test_framing_bad_header():
    buf = BufferingThermProto()
    buf.dataReceived(datastrings.FRAMING_BAD_HEADER)

    assert len(buf.messages) == 1
    assert len(buf._buf) == 0
    assert buf.messages[0].temperatures[0] == datastrings.BOTH_K_CH1
    assert buf.messages[0].temperatures[1] == datastrings.BOTH_K_CH2


def test_framing_trail_header():
    buf = BufferingThermProto()
    buf.dataReceived(datastrings.FRAMING_TRAIL_HEADER)

    assert len(buf.messages) == 1
    assert buf._buf == b"\x65\x14\xFF"
    assert buf.messages[0].temperatures[0] == datastrings.BOTH_K_CH1
    assert buf.messages[0].temperatures[1] == datastrings.BOTH_K_CH2


def test_framing_two_messages():
    buf = BufferingThermProto()
    buf.dataReceived(datastrings.FRAMING_TWOMSGS)

    assert len(buf.messages) == 2
    assert len(buf._buf) == 0
    assert buf.messages[0].temperatures[0] == datastrings.BOTH_K_CH1
    assert buf.messages[0].temperatures[1] == datastrings.BOTH_K_CH2
    assert buf.messages[1].temperatures[0] == datastrings.BOTH_K_CH1
    assert buf.messages[1].temperatures[1] == datastrings.BOTH_K_CH2


def test_framing_bad_msg():
    buf = BufferingThermProto()
    buf.dataReceived(datastrings.BAD_UNIT)

    assert len(buf.messages) == 0


def test_csvwriter():
    buf = io.StringIO()
    conv = ThermometerToCSVProtocol(file_handle=buf)
    conv.dataReceived(datastrings.FRAMING_LEADZERO)
    conv.dataReceived(datastrings.FRAMING_LEADZERO)
    lines = buf.getvalue().splitlines()
    assert len(lines) == 3
