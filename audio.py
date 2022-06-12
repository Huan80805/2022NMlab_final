# Modified from jetson_voice/utils/audio.py
#REF: https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-streaming-mic?hl=zh-tw
# Control Audio IO
import os
import multiprocessing as mp
import pprint
import logging
import librosa
import pyaudio as pa
import numpy as np
from gtts import gTTS
from utils import mutealsa
import sys
import wave
np.set_printoptions(threshold=sys.maxsize)

                
def audio_to_float(samples):
    """
    Convert audio samples to 32-bit float in the range [-1,1]
    """
    if samples.dtype == np.float32:
        return samples
        
    return samples.astype(np.float32) / 32768
  
class AudioInput:
    """
    Live audio stream from microphone input device.
    """
    def __init__(self, device, sample_rate=16000, chunk_size=1600):
        self.stream = None
        with mutealsa():
            self.interface = pa.PyAudio()
        self.device_info = find_audio_device(device, self.interface)
        self.device_id = self.device_info['index']
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.closed = True
        self.listening = False
        # Create a thread-safe buffer of audio data
        self.buff = mp.Queue()
        print('Audio Input Device:')
        pprint.pprint(self.device_info)
        self.open()
     
    def open(self):
        if not self.closed:
            return
        
        # device_sample_rate = int(self.device_info['defaultSampleRate'])
        # device_chunk_size = int(self.chunk_size * device_sample_rate / self.sample_rate)
        
        try:
            self.stream = self.interface.open(
            format=pa.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
            )
            self.closed = False
                
        except OSError as err:
            self.stream = None
            self.closed = True
            raise ValueError(f"audio input device {self.device_id} couldn't be opened with sample_rate={self.sample_rate}")   
        print(f"\naudio stream opened on device {self.device_id} ({self.device_info['name']})")
        print("you can begin speaking now... (press Ctrl+C to exit)\n")
    
    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self.buff.put(in_data)
        return None, pa.paContinue      
    
    def close(self):
        if not self.closed:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.closed = True
            self.buff.put(None)
    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""
        while not self.closed:
            data = []
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self.buff.get()
            # Avoid ROBOT listening while speaking
            if not self.listening:
                continue
            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except:
                    break

            yield b"".join(data)
        
    def test_stream(self):
        # TEST MICROPHONE FUNCTION
        # RECORED 10s AND SAVE AS "test.wav"
        record_seconds = 10
        frames = []
        for i in range(0, int(self.sample_rate / self.chunk_size * record_seconds)):
            data = self.buff.get()
            frames.append(data)

        print("* done recording")
        self.close()

        wf = wave.open("test.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.interface.get_sample_size(pa.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

class AudioOutput:
    """
    gtts Audio Output stream to speaker

    """
    def __init__(self, device, sample_rate=None, chunk_size=4096):
        self.stream = None
        
        if device is None:
            self.device_id = None
            logging.warning(f"creating pass-through audio output without a device")
            return
            
        self.interface = pa.PyAudio()
        self.device_info = find_audio_device(device, self.interface)
        self.device_id = self.device_info['index']
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.requested_rate = sample_rate
        
        print('Audio Output Device:')
        pprint.pprint(self.device_info)
        
        self.open()
    
    def __del__(self):
        if self.device_id is None:
            return
            
        self.close()
        self.interface.terminate()
        
    def open(self):
        if self.stream or self.device_id is None:
            return
            
        try:
            self.stream = self.interface.open(format=pa.paFloat32,
                            channels=1, rate=self.sample_rate,
                            frames_per_buffer=self.chunk_size,
                            output=True, output_device_index=self.device_id)
        except:
            self.sample_rate = int(self.device_info['defaultSampleRate'])
            logging.error(f"failed to open audio output device with sample_rate={self.requested_rate}, trying again with sample_rate={self.sample_rate}")
            
            self.stream = self.interface.open(format=pa.paFloat32,
                            channels=1, rate=self.sample_rate,
                            frames_per_buffer=self.chunk_size,
                            output=True, output_device_index=self.device_id)
        
        logging.info(f"opened audio output device {self.device_id} ({self.device_info['name']})")
        
    def close(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
       
    def write(self, samples):
        if self.device_id is None:
            return
        assert isinstance(samples, gTTS)
        self.open()
        #TODO: avoid saving gtts audio
        samples.save("temp.wav")
        y, sr = librosa.load("temp.wav")
        if sr != self.sample_rate:
            data = librosa.resample(y, sr, self.sample_rate)
        os.remove("temp.wav")
        self.stream.write(data.tobytes())          
#
# device enumeration
# 
_audio_device_info = None

def _get_audio_devices(audio_interface=None):
    global _audio_device_info
    
    if _audio_device_info:
        return _audio_device_info
        
    if audio_interface:
        interface = audio_interface
    else:
        interface = pa.PyAudio()
        
    info = interface.get_host_api_info_by_index(0)
    numDevices = info.get('deviceCount')
    
    _audio_device_info = []
    
    for i in range(0, numDevices):
        _audio_device_info.append(interface.get_device_info_by_host_api_device_index(0, i))
    
    if not audio_interface:
        interface.terminate()
        
    return _audio_device_info
     
     
def find_audio_device(device, audio_interface=None):
    """
    Find an audio device by it's name or ID number.
    """
    devices = _get_audio_devices(audio_interface)
    
    try:
        device_id = int(device)
    except ValueError:
        if not isinstance(device, str):
            raise ValueError("expected either a string or an int for 'device' parameter")
            
        found = False
        
        for id, dev in enumerate(devices):
            if device.lower() == dev['name'].lower():
                device_id = id
                found = True
                break
                
        if not found:
            raise ValueError(f"could not find audio device with name '{device}'")
            
    if device_id < 0 or device_id >= len(devices):
        raise ValueError(f"invalid audio device ID ({device_id})")
        
    return devices[device_id]
                
   
def list_audio_inputs():
    """
    Print out information about present audio input devices.
    """
    devices = _get_audio_devices()

    print('')
    print('----------------------------------------------------')
    print(f" Audio Input Devices")
    print('----------------------------------------------------')
        
    for i, dev_info in enumerate(devices):    
        if (dev_info.get('maxInputChannels')) > 0:
            print("Input Device ID {:d} - '{:s}' (inputs={:.0f}) (sample_rate={:.0f})".format(i,
                  dev_info.get('name'), dev_info.get('maxInputChannels'), dev_info.get('defaultSampleRate')))
                 
    print('')
    
    
def list_audio_outputs():
    """
    Print out information about present audio output devices.
    """
    devices = _get_audio_devices()
    
    print('')
    print('----------------------------------------------------')
    print(f" Audio Output Devices")
    print('----------------------------------------------------')
        
    for i, dev_info in enumerate(devices):  
        if (dev_info.get('maxOutputChannels')) > 0:
            print("Output Device ID {:d} - '{:s}' (outputs={:.0f}) (sample_rate={:.0f})".format(i,
                  dev_info.get('name'), dev_info.get('maxOutputChannels'), dev_info.get('defaultSampleRate')))
                  
    print('')
    
    
def list_audio_devices():
    """
    Print out information about present audio input and output devices.
    """
    list_audio_inputs()
    list_audio_outputs()

