#REF: https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=zh-tw
#Google API Key
from __future__ import division
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../decent-lambda-352910-86fe91bb705c.json"
import re
import sys
from google.cloud import speech
import time
import logging
from audio import AudioInput, list_audio_devices
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
logging.getLogger().setLevel(logging.DEBUG)

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
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)
            # print(transcript)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0


def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "en-US"  # a BCP-47 language tag
    #TODO change sample rate to interface's sample rate
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    stream = AudioInput(device=11, sample_rate=RATE, chunk_size=CHUNK)
    # stream.test_stream()
    start = time.time()
    while not stream.closed:
        samples = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in samples
        )
        logging.debug("request parsed")
        responses = client.streaming_recognize(streaming_config, requests)
        # Now, put the transcription responses to use.
        logging.debug("response generated")
        listen_print_loop(responses)


if __name__ == "__main__":
    list_audio_devices()
    main()