from tkinter import Image
from CNN_LSTM import CNN_LSTM
from natsort import natsorted
import os
import cv2
import pandas as pd
import shutil

model = CNN_LSTM()
video = "GH010091"
model.loadModel("C:\\Users\\Lucas\\dev\\aigt\\DeepLearnLive\\Networks\\CNN_LSTM\\balancePhaseRun1_Fold_3")
images = "C:\\Users\\Lucas\\Video Images\\Training\\" + video
os.chdir(images)
count=0        
df1 = pd.read_csv(video + "_Labels.csv")
newdf = pd.DataFrame(columns=df1.columns)
for image in natsorted(os.listdir(images)):
    if image.endswith(".jpg"):
        print("\nWorking in file: " + image)
        im = cv2.imread(image)
        pred = model.predict(im)
        if pred[0] == 'Surgery':
            newdf = newdf.append(df1.iloc[count]) # append surgery row to new dataset
            shutil.copy(images + "\\" + image, "C:\\Users\\Lucas\\Video Images\\Testing\\" + image)
    count += 1
newdf.to_csv("C:\\Users\\Lucas\\Video Images\\Testing\\" + video + "_Surgery.csv")


            



