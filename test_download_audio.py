# Just call a command
import subprocess
import os
try:
    os.remove("download.mp3")
except FileNotFoundError:
    pass
#ba: select best audio quality
#wa: worst
subprocess.call(["yt-dlp",
                "-f",
                "wa",
                "-x",
                "--audio-format",
                "mp3",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "-o",
                "download.mp3"])
assert os.path.isfile("download.mp3")