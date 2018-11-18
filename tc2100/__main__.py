"""
Dump TC2100 temperature readings to CSV
"""

import argparse
import sys
from typing import TextIO

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

from tc2100.protocol import ThermometerToCSVProtocol
from tc2100.version import __version__ as version


_application_name = 'tc2100dump'


def main():
    """ Run the program """
    parser = get_arg_parser()
    args = parser.parse_args()
    if args.version:
        print(version_string())
        sys.exit(0)

    run_dump_to_csv(args.port, args.out)


def get_arg_parser() -> argparse.ArgumentParser:
    """ Obtain the argparse for the executable

    :return: Argument parser
    """
    parser = argparse.ArgumentParser(
        description="Dump values from a digital thermometer")
    parser.add_argument("--port", type=str, required=False,
                        help="Path to serial port, like /dev/ttyUSB0 or COM1")
    parser.add_argument("--out", type=str, required=False,
                        help="Output file. Use '-' for stdout.")
    parser.add_argument("--version", action='store_true',
                        help="Print version and exit")

    return parser


def run_dump_to_csv(port: str, file_name: str = None):
    """ Connect to a TC2100 and dump its output to a file

    :param port: Serial port
    :param file_name: Destination file
    :return: Zero on success, or non-zero for error
    """

    if not file_name or file_name == '-':
        _run_dump(port, sys.stdout)
        return

    with open(file_name, mode='w', newline='') as outfile:
        _run_dump(port, outfile)


def version_string() -> str:
    """ Obtain a version string for this executable

    :return Version string
    """
    return "%s version %s" % (_application_name, version)


def _run_dump(port: str, file_handle: TextIO) -> None:
    SerialPort(ThermometerToCSVProtocol(file_handle=file_handle),
               port, reactor, baudrate=9600)
    reactor.run()


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
