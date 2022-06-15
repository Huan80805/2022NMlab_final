#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import readline
from gtts import gTTS
from audio import AudioOutput
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--output-device", default=None, type=str, help='output audio device to use')
args = parser.parse_args()
print(args)
gtts_sample_rate = 24000
# open output audio device
if args.output_device:
    audio_device = AudioOutput(args.output_device, sample_rate=gtts_sample_rate)

while True:
    print(f'\nEnter text, or Q to quit:')
    text = input('> ')
    if text.upper() == 'Q':
        sys.exit()
    print('')
    start = time.perf_counter()
    audio = gTTS(text=text, lang="zh-TW")
    stop = time.perf_counter()
    latency = stop-start
    # duration = audio.shape[0]/tts.sample_rate
    # print(f"Run {run} -- Time to first audio: {latency:.3f}s. Generated {duration:.2f}s of audio. RTFx={duration/latency:.2f}.")
    # output the audio
    if args.output_device:
        audio_device.write(audio)