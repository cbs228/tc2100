""" Temperature observation message """

import enum
import math
from struct import Struct
from datetime import datetime
from datetime import timezone
from typing import Tuple, NamedTuple


@enum.unique
class TemperatureUnit(enum.IntEnum):
    """ A unit of temperature

    .. py:attribute:: C

       Degrees Celsius

    .. py:attribute:: F

       Degrees Fahrenheit

    .. py:attribute:: K

       Kelvin
    """

    C = 1
    F = 2
    K = 3

    def __str__(self):
        return str(self.name)


@enum.unique
class ThermocoupleType(enum.IntEnum):
    """ A type of thermocouple

    .. py:attribute:: K

       K Type

    .. py:attribute:: J

       J Type

    .. py:attribute:: T

       T Type

    .. py:attribute:: E

       E Type

    .. py:attribute:: R

       R Type

    .. py:attribute:: S

       S Type

    .. py:attribute:: N

       N Type
    """

    K = 1
    J = 2
    T = 3
    E = 4
    R = 5
    S = 6
    N = 7

    def __str__(self):
        return str(self.name)


class MeterTime(NamedTuple):
    """ Elapsed time indication from the thermometer

    The TC2100 represents time as ``hours : minutes : seconds`` from
    boot-up. The maximum representable time is ``255:59:59``. `MeterTime`
    objects are immutable.

    .. py:attribute:: hours

        Elapsed time since meter bootup, in hours

    .. py:attribute:: minutes

        Elapsed time since meter bootup, in minutes

    .. py:attribute:: seconds

        Elapsed time since meter bootup, in seconds
    """
    hours: int
    minutes: int
    seconds: int

    _format = Struct("!3B")

    def __str__(self):
        return f"{self.hours:03d}:{self.minutes:02d}:{self.seconds:02d}"

    def to_bytes(self) -> bytes:
        """ Convert to wireline representation

        :return: Packed byte representation of this MeterTime
        """
        return self._format.pack(self.hours, self.minutes, self.seconds)

    @classmethod
    def from_bytes(cls, octets: bytes) -> 'MeterTime':
        """ Convert from wireline representation

        :param octets: Packed byte representation of this message
        :return: A decoded time. An exception is thrown if the decoding
                 fails.
        """
        return MeterTime(*cls._format.unpack(octets))

    @classmethod
    def size(cls) -> int:
        """ Get packed size of this message

        :return: Size of the packed bytes generated by
                 :py:meth:`MeterTime.to_bytes`
        """
        return cls._format.size


class Observation(NamedTuple):
    """ Temperature observation message from the thermometer

    Observations are time-tagged in Python, using the current value of the
    system's real-time clock, when they are converted :py:meth:`from_bytes()`.
    Otherwise, an Observation contains only data output by the thermometer.

    .. py:attribute:: system_time

        Time, according to the system clock, when this Observation was
        de-serialized. Always a timezone-aware `datetime` in the UTC time zone.

    .. py:attribute:: meter_time

        Time, according to the meter, that the temperature measurement was
        taken.

    .. py:attribute:: thermocouple_type

        Thermocouple type used to make this measurement.

    .. py:attribute:: unit

        The TC2100 outputs temperature in the units that it was configured to
        display. This field represents the temperature units for the
        :py:meth:`temperatures`.

    .. py:attribute:: temperature_ch1

        Temperature value on channel 1, or `math.nan` if the measurement is
        not valid.

    .. py:attribute:: temperature_ch2

        Temperature value on channel 2, or `math.nan` if the measurement is
        invalid.
    """

    system_time: datetime or None
    meter_time: MeterTime or None
    thermocouple_type: ThermocoupleType or str
    unit: TemperatureUnit or str
    temperature_ch1: float
    temperature_ch2: float

    _num_channels = 2
    _flag_valid = 0x08
    _flag_invalid = 0x40
    _flag_negative = 0x80
    _invalid_placeholder = -32768
    _mask_lowbyte_only = 0x0F
    _units_highbyte = 0x80
    _tzero = MeterTime(0, 0, 0)
    _format = Struct(
        "!"
        "2h"    # measurements, in tens of display units
        "B"     # thermocouple type (enumerated)
        "B"     # display unit (enumerated)
        "2B"    # channel validity / status flags
    )

    @property
    def temperatures(self) -> Tuple[float, float]:
        """ Obtain all temperature measurements

        :return: Temperature measurements from each channel
        """
        return self.temperature_ch1, self.temperature_ch2

    def as_dict(self) -> dict:
        """ Convert to dict

        :return: This Observation, expressed as a mutable dict.
        """
        return self._asdict()  # pylint: disable=no-member

    def to_bytes(self) -> bytes:
        """ Convert to wireline representation

        The conversion will be lossy if, for example, the channel temperatures
        are not evenly divisible by 0.1.

        :return: Packed byte representation of this Observation
        """
        out_fields = []
        out_fields.extend([self._encode_temperature_value(v)
                           for v in self.temperatures])
        if isinstance(self.thermocouple_type, str):
            thermtype = ThermocoupleType[self.thermocouple_type]
        else:
            thermtype = self.thermocouple_type
        out_fields.append(int(thermtype))

        if isinstance(self.unit, str):
            unit = TemperatureUnit[self.unit]
        else:
            unit = self.unit
        out_fields.append(int(unit) | 0x80)

        out_fields.extend([self._encode_temperature_flag(v)
                           for v in self.temperatures])

        meter_time = self.meter_time or self._tzero
        return self._format.pack(*out_fields) + meter_time.to_bytes()

    @classmethod
    def from_bytes(cls, octets: bytes) -> 'Observation':
        """ Convert from wireline representation

        :param octets: Packed byte representation of this message
        :return: A decoded message. An exception is thrown if the decoding
                 fails.
        """
        meter_time = MeterTime.from_bytes(octets[-3:])
        decode = cls._format.unpack(octets[0:-3])
        therm_type = ThermocoupleType(decode[2] & cls._mask_lowbyte_only)
        display_unit = TemperatureUnit(decode[3] & cls._mask_lowbyte_only)
        temperatures = [cls._decode_temperature(decode[i], decode[i + 4])
                        for i in range(0, cls._num_channels)]
        return Observation(datetime.now(timezone.utc),
                           meter_time,
                           therm_type,
                           display_unit,
                           temperatures[0],
                           temperatures[1])

    @classmethod
    def size(cls) -> int:
        """ Get packed size of this message

        :return Size of the packed byte representation of an Observation,
                as generated by :py:meth:`Observation.to_bytes`
        """
        return cls._format.size + MeterTime.size()

    @classmethod
    def field_names(cls) -> Tuple:
        """ Get all field names

        :return Field names of an Observation, in an order suitable for
                writing to a CSV file
        """
        return cls._fields

    @classmethod
    def _decode_temperature(cls, value, valid_flag) -> float:
        if valid_flag & cls._flag_valid:
            val = float(value) / 10.0
            if valid_flag & cls._flag_negative:
                val = -val
            return val
        return math.nan

    @classmethod
    def _encode_temperature_value(cls, temperature) -> int:
        if not math.isfinite(temperature):
            return cls._invalid_placeholder
        return int(math.fabs(temperature) * 10)

    @classmethod
    def _encode_temperature_flag(cls, temperature) -> int:
        if not math.isfinite(temperature):
            return cls._flag_invalid

        flag = cls._flag_valid
        if temperature < 0:
            flag |= cls._flag_negative
        return flag
