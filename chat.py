import openai
import os                                                                                                                                                                                                          
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env"))
openai.api_key = os.getenv("OPENAI_KEY")
class ChatBot():
    def __init__(self, language='zh-TW'):
        if language.lower() == 'zh-tw':
            self.speaker_a = '人:'
            self.speaker_b = 'AI:'
            self.history = '這是一個能跟你互動還能放音樂的機器人\n'
        elif language.lower() == 'en-us':
            self.speaker_a = 'Human:'
            self.speaker_b = 'AI:'
            self.history = 'This is a AI robot that can play music and chat with you\n'
        else:
            raise NotImplementedError
        return
    def get_response_text(self, text):
        assert len(text)!=0, "no input text for Chatbot"
        self.history += (self.speaker_a + text.strip() + '\n' + self.speaker_b)
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt = self.history,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[self.speaker_a, self.speaker_b]
        )
        response_text = response["choices"][0]['text'].strip()
        self.history += response_text+'\n'
        return response_text