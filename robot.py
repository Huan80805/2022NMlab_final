from audio import AudioOutput
from gtts import gTTS
from chat import ChatBot
import logging
import time
from asr import Hearing
from player import Player
from utils import get_yt_url, download_yt_audio
from datetime import datetime
from trt_pose_hand.client import get_gesture
from youtubesearchpython import VideosSearch
import sys
# # list audio devices
# if args.list_devices:
#     list_audio_devices()
#     sys.exit()
##########################################################
from Weather import *

class Robot():
    def __init__(self, asr_model="quartznet", mic='11', speaker='11', language='zh-TW'):
        self.in_device = mic
        self.out_device = speaker
        self.language = language
        # Move audio input stream into Hearing
        # supported language: https://cloud.google.com/speech-to-text/docs/languages
        self.hearing = Hearing(device=self.in_device, 
                            sample_rate=44100, 
                            chunk_size=int(44100/10),
                            language=self.language)
        # self.out_stream is defined for chatbot only
        self.out_stream = AudioOutput(device=self.out_device)
        self.chatbot = ChatBot(language=self.language)
        # Define keyword, and corresponding response for different operations
        if self.language == 'zh-TW':
            self.keyword = {
                'music': [['播','放'],['音樂']],
                'stream': [['開'], ['直播']],
                'weather': ['天氣'],
                'time': [['現在'],['時間', '幾點']]
            }
            self.response = {
                'music': ['你想要播什麼歌', '正在網路上搜尋並準備播放'],
                'stream': ['正在youtube上開啟直播'],
                'weather': ['請問要查詢哪裡的天氣', '請稍後，正在為您查詢']
            }
        elif self.language == 'en-US':
            self.keyword = {
                'music': [['play', 'hear'],['music']],
                'stream': ['stream'],
                'weather': ['weather'],
                'time': [['now', 'current', 'what'],['time']]
            }
            self.response = {
                'music': ['what song do you want play?','Searching on youtube and preparing to play'],
                'stream': ['opening a live streaming on youtube'],
            }
        self.mode = 'HEARING'
        print('----------ROBOT IS NOW READY---------')
    
    def set_lang(self, lang):
        #TODO: set_language, enable users switching language
        #Redefine keyword, response, asr, tts, chat model?
        return
    def hear(self):
        # Avoid Robot speaking while listening
        self.hearing.stream.listening = True
        transcript = self.hearing.hear()
        self.hearing.stream.listening = False
        print(transcript)
        return transcript
    def speak(self, text):
        print(text)
        audio = gTTS(text=text, lang=self.language)
        self.out_stream.write(audio)
    
    def chat(self, text):
        return self.chatbot.get_response_text(text=text)

    def play_song(self):
        self.speak(self.response['music'][0])
        text = self.hear()
        # Rule-based just for now
        song = text.lower().split("play")[-1]
        self.speak(self.response['music'][1]+song)
        # Release out_stream
        # TODO, unify two out_stream?
        self.out_stream.close()
        url = get_yt_url(name=song)
        fp = download_yt_audio(url)
        player = Player(filepath=fp)
        # another thread
        player.start()
        # handle hand-pose tracking here
        # pan, stop, fist, peace
        while not player.closed:
            gesture = get_gesture()
            print(gesture)
            if KeyboardInterrupt:
                break
            # do gesture-related operation
        
        player.stop()
        self.out_stream = AudioOutput(device=self.out_device)
    
    def get_weather(self):
        self.speak(self.response['weather'][0])
        city = self.hear()
        print(f'___搜尋{city}___')
        self.speak(self.response['weather'][1])
        return search_weather(city)
        
    def get_time(self):
        now = datetime.now()
        if self.language == 'zh-TW':
            current_time = now.strftime("%H點%M分%S秒")
        else:
            current_time = now.strftime('%H O\'clock %M minute and %Seconds')
        return current_time
    def run(self):
        while True:
            text = self.hear()
            # playing music mode
            if any(word in text.lower() for word in self.keyword['music'][0]) and\
                any(word in text.lower() for word in self.keyword['music'][1]):
                self.play_song()
            elif any(word in text.lower() for word in self.keyword['time'][0]) and\
                any(word in text.lower() for word in self.keyword['time'][1]):
                current_time = self.get_time()
                self.speak(current_time) 
            # search weather mode
            elif any(word in text.lower() for word in self.keyword['weather'][0]):
                weather_ans = self.get_weather()
                self.speak(weather_ans)
            # chat mode
            else:
                response = self.chat(text)
                self.speak(response)
                
                


if __name__ == "__main__":
    robot = Robot()
    robot.run()



                
