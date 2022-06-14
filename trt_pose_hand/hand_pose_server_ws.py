import json
import cv2
import math
import os
import sys
import time
import numpy as np
import traitlets
import pickle
import socket
from PIL import Image
import torch
import torchvision.transforms as transforms
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


import trt_pose.coco
import trt_pose.models
from trt_pose.draw_objects import DrawObjects
from trt_pose.parse_objects import ParseObjects
from preprocessdata import preprocessdata
from gesture_classifier import gesture_classifier

with open('preprocess/hand_pose.json', 'r') as f:
    hand_pose = json.load(f)
topology = trt_pose.coco.coco_category_to_topology(hand_pose)

num_parts = len(hand_pose['keypoints'])
num_links = len(hand_pose['skeleton'])
model = trt_pose.models.resnet18_baseline_att(num_parts, 2 * num_links).cuda().eval()
data = torch.zeros((1, 3, 224, 224)).cuda()

MODEL_WEIGHTS = 'hand_pose_resnet18_att_244_244.pth'
model.load_state_dict(torch.load(MODEL_WEIGHTS))

parse_objects = ParseObjects(topology,cmap_threshold=0.15, link_threshold=0.15)
draw_objects = DrawObjects(topology)

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
device = torch.device('cuda')

def preprocess(image):
    global device
    device = torch.device('cuda')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

preprocessdata = preprocessdata(topology, num_parts)
gesture_classifier = gesture_classifier()


clf = make_pipeline(StandardScaler(), SVC(gamma='auto', kernel='rbf'))
clf = pickle.load(open('svmmodel.sav', 'rb'))

with open('preprocess/gesture.json', 'r') as f:
    gesture = json.load(f)
gesture_type = gesture["classes"]

def draw_joints(image, joints):
    count = 0
    for i in joints:
        if i==[0,0]:
            count+=1
    if count>= 3:
        return 
    for i in joints:
        cv2.circle(image, (i[0],i[1]), 2, (0,0,255), 1)
    cv2.circle(image, (joints[0][0],joints[0][1]), 2, (255,0,255), 1)
    for i in hand_pose['skeleton']:
        if joints[i[0]-1][0]==0 or joints[i[1]-1][0] == 0:
            break
        cv2.line(image, (joints[i[0]-1][0],joints[i[0]-1][1]), (joints[i[1]-1][0],joints[i[1]-1][1]), (0,255,0), 1)

def execute(change):
    image = change['new']
    data = preprocess(image)
    cmap, paf = model(data)
    cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
    counts, objects, peaks = parse_objects(cmap, paf)
    joints = preprocessdata.joints_inference(image, counts, objects, peaks)
    draw_joints(image, joints)
    dist_bn_joints = preprocessdata.find_distance(joints)
    gesture = clf.predict([dist_bn_joints,[0]*num_parts*num_parts])
    gesture_joints = gesture[0]
    preprocessdata.prev_queue.append(gesture_joints)
    preprocessdata.prev_queue.pop(0)
    preprocessdata.print_label(image, preprocessdata.prev_queue, gesture_type)
    return image


#img = np.array(Image.open('./test.png'))
#img = execute({'new': img})
#img = Image.fromarray(img).save('result.png')
#sys.exit()

HOST = '140.112.18.210'
PORT = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')
count = 0
th = 0

while True:
    conn, addr = s.accept()
    print('connected by ' + str(addr))
    while True:
        th = 0
        print(count)
        indata = b''
        while True:
            try:
                indata += conn.recv(1024)
                img = pickle.loads(indata)
                break
            except:
                th += 1
                if th == 1000:
                    break
                #print(th)
                continue
        if th == 1000:
            break
        img = execute({'new': img})
        #Image.fromarray(img).save('result.png')
        outdata = 'Done'
        conn.send(outdata.encode())
        count += 1
        