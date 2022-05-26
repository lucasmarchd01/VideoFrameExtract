# This code extracts frames from a video file.

import cv2
import os

videofile = "GH010065"
filepath = "C:\\Users\\Lucas March\\Video Images\\Training\\GH010065"
vidcap = cv2.VideoCapture("C:\\Users\\Lucas March\\Videos\\Gh010065-1.mp4")


success,image = vidcap.read()
time = 0
os.chdir(filepath)
print("Extracting images in: " + filepath)
while success:
  cv2.imwrite(videofile + "@t=%.3f.jpg" % time, image)     # save frame as JPEG file      
  success,image = vidcap.read()
  print('Read a new frame: ', success)
  time += 1/15