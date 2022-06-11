import openai
import os                                                                                                                                                                                                          
from dotenv import load_dotenv
from pathlib import Path
from chat import ChatBot
load_dotenv(Path(".env"))
openai.api_key = os.getenv("OPENAI_KEY")
if __name__ == "__main__":
    chatbot = ChatBot()
    while True:
        input_text = input("human:")
        response = chatbot.get_response_text(input_text)
        print(response)