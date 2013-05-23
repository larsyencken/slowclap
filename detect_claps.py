#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  detect_claps.py
#  clapper
#

"""
Detect claps using the microphone.
"""

import time
import sys
import optparse
from collections import deque

import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def detect_claps():
    p = pyaudio.PyAudio()
    q = deque([], 3)
    bucket = deque([], 10)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        data = np.fromstring(data, 'int16')
        q.append(abs(data).sum())
        if sum(q) > 1.5e7 and not sum(bucket):
            print time.time(), 'clap'
            bucket.append(1)
        else:
            bucket.append(0)


def _create_option_parser():
    usage = \
"""%prog [options]

Detect claps on the default microphone."""  # nopep8

    parser = optparse.OptionParser(usage)

    return parser


def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if args:
        parser.print_help()
        sys.exit(1)

    detect_claps(*args)


if __name__ == '__main__':
    main(sys.argv[1:])
