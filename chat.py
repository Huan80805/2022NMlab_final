import openai
import os                                                                                                                                                                                                          
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env"))
openai.api_key = os.getenv("OPENAI_KEY")
class ChatBot():
    def __init__(self, speaker_a='Human', speaker_b='AI'):
        self.speaker_a = speaker_a+':'
        self.speaker_b = speaker_b+':'
        self.history = 'This is a AI robot that can play music and chat with you\n'
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