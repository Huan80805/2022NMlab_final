from audio import AudioOutput, AudioInput
from gtts import gTTS
from chat import ChatBot
import logging
from asr import Hearing
# # list audio devices
# if args.list_devices:
#     list_audio_devices()
#     sys.exit()

class Robot():
    def __init__(self, asr_model="quartznet", mic='11', speaker='11'):
        # Move audio input stream into Hearing
        self.hearing = Hearing(device=mic, sample_rate=16000, chunk_size=int(16000/10))
        # Defined audio output stream to flexible
        self.out_stream = AudioOutput(speaker)
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
        logging.info('----------ROBOT IS NOW READY---------')
    
    def hear(self):
        # Avoid Robot speaking while listening
        self.hearing.stream.listening = True
        transcript = self.hearing.hear()
        self.hearing.stream.listening = False
        return transcript
    def speak(self, text):
        audio = gTTS(text=text, lang='en')
        self.out_stream.write(audio)
    
    def chat(self, text):
        return self.chatbot.get_response_text(text=text)

    def run(self):
        # Default mode: hearing
        while True:
            if self.mode == "HEARING":
                text = self.hear()
                print(text)
                response = self.chat(text)
                print(response)
                self.speak(response)
            else:
                raise NotImplementedError
                
                


if __name__ == "__main__":
    robot = Robot()
    robot.run()



                
