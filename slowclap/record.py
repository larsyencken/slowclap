#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  record.py
#  clapper
#

"""
Record an audio sample.
"""

from __future__ import absolute_import, print_function, division

import sys
import optparse
import wave

import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def record(output_file, seconds):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

        sys.stdout.write('.')
        sys.stdout.flush()

    print("\n* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def _create_option_parser():
    usage = \
"""%prog [options] output.wav

Record audio on the default microphone."""  # nopep8

    parser = optparse.OptionParser(usage)
    parser.add_option('-s', action='store', dest='seconds', default=5,
                      type='int', help='Number of seconds to record')

    return parser


def main(argv):
    parser = _create_option_parser()
    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    record(*args, seconds=options.seconds)


if __name__ == '__main__':
    main(sys.argv[1:])
