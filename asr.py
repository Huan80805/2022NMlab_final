#REF: https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=zh-tw
#Google API Key
from __future__ import division
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "decent-lambda-352910-86fe91bb705c.json"
import re
from google.cloud import speech
from audio import AudioInput


def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            num_chars_printed = len(transcript)
        else:
            return transcript
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            # if re.search(r"\b(exit|quit)\b", transcript, re.I):
            #     print("Exiting..")
            #     break



class Hearing():
    def __init__(self, device, sample_rate, chunk_size):
        self.stream = AudioInput(device, sample_rate, chunk_size)
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        self.language_code = "en-US"  # a BCP-47 language tag
        #TODO change sample rate to interface's sample rate
        self.client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=self.language_code,
        )

        self.config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )
    def hear(self):
        while not self.stream.closed:
            samples = self.stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in samples
            )
            responses = self.client.streaming_recognize(self.config, requests)
            # Now, put the transcription responses to use.
            transcript = listen_print_loop(responses)
            break
        return transcript
