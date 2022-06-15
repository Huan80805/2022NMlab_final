import time
from turtle import done
import cv2
from PIL import Image
import pickle
import numpy as np
import socket


def camera():
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    _, frame = cap.read()
    cap.release()
    return frame

def get_gesture():
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    HOST = '140.112.18.210'
    PORT = 8000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    try:
        while True:
            _, frame = cap.read()
            frame = frame[::-1, :, ::-1]
            frame = np.array( Image.fromarray(frame[:, 420:1500, :]).resize((224, 224)) )

            frame = pickle.dumps(frame)

            s.send(frame)

            gesture = s.recv(1024).decode()
            if gesture != 'no hand':
                s.close()
                cap.release()
                return gesture
    except:
        s.close()
        cap.release()


if __name__ == '__main__':
    pipeline = (
        "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)1920, height=(int)1080, "
            "format=(string)NV12, framerate=(fraction)30/1 ! "
        "queue ! "
        "nvvidconv flip-method=2 ! "
            "video/x-raw, "
            "width=(int)1920, height=(int)1080, "
            "format=(string)BGRx, framerate=(fraction)30/1 ! "
        "videoconvert ! "
            "video/x-raw, format=(string)BGR ! "
        "appsink"
    )
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    HOST = '140.112.18.210'
    PORT = 8000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    try:
        while True:
            _, frame = cap.read()
            frame = frame[::-1, :, ::-1]
            frame = np.array( Image.fromarray(frame[:, 420:1500, :]).resize((224, 224)) )

            frame = pickle.dumps(frame)

            s.send(frame)

            Done = s.recv(1024)
            if Done.decode() != 'Done':
                s.close()
                print('serer closed connection')
                #break
    except:
        s.close()
        cap.release()