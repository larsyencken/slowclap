#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  clapper-demo.py
#  clapper
#

"""
Using a clapper process to detect SimpleCV.
"""

import sys
import optparse
from collections import deque
import multiprocessing as mp

import pyaudio
import numpy as np
import SimpleCV
import pygame

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def clapper():
    state = mp.Value('i', 0)
    p = mp.Process(target=detect_clap, args=(state,))
    p.start()

    disp = SimpleCV.Display((1024, 768), flags=pygame.FULLSCREEN)
    cam = SimpleCV.Camera()
    while disp.isNotDone():
        img = cam.getImage()
        img = img.toGray() if state.value else img
        img.save(disp)

        if disp.lastLeftButton:
            break


def detect_clap(state):
    p = pyaudio.PyAudio()
    q = deque([], 3)
    bucket = deque([], 3 * RATE / CHUNK)

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
            state.value = (state.value + 1) % 2
            bucket.append(1)
        else:
            bucket.append(0)

    stream.stop_stream()
    stream.close()
    p.terminate()


def _create_option_parser():
    usage = \
"""%prog [options]"""  # nopep8

    parser = optparse.OptionParser(usage)

    return parser


def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if len(args) != 0:
        parser.print_help()
        sys.exit(1)

    clapper(*args)


if __name__ == '__main__':
    main(sys.argv[1:])
