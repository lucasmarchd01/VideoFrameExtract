import os
from natsort import natsorted
import pandas as pd


def fun1():
    videofile = "GH010064"
    filepath = "C:\\Users\\Lucas March\\Video Images\\Training\\GH010064"

    os.chdir(filepath)
    data = pd.read_csv("GH010064_Labels.csv")

    time = 0

    for image in natsorted(os.listdir(filepath)):
        if os.path.exists(image) and image.endswith(".jpg"):
            print(videofile + "@t=%.3f.jpg" % time)
            os.rename("GH010059@t=%.3f.jpg" % time, videofile + "@t=%.3f.jpg" % time)
        data["fileName"] = data["fileName"].replace(["GH010059@t=%.3f.jpg" % time], 
                                                videofile + "@t=%.3f.jpg" % time)
        time += 1/15
    data.to_csv("GH010064444_Labels.csv", index=False)

def fun2():
    labelspath = "C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\yolov5\\runs\\detect\\gh010056_detect\\labels\\"
    imagespath = "C:\\Users\\Lucas\\Video Images\\Training\\GH010056"
    os.chdir(imagespath)
    for image in natsorted(os.listdir(imagespath)):
        if not os.path.exists(labelspath + image.replace(".jpg", ".txt")) and image.endswith(".jpg"):
            print("adding file: " + image.replace(".jpg", ".txt"))
            f = open(labelspath + image.replace(".jpg", ".txt"), 'a')
            f.close()

if __name__ == "__main__":
    fun2()