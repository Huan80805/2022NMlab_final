from audio import AudioOutput
from gtts import gTTS
from chat import ChatBot
import logging
import time
from asr import Hearing
from player import Player
from utils import get_yt_url, download_yt_audio
# # list audio devices
# if args.list_devices:
#     list_audio_devices()
#     sys.exit()

class Robot():
    def __init__(self, asr_model="quartznet", mic='11', speaker='11'):
        self.in_device = mic
        self.out_device = speaker
        # Move audio input stream into Hearing
        self.hearing = Hearing(device=self.in_device, sample_rate=16000, chunk_size=int(16000/10))
        # self.out_stream is defined for chatbot only
        self.out_stream = AudioOutput(device=self.out_device)
        self.chatbot = ChatBot()
        # TODO audio output stream for music
        #########################
        # MODE
        # 1. HEARING COMMANDS AND RESPONSE
        # 2. PLAYING MUSIC AND ACTIVATE HAND POSE RECOGNITION
        # 3. PROCESSING COMMAND
        # choices: ['HEARING', 'PLAYING', 'PROCESSING']
        ########################
        self.mode = 'HEARING'
        print('----------ROBOT IS NOW READY---------')
    
    def hear(self):
        # Avoid Robot speaking while listening
        self.hearing.stream.listening = True
        transcript = self.hearing.hear()
        self.hearing.stream.listening = False
        print(transcript)
        return transcript
    def speak(self, text):
        print(text)
        audio = gTTS(text=text, lang='en')
        self.out_stream.write(audio)
    
    def chat(self, text):
        return self.chatbot.get_response_text(text=text)

    def play_song(self):
        self.speak("what song do you want me to play?")
        text = self.hear()
        # Rule-based just for now
        song = text.lower().split("play")[-1]
        self.speak(f"Searching {song} and preparing to play now")
        # Release out_stream
        # TODO, unify two out_stream?
        self.out_stream.close()
        url = get_yt_url(name=song)
        fp = download_yt_audio(url)
        player = Player(filepath=fp)
        # another thread
        player.start()
        # enable hand-pose tracking here
        time.sleep(60)
        player.stop()
        self.out_stream = AudioOutput(device=self.out_device)

    def run(self):
        # Default mode: hearing
        while True:
            if self.mode == "HEARING":
                text = self.hear()
                if "play" in text.lower() and "music" in text.lower():
                    self.play_song()
                else:
                    # Chat mode
                    response = self.chat(text)
                    self.speak(response)
            else:
                raise NotImplementedError
                
                


if __name__ == "__main__":
    robot = Robot()
    robot.run()



                
