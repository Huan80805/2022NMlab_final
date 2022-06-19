# Speech Robot
This project is a Speech Robot based on Google ASR model and GTTS(Google Text-To-Speech) deployed on jetson nano 2GB. User order the jetson nano by oral or hand pose commend and the jetson nano will output corresponding information. We provide four services. Such as <br>
* Chatting
* Weather searching
* Time searching
* Playing YT music

## Hardware requirement
1. [jetson nano](https://www.nvidia.com/zh-tw/autonomous-machines/embedded-systems/jetson-nano/)
2. Speaker (eg. KTNET Q61)
3. Mic (eg. INTOPIC JAZZ-012)
4. USB sound adapter (eg. SABRENT USB audio adapter)
5. [Raspberry Pi camera v2](https://www.raspberrypi.com/products/camera-module-v2/)
6. Cable to connect above devices.

## Pre-requirement and Installation 
pre-requirement to build librosa
```
sudo apt-get install portaudio19-dev llvm-9 llvm-p-dev
export LLVM_CONFIG=/usr/bin/llvm-config-9
```
preinstallation required for numba
```
git clone https://github.com/wjakob/tbb.git
cd tbb/build
cmake ..
make -j4
sudo make install
```
now you can pip install the rest packages
```
pip3 install -r requirement.txt
```
we use openai and google speech-to-text cloud service in this project. Replace filepath 'decent-lambda-352910-86fe91bb705c.json' with your google cloud key json fileplease and put your api openai key in .env file, specifically
```
OPENAI_KEY='your api key'
```

hand pose classfication
> IMPORTANT: Everything about the hand pose os in the "trt_pose_hand" directory.<br>
 Our model is from [trt_pose_hand](https://github.com/NVIDIA-AI-IOT/trt_pose_hand). Please follow it's "Getting Started" tutorial to install [trt_pose](https://github.com/NVIDIA-AI-IOT/trt_pose). (torch2trt is not needed). Then, using below commend to install needed python package.
```sh
pip install -r requirement_workstation.txt
```
## Test pre-requirement
we provide several scripts to test whether each component is working
```

# list all audio devices
python3 test_asr.py --list_audio_devices

# test if a specific mic is working, this will record "voice.wav" lasting 5 seconds 
python3 test_mic.py --input_device ${device_idx}

# run a speech recognition from a specific mic
python3 test_asr.py --input_device ${device_idx}

# test openAI nlp cloud service, you should see a chat with AI by text
python3 test_chat.py

# test gtts and speaker
python3 test_tts.py --output_device ${device_idx}

```
## How to use

Run the ```hand_pose_server_ws.py``` and ```server_send_gesture.py``` respectively on your server or any device with defined ID. The first server is for receiving image from jetson nano and do the hand pose algorithm. The second one is for handling request from speech robot. Don't forget change the IP and port of socket into your own IP and desired port number. And you also need to 
```sh
python3 hand_pose_server_ws.py
python3 server_send_gesture.py
```
Then, run photo taking process on jetson nano with camera.
```sh
python3 client.py
```
Finally you can start a robot, please modify robot.py with your device ids and run
```
python3 robot.py
``` 
## Used Technology and Result Demo
<div style="text-align:center"><img src='./img/architecture.png' height=250></div>

### Demo
https://www.youtube.com/watch?v=dH29B6pBTYY
### Speech-to-speech interface
We integrate speech-to-text, NLP model and text-to-speech cloud servies to provide users with an AI robot who can "chat" with users.
### Music player
We use yt-dlp packages to download the video user request playing. furthermore, we use PyAudio to control the audio segment sent into speakers, which enables controlling music in real-time. Users can choose to use "voice command" or "hand pose" to control music
### Controlling music playing by hand pose
During the music playback, we use hand pose to control the playing, for the voice of music might interference detection of oral commend. We use the [trt_pose_hand](https://github.com/NVIDIA-AI-IOT/trt_pose_hand) as our hand pose estimation and classification model. There are totally six different gestures (pan, peace, ok, fist, stop and no hand) and corresponding five operations for controlling the playing of current music. 
![](./img/HandPose.png)
Six kinds of gesture map five operation.<br>
1. "stop" will terminate the playing.
2. "peace" will Pause the playing.
3. "pan" will continue the playing.
4. "fist" will increase the volume of music.
5. "ok" will decrease the volume of music.
6. "no hand" will do nothing.

Remark: Please make sure your hand is <font color='red'>enough far away and in the middle</font> of scene.

### Search weather
We provide a weather searching function in our chat robot. Using keyword "天氣" or "weather" to activate this service. After service activated success, robot will ask where does the user want to search the weather. Choose and speak the desire city name, robot will search and answer you. We use beautifulsoup4 and requests to do the web crawlering. The default target website is [新浪天氣](https://weather.sina.com.tw/tw_today.shtml).

<div style="text-align:center"><img src='./img/Requests.png' height=150><img src='./img/BS4.png' height=150></div>


