import csv
import os

readCSV = ""
currentDir = "C:\\Users\\Lucas\\Video Images\\Training\\Step_Detection - Copy.csv"
newDir= "C:\\Users\\Lucas\\Video Images\\Training\\Step_Detection_Reduced.csv"


with open(readCSV, 'r') as file:
    reader = csv.reader(file)
    for line in reader:
        if line[5] == "Surgery":
            os.rename()

