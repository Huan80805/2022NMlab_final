from logging import exception
from audio import AudioOutput
from gtts import gTTS
from chat import ChatBot
from asr import Hearing
from player import Player
from utils import get_yt_url, download_yt_audio
from datetime import datetime
from trt_pose_hand.client_player import Client_Player
from trt_pose_hand.client_camera import Client_Cam
from multiprocessing import Process
import multiprocessing
import time
import sys
import os
# # list audio devices
# if args.list_devices:
#     list_audio_devices()
#     sys.exit()
##########################################################
from Weather import search_weather

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
                'time': [['現在'],['時間', '幾點']],
                'on': ['開機','關機']
            }
            self.response = {
                'music': ['你想要播什麼歌', '正在網路上搜尋', '找到最相符的影片並準備下載', 
                '在local端找到','下載失敗你可能要換個關鍵字'],
                'stream': ['正在youtube上開啟直播'],
                'weather': ['請問要查詢哪裡的天氣', '請稍後，正在為您查詢'],
                'on': ['你好,有什麼需要為您服務的嗎, 你可以播放音樂,搜尋天氣,查詢時間，也可以單純跟我對話',
                    '關機中,若需要重新啟動請說開機']
            }
        elif self.language == 'en-US':
            self.keyword = {
                'music': [['play', 'hear'],['music']],
                'stream': ['stream'],
                'weather': ['weather'],
                'time': [['now', 'current', 'what'],['time']],
                'on': ['turn on', 'turn off']
            }
            self.response = {
                'music': ['what song do you want play?','Searching on youtube by keyword ', 
                'I found the most relevant video: '],
                'stream': ['opening a live streaming on youtube'],
                'on': ['hi, anything i can help you with? i can play music, searching for weather, time,\
                    or you can chat with me too', 'shuting down, to reboot please say turn on']
            }
        #Open a process to iteratively send cam data
        # client_cam = Process(target=Client_Cam)
        # client_cam.start()
        self.mode = 'HEARING'
        # manager = multiprocessing.Manager()
        # self.mp3_cache = manager.dict()
        self.on = False
    
    def set_lang(self, lang):
        #TODO: set_language, enable users switching language
        #Redefine keyword, response, asr, tts, chat model?
        return
    def hear_loop(self):
        # Avoid Robot speaking while listening
        # loop to escape timeout error
        self.hearing.stream.listening = True
        transcript = self.hearing.hear()
        self.hearing.stream.listening = False
        return transcript
    def hear(self):
        transcript = None
        while transcript == None:
            try:
                transcript = self.hear_loop()
            except KeyboardInterrupt:
                sys.exit()
            # except:
            #     transcript = None
        print(transcript)
        return transcript
    def speak(self, text):
        print(text)
        audio = gTTS(text=text, lang=self.language)
        self.out_stream.write(audio)
    
    def chat(self, text):
        return self.chatbot.get_response_text(text=text)

    def play_song(self):
        mode = None
        while mode == None:
            self.speak("請選擇控制音樂的方式： 語音或手勢")
            text = self.hear()
            if "語音" in text:
                self.speak("選擇用語音控制音樂"+self.response['music'][0])
                mode = 'voice'
            elif "手" in text or "首飾" in text: 
                self.speak("選擇用手勢控制音樂"+self.response['music'][0])
                mode = 'hand_pose'
            else:
                self.speak("目前只支持語音或手勢")
        text = self.hear()
        song = text.lower().split("play")[-1]
        url, title = get_yt_url(name=song)
        # Release out_stream
        # TODO, unify two out_stream?
        # Download music
        try:
            p = Process(target=download_yt_audio, args=(url,))
            p.start()
            self.speak(self.response['music'][1]+song)
            self.speak(self.response['music'][2]+title)
            self.out_stream.close()
            p.join()
        except:
            self.speak(self.response['music'][4])
        if mode == 'hand_pose':        
            # TODO, change filepath here by keyword
            player = Player(filepath="download.mp3")
            # another thread
            player.start()
            # handle hand-pose tracking here
            # pan, stop, fist, peace
            player_client = Client_Player()
            player_client.init_conn()
            while not player.closed:
                try:
                    gesture = player_client.get_gesture()
                    print(gesture)
                    if gesture == "stop":
                        player.stop()
                    elif gesture == "peace" and not player.paused:
                        player.pause(True)
                    elif gesture == "pan" and player.paused:
                        player.pause(False)
                    elif gesture == "ok":
                        player.volume = max(50, player.volume-5)
                    elif gesture == "fist":
                        player.volume = min(90, player.volume+5)
                    else:
                        pass
                    time.sleep(5)
                except KeyboardInterrupt:
                    break
            player_client.end_conn()
            player.stop()
            self.out_stream = AudioOutput(device=self.out_device)
        else:
            # TODO, change filepath here by keyword
            player = Player(filepath="download.mp3")
            # another thread
            player.start()
            while not player.closed:
                try:
                    text = self.hear()
                    if "停止" in text:
                        player.stop()
                    if "暫停" in text and not player.paused:
                        player.pause(True)
                    elif ("播" in text or "放" in text) and player.paused:
                        player.pause(False)
                    elif "大" in text:
                        player.volume = min(90, player.volume+10)
                        print(player.volume)
                    elif "小" in text:
                        player.volume = max(50, player.volume-10)
                        print(player.volume)
                    else:
                        pass
                except KeyboardInterrupt:
                    break
            player.stop()
            self.out_stream = AudioOutput(device=self.out_device)
            


    
    def get_weather(self, city):
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
            try:
                text = self.hear()
                if self.on:
                    if self.keyword["on"][1] in text.lower():
                        self.on = False
                        self.speak(self.response['on'][1])
                    # playing music mode
                    elif any(word in text.lower() for word in self.keyword['music'][0]) and\
                        any(word in text.lower() for word in self.keyword['music'][1]):
                        self.play_song()
                    # Seach time mode
                    elif any(word in text.lower() for word in self.keyword['time'][0]) and\
                        any(word in text.lower() for word in self.keyword['time'][1]):
                        current_time = self.get_time()
                        self.speak(current_time) 
                    # search weather mode
                    elif self.keyword['weather'][0] in text.lower():
                        self.speak(self.response['weather'][0])
                        city = self.hear()
                        self.speak(self.response['weather'][1])
                        try:
                            weather_ans = self.get_weather(city)
                            self.speak(weather_ans)
                        except:
                            self.speak(f"找不到關於{city}的天氣")
                    # chat mode
                    else:
                        response = self.chat(text)
                        self.speak(response)
                else:
                    if self.keyword["on"][0] in text.lower():
                        self.on = True
                        self.speak(self.response['on'][0])

            except KeyboardInterrupt:
                sys.exit()
                
                


if __name__ == "__main__":
    robot = Robot()
    robot.run()



                
