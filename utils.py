from ctypes import *
from contextlib import contextmanager
import json
from time import time
from youtubesearchpython import VideosSearch
import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path
import requests
import xmltodict
import glob
load_dotenv(Path(".env"))
weather_key = os.getenv("OPENDATA_GOV_KEY")
# Mute alsa eror message for clean terminal output
# Turn this off when debugging
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
@contextmanager
def mutealsa():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

def get_yt_url(name):
    videosSearch = VideosSearch(name)
    url = videosSearch.result()['result'][0]['id']
    title = videosSearch.result()['result'][0]['title']
    return f"https://www.youtube.com/watch?v={url}", title

def download_yt_audio(url):
    #mp3_cache is a dictionary mapping url to local mp3 file path
    assert isinstance(url, str)
    # Just call a command
    # Clean up cache
    try:
        # os.remove(f'{len(mp3_cache)}.mp3')
        os.remove("download.mp3")
    except FileNotFoundError:
        pass
    #ba: select best audio quality
    #wa: worst
    # filename = f'{len(mp3_cache)}.mp3'
    subprocess.call(["yt-dlp",
                    "-f",
                    "wa",
                    "-x",
                    "--audio-format",
                    "mp3",
                    url,
                    "-o",
                    "download.mp3"])
    assert os.path.isfile("download.mp3"), "download failed"
    return "download.mp3"
def get_cur_location():
    out = subprocess.check_output(['curl', 'ipinfo.io']).decode()
    out = json.loads(out)
    return out["city"]

def get_weather():
    # ref:https://ithelp.ithome.com.tw/articles/10276375
    # this url is linked to current weather data
    city = get_cur_location()
    url = "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0003-001"
    params = {
        "Authorization": weather_key,
        "locationName": city,
    }
    response = requests.get(url, params=params)
    data = xmltodict.parse(response.text)
    print(data["cwbopendata"])


if __name__ == "__main__":
    url, title = get_yt_url('忠明國小校歌')
    print(url, title)
    temp = {}
    download_yt_audio(url,temp)
    