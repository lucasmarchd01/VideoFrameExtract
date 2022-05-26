import os
from natsort import natsorted
import pandas as pd

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
