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
from collections import deque, namedtuple
import subprocess

import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 1.5e7

Chunk = namedtuple('Chunk', 'data time')
Clap = namedtuple('Clap', 'time')


class Detector(object):
    def __init__(self, feed):
        self.feed = feed

    def __iter__(self):
        for c in self.feed:
            if self.detect(c):
                yield Clap(c.time)

    def detect(self, chunk):
        # sure, it's a clap, why not? :)
        return True


class WindowDetector(Detector):
    def __iter__(self, feed, n):
        self.q = deque([], n)
        super(WindowDetector, self).__init__(feed)

    def detect(self, chunk):
        self.q.append(chunk.data)
        return self.detect_window(list(self.q))


class AmplitudeDetector(Detector):
    "Call a sufficiently noisy event a clap."

    def __init__(self, feed, threshold=THRESHOLD):
        super(AmplitudeDetector, self).__init__(feed)
        self.threshold = threshold

    def detect(self, chunk):
        if abs(chunk.data).sum() > self.threshold:
            return True


class MicrophoneFeed(object):
    def __init__(self):
        self.enabled = True
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                                  input=True, frames_per_buffer=CHUNK)
        self.t = 0.0

    def __iter__(self):
        while self.enabled:
            data = self.stream.read(CHUNK)
            chunk = np.fromstring(data, 'int16')
            yield Chunk(chunk, self.t)
            self.t += CHUNK / RATE

    def close(self):
        self.enabled = False


class VerboseFeed(object):
    def __init__(self, feed):
        self.feed = feed

    def __iter__(self):
        for c in self.feed:
            print('*' * (abs(c.data).sum() // 500000))
            yield c


class RateLimitedDetector(Detector):
    def __init__(self, d, rate_limit=1):
        self.child = d
        self.last_clap = -rate_limit
        self.rate_limit = rate_limit

    def __iter__(self):
        for clap in self.child:
            if clap.time - self.last_clap > self.rate_limit:
                self.last_clap = clap.time
                yield clap


def detect_claps(once=False, verbose=False, command=None, threshold=THRESHOLD,
                 rate_limit=1):
    feed = MicrophoneFeed()

    if verbose:
        feed = VerboseFeed(feed)

    detector = AmplitudeDetector(feed, threshold)

    if rate_limit > 0:
        detector = RateLimitedDetector(detector, rate_limit)

    for clap in detector:
        if verbose:
            print('=== CLAP ===')

        if command:
            subprocess.Popen(command,
                             shell=True,
                             stdin=open('/dev/stdin'),
                             stdout=sys.stdout,
                             stderr=sys.stderr)

        if once:
            feed.close()


def _create_option_parser():
    usage = \
"""%prog [options]

Detect claps on the default microphone."""  # nopep8

    parser = optparse.OptionParser(usage)
    parser.add_option('--once', action='store_true',
                      help='Stop after one clap')
    parser.add_option('--exec', action='store', dest='command',
                      help='Execute command on clap')
    parser.add_option('-v', '--verbose', action='store_true',
                      help='Print the stream of volume recorded')
    parser.add_option('-t', '--threshold', action='store',
                      type='int', default=THRESHOLD,
                      help='The volume threshold for a clap'
                      '[{0}]'.format(THRESHOLD))
    parser.add_option('-r', '--rate-limit', action='store', dest='rate_limit',
                      type='float', default=1,
                      help='Mininum time in seconds before a new clap is '
                      'detected [1]')

    return parser


def main():
    argv = sys.argv[1:]
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if args:
        parser.print_help()
        sys.exit(1)

    try:
        detect_claps(once=options.once,
                     command=options.command,
                     verbose=options.verbose,
                     threshold=options.threshold,
                     rate_limit=options.rate_limit)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
