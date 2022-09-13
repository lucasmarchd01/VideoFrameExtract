import math
import os
import numpy
import pandas
from matplotlib import pyplot as plt

def formatBoundingBoxes(dataCSV,textDir):
    boundingBoxes = []
    imgSize = (1280, 720)
    labels = ['cautery','resection']
    c = 0
    for i in dataCSV.index:
        print("processing index: " + str(c))
        imageFile = dataCSV["FileName"][i]
        textFile = imageFile.replace('.jpg','.txt')
        videoName,timestamp = imageFile.split("@")
        videoFolder = videoName.lower() + "_labels"
        #textFilePath = os.path.join(textDir,videoFolder,textFile)
        textFilePath = os.path.join(textDir, textFile)
        bboxList = []
        with open(textFilePath,'r') as f:
            lines = f.readlines()
        for line in lines:
            classNum,xmin,ymin,xmax,ymax,conf = line.split()
            bbox = {"class":labels[int(classNum)],
                    "xmin":float(xmin)*imgSize[0],
                    "ymin":float(ymin)*imgSize[1],
                    "xmax":float(xmax)*imgSize[0],
                    "ymax":float(ymax)*imgSize[1],
                    "conf":float(conf)}
            bboxList.append(bbox)
        boundingBoxes.append(bboxList)
        c += 1
    return boundingBoxes

def distance(pt1,pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def getShortestDistance(linePt1,linePt2,cornerPt):
    l2 = distance(linePt1,linePt2)
    if l2 == 0:
        ptLineDistance = math.sqrt(distance(cornerPt,linePt1))
    else:
        t = ((cornerPt[0] - linePt1[0]) * (linePt2[0] - linePt1[0]) + (cornerPt[1] - linePt1[1]) * (linePt2[1] - linePt1[1])) / l2
        t = max(0,min(1,t))
        newPoint = (linePt1[0]+t*(linePt2[0]-linePt1[0]),linePt1[1]+t*(linePt2[1]-linePt1[1]))
        ptLineDistance = math.sqrt(distance(cornerPt,newPoint))
    return ptLineDistance

def getBestCornerToLine(resectionMarginBBox,cauteryBBox,coords=None):
    if coords == None:
        cauteryCorners = [(cauteryBBox["xmin"],cauteryBBox["ymin"]),
                          (cauteryBBox["xmin"],cauteryBBox["ymax"]),
                          (cauteryBBox["xmax"],cauteryBBox["ymin"]),
                          (cauteryBBox["xmax"],cauteryBBox["ymax"])]
    else:
        cauteryCorners = [(cauteryBBox[coords[0]],cauteryBBox[coords[i]])]
    resectionCorners = [(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),
                      (resectionMarginBBox["xmin"], resectionMarginBBox["ymax"]),
                      (resectionMarginBBox["xmax"], resectionMarginBBox["ymin"]),
                      (resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])]

    bestCorner = -1
    bestDistance = math.inf
    for i in range(len(cauteryCorners)):
        cornerPoint = cauteryCorners[i]
        distances = []
        for j in range(0,4):
            resectionCorner = resectionCorners[j]
            distances.append(distance(cornerPoint, resectionCorner))
        shortestDistance = min(distances)
        if shortestDistance < bestDistance:
            bestCorner = i
    if bestCorner !=-1:
        if coords ==None:
            if bestCorner == 0:
                coords = ("xmin","ymin")
            elif bestCorner == 1:
                coords = ("xmin","ymax")
            elif bestCorner == 2:
                coords = ("xmax", "ymin")
            else:
                coords = ("xmax","ymax")
        return cauteryCorners[bestCorner],coords
    else:
        return(math.inf,math.inf),None

def getBestPointGeneric(resectionCenter,bbox):
    cauteryCenter = getBBoxCenter(bbox)
    if cauteryCenter[0] > resectionCenter[0] and cauteryCenter[1]>resectionCenter[1]:
        bestPoint = (bbox["xmin"],bbox["ymin"])
    elif cauteryCenter[0] > resectionCenter[0]:
        bestPoint = (bbox["xmin"], bbox["ymax"])
    elif cauteryCenter[1] > resectionCenter[1]:
        bestPoint = (bbox["xmax"],bbox["ymin"])
    else:
        bestPoint = (bbox["xmax"],bbox["ymax"])
    return bestPoint



def getBestPointToCenter(center,bbox):
    cauteryCorners = [(bbox["xmin"], bbox["ymin"]),
                      (bbox["xmin"], bbox["ymax"]),
                      (bbox["xmax"], bbox["ymin"]),
                      (bbox["xmax"], bbox["ymax"])]
    distances = [abs(distance(center,corner)) for corner in cauteryCorners]
    minCorner = numpy.argmin(numpy.array(distances))
    return cauteryCorners[minCorner]

def getBBoxCenter(bbox):
    xmin = bbox["xmin"]
    width = bbox["xmax"]-bbox["xmin"]
    ymin = bbox["ymin"]
    height = bbox["ymax"]- bbox["ymin"]
    xCenter = round(xmin + (width/2))
    yCenter = round(ymin + (height/2))
    return (xCenter,yCenter)

def plotCuts(dataEntries):
    rights = [[],[],[]]
    lefts = [[],[],[]]
    posteriors = [[],[],[]]
    timeStamps = []
    resectionBBox = []#getAvgResectionMargin(dataEntries)

    cauteryBBox = []
    lastlabel = "None"
    for i in dataEntries.index:
        timestamp = i - dataEntries.index[0]
        boundingBoxes = eval(dataEntries["Tool bounding box"][i])
        newcauteryBBox = [x for x in boundingBoxes if x["class"]=="cautery"]
        newResectionBBox = [x for x in boundingBoxes if x["class"]=="resection"]
        if newcauteryBBox != []:
            cauteryBBox = newcauteryBBox[0]
        if newResectionBBox != []:
            resectionBBox = newResectionBBox[0]
            resectionCenter = getBBoxCenter(resectionBBox)
        if cauteryBBox != [] and resectionBBox!=[]:
            cutLabel = dataEntries["Step"][i]
            bestPoint,coords = getBestCornerToLine(resectionBBox, cauteryBBox)
            bboxWidth = resectionBBox["xmax"] - resectionBBox["xmin"]
            bboxHeight = resectionBBox["ymax"] - resectionBBox["ymin"]

            normalizedPoint = ((bestPoint[0]-resectionCenter[0])/bboxWidth,(bestPoint[1]-resectionCenter[1])/bboxHeight)
            if cutLabel.lower() == "right":
                rights[0].append(normalizedPoint[0])
                rights[1].append(normalizedPoint[1])
                rights[2].append(timestamp)
            elif cutLabel.lower() == "left":
                lefts[0].append(normalizedPoint[0])
                lefts[1].append(normalizedPoint[1])
                lefts[2].append(timestamp)
            elif cutLabel.lower() == "posterior":
                posteriors[0].append(normalizedPoint[0])
                posteriors[1].append(normalizedPoint[1])
                posteriors[2].append(timestamp)
    fig = plt.figure()
    plt.scatter(rights[0],rights[1],label="Right")
    plt.scatter(lefts[0],lefts[1],label="Left")
    plt.scatter(posteriors[0],posteriors[1],label="Posterior")
    plt.legend()
    plt.show()
    df = pandas.DataFrame({"x":rights[0]+lefts[0]+posteriors[0],
                           "y":rights[1]+lefts[1]+posteriors[1],
                           "times":rights[2]+lefts[2]+posteriors[2],
                           "labels":["right" for i in rights[0]]+["left" for i in lefts[0]]+["posterior" for i in posteriors[0]]})
    return df

def getAvgResectionMargin(dataEntries):
    resectionXmins = []
    resectionXmaxs = []
    resectionYmins = []
    resectionYmaxs = []
    for i in dataEntries.index:
        boundingBoxes = eval(dataEntries["Tool bounding box"][i])
        resectionBBox = [x for x in boundingBoxes if x["class"]=="resection"]
        if resectionBBox!= []:
            resectionBBox = resectionBBox[0]
            resectionXmins.append(resectionBBox["xmin"])
            resectionXmaxs.append(resectionBBox["xmax"])
            resectionYmins.append(resectionBBox["ymin"])
            resectionYmaxs.append(resectionBBox["ymax"])
    avgXmin = sum(resectionXmins)/len(resectionXmins)
    avgXmax = sum(resectionXmaxs) / len(resectionXmaxs)
    avgYmin = sum(resectionYmins) / len(resectionYmins)
    avgYmax = sum(resectionYmaxs) / len(resectionYmaxs)
    bbox = {"class":"resection",
            "xmin":round(avgXmin),
            "xmax":round(avgXmax),
            "ymin":round(avgYmin),
            "ymax":round(avgYmax)}
    return bbox

def main():
    csvFile = "C:\\Users\\Lucas\dev\\aigt\\DeepLearnLive\\Datasets\\Step_Detection.csv"
    textDir = "C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\yolov5\\runs\\detect\\exp28\\labels\\"
    dataCSV = pandas.read_csv(csvFile)
    #dataCSV = dataCSV.loc[dataCSV["Fold"]==0]
    if not "Tool bounding box" in dataCSV.columns:
        dataCSV["Tool bounding box"] = formatBoundingBoxes(dataCSV,textDir)
        dataCSV.to_csv(csvFile,index=False)
    #videos = sorted(dataCSV["Folder"].unique())
    # for video in videos:
    #     videoName = os.path.basename(video)
    #     entries = dataCSV.loc[dataCSV["Folder"] == video]
    #     df = plotCuts(entries)
    #     df.to_csv("D:/Lucas/{}_cauteryDistances.csv".format(videoName))

main()