from datetime import timedelta
import math

from tc2100.observation import Observation, ThermocoupleType, TemperatureUnit

NO_DATA = (b"\x65\x14\x00\x00\x00\x09\xB0\x09\xB4\x07\x81"
           b"\x40\x40\x00\x06\x2A\x0D\x0A")

CH1 = (b"\x65\x14\x00\x00\x00\x00\xD0\x09\xB3\x07\x81\x08"
       b"\x40\x00\x0B\x2B\x0D\x0A")

CH2 = (b"\x65\x14\x00\x00\x00\x09\xAF\x00\xCC\x07\x81\x40"
       b"\x08\x00\x0C\x0C\x0D\x0A")

BOTH = (b"\x65\x14\x00\x00\x00\x00\xE4\x00\xE8\x01\x81"
        b"\x08\x08\x02\x1C\x1E\x0D\x0A")

BOTH_K = (b"\x65\x14\x00\x00\x00\x0B\x8E\x0B\x95\x01\x83"
          b"\x08\x08\x00\x02\x22\x0D\x0A")


def temp_unit_strings():
    assert str(TemperatureUnit.K) == 'K'
    assert int(TemperatureUnit.K) == 3


def thermocouple_strings():
    assert str(ThermocoupleType.K) == 'K'
    assert int(ThermocoupleType.K) == 1


def test_decode_no_data():
    msg = Observation.from_bytes(NO_DATA)
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.channel_temp[0] != msg.channel_temp[0]
    assert msg.channel_temp[1] != msg.channel_temp[1]
    assert msg.units == TemperatureUnit.C
    assert msg.meter_time == timedelta(seconds=42, minutes=6)


def test_decode_ch1():
    msg = Observation.from_bytes(CH1)
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.channel_temp[0] == 20.8
    assert msg.channel_temp[1] != msg.channel_temp[1]
    assert msg.units == TemperatureUnit.C


def test_decode_ch2():
    msg = Observation.from_bytes(CH2)
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.channel_temp[0] != msg.channel_temp[0]
    assert msg.channel_temp[1] == 20.4
    assert msg.units == TemperatureUnit.C


def test_decode_kelvin():
    msg = Observation.from_bytes(BOTH_K)
    assert msg.channel_temp[0] == msg.channel_temp[0]
    assert msg.channel_temp[1] == msg.channel_temp[1]
    assert msg.units == TemperatureUnit.K


def test_decode_reencode():
    msg = Observation.from_bytes(BOTH)

    assert msg.thermocouple_type == ThermocoupleType.K
    assert msg.channel_temp[0] == 22.8
    assert msg.channel_temp[1] == 23.2
    assert msg.units == TemperatureUnit.C
    assert msg.meter_time == timedelta(seconds=30, minutes=28, hours=2)

    outb = msg.to_bytes()
    assert outb == BOTH


def test_convert_synthetic():
    msg = Observation(channel_temp=[math.nan, math.nan], units='K',
                      thermocouple_type='N')
    out = msg.to_bytes()
    inp = Observation.from_bytes(out)

    assert inp.channel_temp[0] != inp.channel_temp[0]
    assert inp.channel_temp[1] != inp.channel_temp[1]
    assert inp.thermocouple_type == ThermocoupleType.N
    assert inp.units == TemperatureUnit.K
    assert inp.meter_time == timedelta(seconds=0)
