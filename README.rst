slowclap
========

Detect a clap using your computer's microphone, and take some action. Uses a live microphone feed based on the PyAudio frontend for PortAudio.

Status: *working*

Installing
----------

You need portaudio installed, then you can install the latest version pip::

    sudo pip install slowclap

It will pull in pyaudio and numpy depenencies.

Usage
------

Command-line
~~~~~~~~~~~~

With default settings, run a shell command of your choosing each time a clap is detected::

    slowclap --exec='echo Clap'

You might need to tune the threshold to your mic with the ``-t`` option.

Python API
~~~~~~~~~~

Set up a simple detection loop::

    import slowclap as sc
    feed = sc.MicrophoneFeed()
    detector = sc.AmplitudeDetector(feed, threshold=17000000)
    for clap in detector:
        # do something
        print(clap.time)

Changelog
---------

v0.1.0
~~~~~~

- Working amplitude clapper
- Supports command-execution and rate-limiting
