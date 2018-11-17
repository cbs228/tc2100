""" Temperature observation message """

import enum
import math
import struct
from struct import Struct
from typing import List, Tuple
from datetime import datetime
from datetime import timedelta
from datetime import timezone


@enum.unique
class TemperatureUnit(enum.IntEnum):
    """ A unit of temperature """

    C = 1
    """ Degrees Celsius """

    F = 2
    """ Fahrenheit """

    K = 3
    """ Kelvin """

    def __str__(self):
        return self.name


@enum.unique
class ThermocoupleType(enum.IntEnum):
    """ A type of thermocouple """

    K = 1
    """ K Type """

    J = 2
    """ J Type """

    T = 3
    """ T Type """

    E = 4
    """ E Type """

    R = 5
    """ R Type """

    S = 6
    """ S Type """

    N = 7
    """ N Type """

    def __str__(self):
        return self.name


class Observation:
    """ Temperature observation message from the thermometer

    :ivar channel_temp: temperature on each channel. If a channel has no
          probe connected, or the measured value is out-of-range, then the
          value will be NaN.
    :ivar units: physical unit of measure for all channels
    :ivar thermocouple_type: the type of thermocouple for all channels
    :ivar system_time: the `datetime` from your system clock at the time the
          message was recorded
    :ivar meter_time: time output by the meter. Time starts at 00h:00m:00s
          at power-on time and counts up, with one second resolution
    """

    _header = b"\x65\x14"
    _trailer = b"\x0d\x0a"
    _flag_valid = 0x08
    _flag_invalid = 0x40
    _invalid_placeholder = -32768
    _mask_lowbyte_only = 0x0F
    _units_highbyte = 0x80
    _hour = timedelta(hours=1)
    _minute = timedelta(minutes=1)
    _second = timedelta(seconds=1)
    _format = Struct(
        "!"
        "2s"    # header
        "3x"    # pad / don't care
        "h"     # ch. 1 measurement, in tens of display units
        "h"     # ch. 2 measurement, in tens of display units
        "B"     # thermocouple type (enumerated)
        "B"     # display unit (enumerated)
        "B"     # ch. 1 validity / status flag
        "B"     # ch. 2 validity / status flag
        "B"     # elapsed time, hours
        "B"     # elapsed time, minutes
        "B"     # elapsed time, seconds
        "2s"    # trailer
    )

    def __init__(self, channel_temp: List[float],
                 units: TemperatureUnit or str,
                 thermocouple_type: ThermocoupleType or str,
                 system_time: datetime = None,
                 meter_time: timedelta = None):
        self.channel_temp = channel_temp            # type: List[float]
        if isinstance(units, str):
            self.units = TemperatureUnit[units]
        else:
            self.units = units                      # type: TemperatureUnit
        if isinstance(thermocouple_type, str):
            self.thermocouple_type = ThermocoupleType[thermocouple_type]
        else:
            self.thermocouple_type =\
                thermocouple_type  # type: ThermocoupleType

        self.system_time = system_time              # type: datetime
        if self.system_time is None:
            self.system_time = datetime.min

        self.meter_time = meter_time                # type: timedelta
        if self.meter_time is None:
            self.meter_time = timedelta()

    def to_bytes(self) -> bytes:
        """ Convert to wireline representation

        The conversion will be lossy if, for example, the channel temperatures
        are not evenly divisible by 0.1.

        :return: Packed byte representation of this Observation
        """
        # convert all channels
        assert len(self.channel_temp) == 2
        chan_bytes = []
        chan_valid = []
        for tmp in self.channel_temp:
            if not math.isfinite(tmp):
                chan_bytes.append(self._invalid_placeholder)
                chan_valid.append(self._flag_invalid)
                continue
            chan_bytes.append(int(tmp * 10))
            chan_valid.append(self._flag_valid)

        # convert time duration
        hrs, rem = divmod(self.meter_time, self._hour)
        mins, rem = divmod(rem, self._minute)
        secs, _ = divmod(rem, self._second)

        return self._format.pack(
            self._header,
            chan_bytes[0],
            chan_bytes[1],
            int(self.thermocouple_type),
            int(self.units | self._units_highbyte),
            chan_valid[0],
            chan_valid[1],
            int(hrs),
            int(mins),
            int(secs),
            self._trailer
        )

    @classmethod
    def from_bytes(cls, octets: bytes) -> 'Observation':
        """ Convert from wireline representation

        :param octets: Packed byte representation of this message
        :return: A decoded message. An exception is thrown if the decoding
                 fails.
        """
        [hdr, ch1m, ch2m, thermt, dispu, ch1v,
         ch2v, hrs, mins, secs, trail] = cls._format.unpack(octets)

        system_time = datetime.now(timezone.utc)

        if hdr != cls._header:
            raise struct.error("bad header")
        if trail != cls._trailer:
            raise struct.error("bad trailer")

        thermocouple_type = ThermocoupleType(thermt & cls._mask_lowbyte_only)
        units = TemperatureUnit(dispu & cls._mask_lowbyte_only)

        channel_temp = [math.nan, math.nan]
        if ch1v & cls._flag_valid:
            channel_temp[0] = float(ch1m) / 10.0
        if ch2v & cls._flag_valid:
            channel_temp[1] = float(ch2m) / 10.0

        meter_time = timedelta(hours=hrs, minutes=mins, seconds=secs)

        return cls(channel_temp=channel_temp, units=units,
                   thermocouple_type=thermocouple_type,
                   system_time=system_time, meter_time=meter_time)

    @classmethod
    def parse_stream(cls, octets: bytes) -> Tuple[List['Observation'], bytes]:
        """ Parse a stream of bytes for Observations

        :param octets: Bytes which contain one or more messages
        :return: Observations and remaining bytes which do not form complete
                 messages
        """
        sze = cls._format.size
        messages = []
        octets = cls._parse_framing(octets)
        while len(octets) >= sze:
            try:
                messages.append(cls.from_bytes(octets[0:sze]))
                octets = octets[sze:]
            except (ValueError, struct.error):
                # if we failed to decode, our framing is off
                octets = cls._parse_framing(octets[1:])
        return messages, octets

    @classmethod
    def _parse_framing(cls, octets: bytes) -> bytes:
        """ Perform message boundary detection

        Serial protocols lack inherent framing---divisions between message
        boundaries. Reads might begin in the middle of a message. This
        method synchronizes to the message boundary by advancing `octets`
        until the start of message is found.

        :param octets: bytes which may contain a message, not necessarily at
               start
        :return: bytes which begin a message, or empty
        """
        while len(octets) >= len(cls._header):
            if octets[0:len(cls._header)] == cls._header:
                return octets
            octets = octets[1:]
        return octets
