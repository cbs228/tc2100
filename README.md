# TC2100 Thermometer Interface

> Receive measurements from your TC2100 or other compatible digital thermometer
> over USB.

## Motivation

The TC2100 is a digital thermometer which supports

* two simultaneous measurement channels; and
* seven standard types of thermocouples.

Although it is usable as a standalone meter, it also includes a USB interface
for real-time computer output.

The manufacturer provides software for the USB interface. *This is not it.*
This is unsupported, third-party software which was developed by reverse
engineering.

The `tc2100` module is a python 3.9 software development kit for receiving
real-time temperature measurements. It includes a console script, `tc2100dump`,
for logging measurements to [csv](https://docs.python.org/3.6/library/csv.html)
files.

## Supported Devices

At present, only one device is supported by this module.

| Name                   | Vendor ID (hex)  | Product ID (hex)  |
|------------------------|------------------|-------------------|
| TC2100                 | `10c4`           | `ea60`            |

Other devices have not been tested and are unlikely to work. If you have another
device which works, open a bug report and ask that it be added to this table.

## The Fine Print

In case you missed it above, this project is not affiliated with the original
manufacturer(s). To our knowledge, the telemetry format is not specified in any
[other] public documents. It has been reverse-engineered without assistance or
support from the manufacturer. Read the
[license](https://github.com/cbs228/tc2100/blob/master/LICENSE) carefully, as
it may affect your rights. There is no warranty.

*Use of these programs in safety-critical applications is strongly discouraged.*

## Installation

```bash
pip3 install tc2100
```

This module requires [twisted](http://twistedmatrix.com/) and
[pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html). The pip
package will automatically install these dependencies.

## Quick Start

Using the supplied USB cable, connect a TC2100 thermometer to your computer.
Hold down the "`PC-Link`" button until the meter beeps and the "`USB`" indicator
illuminates. Then run:

```bash
tc2100dump --out temperatures.csv
```

If you receive "`permission denied`" errors on Linux, you need to grant your
user account permission to use serial devices. On most distributions, including
Ubuntu and CentOS, this can be accomplished by adding yourself to the `dialout`
group:

```bash
sudo usermod -a -G dialout "$USER"
```

Once you perform the above modification, you will need to log out and log back
in again. Never run this program as root!

When running `tc2100dump`, you may omit the `--out` argument to write
measurements to standard output. You may also call this module as an executable
with

```bash
python3 -m tc2100 --out temperatures.csv
```

The script will attempt to auto-detect the correct port for your thermometer.
If auto-detection fails, you may specify the port manually:

```bash
tc2100dump --port /dev/ttyUSB0 --out temperatures.csv
```

If the script detects your thermometer, but no data is printed, check to make
sure you have pressed the "`PC-Link`" button and that the "`USB`" indicator
is illuminated.

## Development Status

This module is likely *feature-complete*. It does what I need it to do, and
additional features are not planned. Bug reports which are broadly categorized
as feature requests will probably be rejected. I am also unable to support the
inclusion of additional devices—even similar ones.

If you observe inconsistencies or other issues with the telemetry output, and
can identify them, please submit a bug report. If able, please include a capture
of the serial data stream and the expected behavior with your report.

Pull requests within the scope of this project are welcome, especially if they
fix bugs. Please ensure that your PRs include tests and pass the included `tox`
checks.

## Technical Details

The TC2100 incorporates a UART-to-USB chipset, which emulates a serial port over
USB. When plugged in, most computers will automatically detect it as a serial
port, like `/dev/ttyUSB0` or `COM1`. No additional drivers are required.

The thermometer has a USB vendor ID of `0x10c4` and a product ID of `0xea60`.
The meter's serial adapter uses `9600` baud with the common `8N1` format: eight
data bits, no parity, and one stop bit.

Once the "PC Link" button is pressed, updates begin to stream immediately, at
regular intervals. Each update is an 18 byte packet which begins with the hex
bytes `b"\x65\x14"` and ends with a CRLF (`b"\x0d\x0a"`). Multi-byte quantities
are sent `big endian`.

This is an example update, in hex:

```
65 14 00 00 00 00 8D 09 0C 01 81 88 40 00 02 05 0D 0A
```

Bytes are decoded as follows:

| Offset (dec)  | C Type        | Description                     |
|---------------|---------------|---------------------------------|
| 0             | `uint8[2]`    | Header                          |
| 2             | `uint8[3]`    | Unknown—always zeros            |
| 5             | `int16`       | Channel 1 measurement           |
| 7             | `int16`       | Channel 2 measurement           |
| 9             | `uint8`       | Thermocouple type, other data   |
| 10            | `uint8`       | Display unit, other data        |
| 11            | `uint8`       | Channel 1 flags                 |
| 12            | `uint8`       | Channel 2 flags                 |
| 13            | `uint8`       | Hours                           |
| 14            | `uint8`       | Minutes                         |
| 15            | `uint8`       | Seconds                         |
| 16            | `uint8[2]`    | CRLF                            |

* The update message cannot be expressed as a C struct, as it lacks the proper
  alignment.
* Measurement **values** are
  - expressed in tenths of degrees
  - in sign-magnitude format. The sign bit is part of the flag bytes (11 and 12)
  - expressed in the same units as the thermometer is set to display. Byte 10
    indicates the unit of measure.
* Channel **flags** are OR'd together:
  - Valid measurement: `0x08`
  - Invalid measurement: `0x40`. Channels which do not have a thermocouple
    connected will have this flag.
  - Negative measurement: `0x80`
* The thermocouple **type** and temperature **units** are stored in the least
  significant nibble of those bytes. The upper nibble contains other data.

The above measurement is in degrees Celsius. The channel 1 measurement is
`-14.1 °C`, and the channel 2 measurement is invalid.

Further details are included in the python class `tc2100.Observation`. Unit
tests include more sample data.

----

License - [MIT](https://github.com/cbs228/tc2100/blob/master/LICENSE)
