import math

from tc2100.observation import Observation, ThermocoupleType, TemperatureUnit,\
    MeterTime

from . import datastrings


def test_temp_unit_strings():
    assert str(TemperatureUnit.K) == 'K'
    assert int(TemperatureUnit.K) == 3


def test_thermocouple_strings():
    assert str(ThermocoupleType.K) == 'K'
    assert int(ThermocoupleType.K) == 1


def test_metertime_create():
    m = MeterTime(255, 3, 2)
    assert m.hours == 255
    assert m.minutes == 3
    assert m.seconds == 2
    assert str(m) == "255:03:02"


def test_metertime_packunpack():
    m = MeterTime.from_bytes(datastrings.NO_DATA[13:16])
    assert m.hours == 0
    assert m.seconds == 42
    assert m.minutes == 6


def test_decode_no_data():
    msg = Observation.from_bytes(datastrings.NO_DATA[5:5+11])
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.temperatures[0] != msg.temperatures[0]
    assert msg.temperatures[1] != msg.temperatures[1]
    assert msg.unit == TemperatureUnit.C
    assert str(msg.meter_time) == "000:06:42"
    msgdict = msg.as_dict()
    assert str(msgdict['meter_time']) == "000:06:42"


def test_decode_ch1():
    msg = Observation.from_bytes(datastrings.CH1[5:5+11])
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.temperatures[0] == 20.8
    assert msg.temperatures[1] != msg.temperatures[1]
    assert msg.unit == TemperatureUnit.C


def test_decode_ch2():
    msg = Observation.from_bytes(datastrings.CH2[5:5+11])
    assert msg.thermocouple_type == ThermocoupleType.N
    assert msg.temperatures[0] != msg.temperatures[0]
    assert msg.temperatures[1] == 20.4
    assert msg.unit == TemperatureUnit.C


def test_decode_kelvin():
    msg = Observation.from_bytes(datastrings.BOTH_K[5:5+11])
    assert msg.temperatures[0] == datastrings.BOTH_K_CH1
    assert msg.temperatures[1] == datastrings.BOTH_K_CH2
    assert msg.unit == TemperatureUnit.K


def test_decode_reencode():
    msg = Observation.from_bytes(datastrings.BOTH[5:5+11])

    assert msg.thermocouple_type == ThermocoupleType.K
    assert msg.temperatures[0] == 22.8
    assert msg.temperatures[1] == 23.2
    assert msg.unit == TemperatureUnit.C
    assert str(msg.meter_time) == "002:28:30"

    outb = msg.to_bytes()
    cmp = datastrings.BOTH[5:5+11]
    assert outb == cmp


def test_convert_synthetic():
    msg = Observation(temperature_ch1=math.nan,
                      temperature_ch2=math.nan,
                      unit='K', thermocouple_type='N',
                      meter_time=None, system_time=None)
    out = msg.to_bytes()
    inp = Observation.from_bytes(out)

    assert inp.temperatures[0] != inp.temperatures[0]
    assert inp.temperatures[1] != inp.temperatures[1]
    assert inp.thermocouple_type == ThermocoupleType.N
    assert inp.unit == TemperatureUnit.K
    assert str(inp.meter_time) == "000:00:00"
