#!/usr/bin/env python
from __future__ import print_function

import sys
import wave
import alsaaudio
import scipy.io.wavfile as wavfile
import serial
import threading
import time

cmd = [0, 0, 0, 0]

def read_from_port(ser):
    global cmd
    ser.flush()
    while True:
        line = ser.readline()
        if len(line) > 0:
            cmd = [0, 0, 0, 0]
            for i, tmp in enumerate(line.split(' ')):
                try:
                    cmd[i] = (cmd[i] + float(tmp)/1024) / 2
                except ValueError:
                    cmd[i] = cmd[i] / 2

if __name__ == '__main__':
    rate, track1 = wavfile.read('1.wav')
    rate, track2 = wavfile.read('2.wav')
    rate, track3 = wavfile.read('3.wav')
    rate, track4 = wavfile.read('4.wav')
    track1 = track1.astype('float32')
    track2 = track2.astype('float32')
    track3 = track3.astype('float32')
    track4 = track4.astype('float32')
    frame_length = min([len(track1), len(track2), len(track3), len(track4)])

    ser = serial.Serial('/dev/ttyACM0', timeout=0.5)

    device = alsaaudio.PCM(device='default')
    device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    device.setchannels(2)
    device.setrate(rate)
    device.setperiodsize(320)

    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
    thread.start()

    while True:
        start = 0
        while start + 320 <= frame_length:
            cut = slice(start, start+320)
            portion = [0.5, 5, 7, 2]
            music = ((portion[0] * cmd[0] * track1[cut] +
                      portion[1] * cmd[1] * track2[cut] +
                      portion[2] * cmd[2] * track3[cut] +
                      portion[3] * cmd[3] * track4[cut])
                     /sum(portion)).astype('int16')
            device.write(music)
            start += 320
