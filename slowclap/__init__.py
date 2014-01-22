#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  detect_claps.py
#  clapper
#

"""
Detect claps using the microphone.
"""

from __future__ import absolute_import, print_function, division

import sys
import optparse
from collections import deque

import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 1.5e7


class Detector(object):
    def __init__(self, feed):
        self.feed = feed

    def __iter__(self):
        for c in self.feed:
            if self.detect(c):
                yield

    def detect(self, chunk):
        # sure, it's a clap, why not? :)
        return True


class WindowDetector(Detector):
    def __iter__(self, feed, n):
        self.q = deque([], n)
        super(WindowDetector, self).__init__(feed)

    def detect(self, chunk):
        self.q.append(chunk)
        return self.detect_window(list(self.q))


class AmplitudeDetector(Detector):
    "Call a sufficiently noisy event a clap."

    def __init__(self, feed, threshold=THRESHOLD):
        super(AmplitudeDetector, self).__init__(feed)
        self.threshold = threshold

    def detect(self, chunk):
        if abs(chunk).sum() > self.threshold:
            return True


class MicrophoneFeed(object):
    def __init__(self):
        self.enabled = True
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                  input=True, frames_per_buffer=CHUNK)

    def __iter__(self):
        while self.enabled:
            data = self.stream.read(CHUNK)
            chunk = np.fromstring(data, 'int16')
            yield chunk

    def close(self):
        self.enabled = False


class VerboseFeed(object):
    def __init__(self, feed):
        self.feed = feed

    def __iter__(self):
        for c in self.feed:
            print('*' * (abs(c).sum() // 500000))
            yield c


def detect_claps():
    feed = MicrophoneFeed()
    feed = VerboseFeed(feed)

    for clap in AmplitudeDetector(feed):
        print('CLAP')


def _create_option_parser():
    usage = \
"""%prog [options]

Detect claps on the default microphone."""  # nopep8

    parser = optparse.OptionParser(usage)

    return parser


def main():
    argv = sys.argv[1:]
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if args:
        parser.print_help()
        sys.exit(1)

    try:
        detect_claps(*args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
