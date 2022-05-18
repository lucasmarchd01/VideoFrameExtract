# Creates csv file for folder with video images


import os
import csv
from natsort import natsorted



directory = "C:\\Users\\Lucas March\\Video Images\\GH010067"
videoName = "GH010067"

with open(directory + "\\" + videoName + ".csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['fileName', 'Time Recorded', 'Phase', 'Folder'])

    for image in natsorted(os.listdir(directory)):
        if image.endswith('.jpg'):
            imageSplit = image.removesuffix(".jpg")
            imageSplit = imageSplit.split("@t=")
            writer.writerow([image, imageSplit[-1], None, directory])
    print(videoName + ".csv saved to: " + directory)

