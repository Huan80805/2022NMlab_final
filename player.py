# Test functionality of playing music
# Ref:https://stackoverflow.com/questions/26673746/
# TODO:
# Read audio from any file extension
from email.mime import audio
from math import ceil
from pydub import AudioSegment
import os
import threading
import pyaudio
from utils import mutealsa, get_yt_url,download_yt_audio
import time
from audio import AudioOutput
class Player(threading.Thread):
    # Run player in a multithread
    # enable real-time modification on audio
    def __init__(self, filepath, sample_rate=44100, volume=70):
        super(Player, self).__init__()
        self.filepath = os.path.abspath(filepath)
        assert os.path.isfile(self.filepath)
        self.sample_rate = sample_rate # unify sample rate for device interface
        self.chunk_size = int(self.sample_rate/10)
        filename, format = os.path.splitext(filepath)
        self.segment = AudioSegment.from_file(self.filepath, format=format.strip('.')).set_frame_rate(self.sample_rate)
        self.volume = volume
        self.time = 0
        self.closed = True
        self.paused = False

    def callback(self, in_data, frame_count, time_info, status):
        # This is where output stream reads data
        # get frame_count samples
        # control volume here
        # span must be integer even without int()
        span = int(1/self.sample_rate*frame_count*1000)
        assert span/1000/frame_count*self.sample_rate == 1, "modify sample_rate and chunk_size or audio may be choppy"
        self.time += span
        while self.paused:
            # when pausing not sending anything to outstream
            continue
        samples = self.segment[self.time: self.time+span] - (60 - (60 * (self.volume/100.0)))
        return (samples._data, pyaudio.paContinue)

    def run(self):
        try:
            # Open an audio segment
            self.closed = False
            with mutealsa():
                player = pyaudio.PyAudio()
            stream = player.open(format = player.get_format_from_width(self.segment.sample_width),
                channels = self.segment.channels,
                rate = self.segment.frame_rate,
                output_device_index = 11,
                output = True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.callback)

            stream.start_stream()
            duration = self.segment.duration_seconds
            while self.time <= duration*1000 and not self.closed:
                continue
            # automatically shut down once music ends
        except KeyboardInterrupt:
            stream.close()
        stream.stop_stream()
        stream.close()

    def play(self):
        # Just another name for self.start()
        # Call thread.start
        self.start()

    def stop(self):
        self.closed = True

    def pause(self, status):
        assert type(status) == type(True)
        self.paused = status


if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser(add_help=True, description="Play a file continously, and exit gracefully on signal")
    # parser.add_argument('--audio_file', type=str, help='The Path to the audio file (mp3, wav and more supported)')
    # args = parser.parse_args()
    # player = Player(args.audio_file)
    # player.play()
    # time.sleep(5)
    # player.volume = 150
    # time.sleep(5)
    # player.volume = 100
    # time.sleep(5)
    # player.pause(True)
    # time.sleep(5)
    # player.pause(False)
    # time.sleep(5)
    # player.stop()
    # #test reopening outputstream
    # out_stream = AudioOutput(device='11')

    url, title = get_yt_url('PTT')
    download_yt_audio(url)
    player = Player("download.mp3")
    player.start()
    time.sleep(20)
    player.stop()
    