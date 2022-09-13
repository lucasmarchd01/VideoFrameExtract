import math
import os
import numpy
import pandas
from matplotlib import pyplot as plt
from pytz import country_timezones
from sklearn import metrics

def formatBoundingBoxes(dataCSV,textDir):
    boundingBoxes = []
    imgSize = (1280, 720)
    labels = ['cautery','resection']
    for i in dataCSV.index:
        imageFile = dataCSV["FileName"][i]
        textFile = imageFile.replace('.jpg','.txt')
        videoName,timestamp = imageFile.split("@")
        videoFolder = videoName.lower() + "_labels"
        textFilePath = os.path.join(textDir,videoFolder,textFile)
        bboxList = []
        with open(textFilePath,'r') as f:
            lines = f.readlines()
        for line in lines:
            classNum,xmin,ymin,xmax,ymax,conf = line.split()
            bbox = {"class":labels[int(classNum)],
                    "xmin":float(xmin),
                    "ymin":float(ymin),
                    "xmax":float(xmax),
                    "ymax":float(ymax),
                    "conf":float(conf)}
            bboxList.append(bbox)
        boundingBoxes.append(bboxList)
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

def getBestToolTip(resectionMarginBBox,cauteryBBox):
    resectionEdges = [[(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmin"], resectionMarginBBox["ymax"])],
                      [(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymin"])],
                      [(resectionMarginBBox["xmax"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])],
                      [(resectionMarginBBox["xmin"], resectionMarginBBox["ymax"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])]]

    resectionCorners = [(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),
                        (resectionMarginBBox["xmin"], resectionMarginBBox["ymax"]),
                        (resectionMarginBBox["xmax"], resectionMarginBBox["ymin"]),
                        (resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])]

    cauteryEdges = [[(cauteryBBox["xmin"], cauteryBBox["ymin"]),(cauteryBBox["xmin"], cauteryBBox["ymax"])],
                    [(cauteryBBox["xmin"], cauteryBBox["ymin"]),(cauteryBBox["xmax"], cauteryBBox["ymin"])],
                    [(cauteryBBox["xmax"], cauteryBBox["ymin"]),(cauteryBBox["xmax"], cauteryBBox["ymax"])],
                    [(cauteryBBox["xmin"], cauteryBBox["ymax"]),(cauteryBBox["xmax"], cauteryBBox["ymax"])]]

    cauteryCorners = [(cauteryBBox["xmin"], cauteryBBox["ymin"]),
                      (cauteryBBox["xmin"], cauteryBBox["ymax"]),
                      (cauteryBBox["xmax"], cauteryBBox["ymin"]),
                      (cauteryBBox["xmax"], cauteryBBox["ymax"])]

    inMargin = []
    for corner in cauteryCorners:
        inMargin.append(corner[0] >= resectionMarginBBox["xmin"] and corner[0] <= resectionMarginBBox["xmax"] and corner[1] >= resectionMarginBBox["ymin"] and corner[1]<=resectionMarginBBox["ymax"])
    numInMargins = inMargin.count(True)
    if numInMargins == 0:
        bestTip,_ = getBestCornerToLine(resectionMarginBBox,cauteryBBox)
    elif numInMargins == 1:
        bestTip = cauteryCorners[inMargin.index(True)]
    elif numInMargins == 2:
        if inMargin[0] and inMargin[1]:
            bestTip = (cauteryBBox["xmin"],((cauteryBBox["ymax"]-cauteryBBox["ymin"])/2)+cauteryBBox["ymin"])
        elif inMargin[0] and inMargin[2]:
            bestTip = (((cauteryBBox["xmax"]-cauteryBBox["xmin"])/2)+cauteryBBox["xmin"], cauteryBBox["ymin"])
        elif inMargin[1] and inMargin[3]:
            bestTip = (((cauteryBBox["xmax"] - cauteryBBox["xmin"]) / 2) + cauteryBBox["xmin"], cauteryBBox["ymax"])
        else:
            bestTip = (cauteryBBox["xmax"], ((cauteryBBox["ymax"] - cauteryBBox["ymin"]) / 2) + cauteryBBox["ymin"])
    else:
        bestTip = getBBoxCenter(cauteryBBox)
    return bestTip


def getBestCornerToLine(resectionMarginBBox,cauteryBBox,coords=None):
    if coords == None:
        cauteryCorners = [(cauteryBBox["xmin"],cauteryBBox["ymin"]),
                          (cauteryBBox["xmin"],cauteryBBox["ymax"]),
                          (cauteryBBox["xmax"],cauteryBBox["ymin"]),
                          (cauteryBBox["xmax"],cauteryBBox["ymax"])]
    else:
        cauteryCorners = [(cauteryBBox[coords[0]],cauteryBBox[coords[i]])]
    resectionEdges = [[(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmin"], resectionMarginBBox["ymax"])],
                      [(resectionMarginBBox["xmin"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymin"])],
                      [(resectionMarginBBox["xmax"], resectionMarginBBox["ymin"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])],
                      [(resectionMarginBBox["xmin"], resectionMarginBBox["ymax"]),(resectionMarginBBox["xmax"], resectionMarginBBox["ymax"])]]

    bestCorner = -1
    bestDistance = math.inf
    for i in range(len(cauteryCorners)):
        cornerPoint = cauteryCorners[i]
        distances = []
        for j in range(0,4):
            resectionCorner1 = resectionEdges[j][0]
            resectionCorner2 = resectionEdges[j][1]
            distances.append(distance(cornerPoint, resectionCorner1)+distance(cornerPoint,resectionCorner2))
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

def getBestPointFromLast(prevPoint,cauteryBBox):
    cauteryCorners = [(cauteryBBox["xmin"], cauteryBBox["ymin"]),
                      (cauteryBBox["xmin"], cauteryBBox["ymax"]),
                      (cauteryBBox["xmax"], cauteryBBox["ymin"]),
                      (cauteryBBox["xmax"], cauteryBBox["ymax"])]
    bestCorner = -1
    bestDistance = math.inf
    for i in range(len(cauteryCorners)):
        cornerPoint = cauteryCorners[i]
        newDistance = distance(cornerPoint, prevPoint)
        if newDistance < bestDistance:
            bestCorner = i
            bestDistance = newDistance
    return cauteryCorners[bestCorner]

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

def getDifferences(dataEntries):
    resectionBBox = getAvgResectionMargin(dataEntries)
    cauteryBBox = []
    bestPoint = None

    for i in dataEntries.index:
        timestamp = i - dataEntries.index[0]
        boundingBoxes = eval(dataEntries["Tool bounding box"][i])
        newcauteryBBox = [x for x in boundingBoxes if x["class"] == "cautery"]
        if newcauteryBBox != []:
            if len(newcauteryBBox) > 1:
                bestConf = -1
                for bbox in newcauteryBBox:
                    if bbox["conf"] >= bestConf:
                        bestCautery = bbox
                        bestConf = bbox["conf"]
            else:
                bestCautery = newcauteryBBox[0]
            cauteryBBox = bestCautery
        if cauteryBBox != [] and resectionBBox != []:
            cutLabel = dataEntries["Step"][i]
            if bestPoint == None and cutLabel.lower() in ["surgery", "posterior", "right", "left"]:
                bestPoint = getBestPointToCenter(getBBoxCenter(resectionBBox), cauteryBBox)
                difference = []
                labels = []
            elif cutLabel.lower() in ["surgery", "posterior", "right", "left"]:
                newbestPoint = getBestPointFromLast(bestPoint, cauteryBBox)
                ptDistance = distance(newbestPoint, bestPoint)
                if ptDistance > 0:
                    difference.append(ptDistance)
                    bestPoint = newbestPoint
                    if cutLabel.lower()=="surgery":
                        labels.append(0)
                    else:
                        labels.append(1)
    return difference,labels

def getThreshold(differenceDF):
    '''differenceDF["avgDiff"] = [0.0 for i in differenceDF.index]
    for i in differenceDF.index:
        if i<differenceDF.index[0]+10:
            differenceDF["avgDiff"][i] = numpy.mean(differenceDF["difference"][:i+1])
        else:
            differenceDF["avgDiff"][i] = numpy.mean(differenceDF["difference"][i-10:i+1])'''
    differenceDF = differenceDF.copy().sort_values("difference")

    scores = list(differenceDF["difference"])
    trueLabels = list(differenceDF["labels"])
    fpr,tpr,thresh = metrics.roc_curve(trueLabels,scores)
    threshold = thresh[numpy.argmin(abs(tpr-(1-fpr)))]
    return threshold

def getPredictions(threshold,differenceDF):
    differenceDF["predictions"] = [0 for i in differenceDF.index]
    for i in differenceDF.index:
        if i<differenceDF.index[0]+7:
            averageDiff = differenceDF["difference"][:i+7]
        else:
            averageDiff = differenceDF["difference"][i-7:i+1]
        numBelowThreshold = [True if i<threshold else False for i in averageDiff]
        numTrue = numBelowThreshold.count(True)
        if numTrue >= 4:#round(len(numBelowThreshold)/2):
            differenceDF["predictions"][i] = 1

    confMat = metrics.confusion_matrix(list(differenceDF["labels"]),list(differenceDF["predictions"]))
    print(confMat)
    accuracy = (confMat[0][0]+confMat[1][1])/numpy.sum(confMat)
    recall = confMat[1][1] / (confMat[1][1]+confMat[1][0])
    f1_score = (2 * confMat[0][0]) / ((2*confMat[0][0]) + confMat[0][1] + confMat[1][0])
    print("Accuracy: {}    Recall: {}     F1: {}".format(accuracy,recall,f1_score))
    return differenceDF,accuracy,recall

def plotCuts(dataEntries):
    rights = [[],[],[]]
    lefts = [[],[],[]]
    posteriors = [[],[],[]]
    noCuts = [[],[],[]]


    resectionBBox = getAvgResectionMargin(dataEntries)
    timeStamps = []
    rightTimes = []
    leftTimes = []
    postTimes = []
    noneTimes = []
    cauteryBBox = []
    prevLabel = "nocut"
    fig = plt.figure()
    len_Cuts = []
    len_nocuts = []
    bestPoint = None
    for i in dataEntries.index:
        timestamp = i - dataEntries.index[0]
        boundingBoxes = eval(dataEntries["Tool bounding box"][i])
        newcauteryBBox = [x for x in boundingBoxes if x["class"]=="cautery"]
        #newResectionBBox = [x for x in boundingBoxes if x["class"]=="resection"]
        if newcauteryBBox != []:
            if len(newcauteryBBox) > 1:
                bestConf = -1
                for bbox in newcauteryBBox:
                    if bbox["conf"] >= bestConf:
                        bestCautery = bbox
                        bestConf = bbox["conf"]
            else:
                bestCautery = newcauteryBBox[0]
            cauteryBBox = bestCautery
        '''if newResectionBBox != []:
            resectionBBox = newResectionBBox[0]
            resectionCenter = getBBoxCenter(resectionBBox)'''
        if cauteryBBox != [] and resectionBBox!=[]:
            cutLabel = dataEntries["Step"][i]
            if bestPoint==None and cutLabel.lower() in ["surgery","posterior","right","left"]:
                bestPoint = getBestPointToCenter(getBBoxCenter(resectionBBox),cauteryBBox)
                difference = []

            elif cutLabel.lower() in ["surgery","posterior","right","left"]:
                newbestPoint = getBestPointFromLast(bestPoint,cauteryBBox)
                ptDistance = distance(newbestPoint,bestPoint)
                if ptDistance>0:
                    difference.append(ptDistance)
                    bestPoint = newbestPoint
                    timeStamps.append(i)
                    if cutLabel.lower() == "right":
                        rightTimes.append(-100)
                        leftTimes.append(0)
                        postTimes.append(0)
                        noneTimes.append(0)
                    elif cutLabel.lower() == "left":
                        rightTimes.append(0)
                        leftTimes.append(-100)
                        postTimes.append(0)
                        noneTimes.append(0)
                    elif cutLabel.lower() == "posterior":
                        rightTimes.append(0)
                        leftTimes.append(0)
                        postTimes.append(-100)
                        noneTimes.append(0)
                    else:
                        rightTimes.append(0)
                        leftTimes.append(0)
                        postTimes.append(0)
                        noneTimes.append(-100)
            #bestPoint = getBestToolTip(resectionBBox, cauteryBBox)
            if bestPoint!=None:
                bboxWidth = resectionBBox["xmax"] - resectionBBox["xmin"]
                bboxHeight = resectionBBox["ymax"] - resectionBBox["ymin"]

                normalizedPoint = ((bestPoint[0]),(bestPoint[1]))
                if cutLabel.lower() != prevLabel and cutLabel.lower() =="right":
                    if len(rights[0])>0:
                        plt.plot(rights[0], rights[1],label="right",color="r")
                        len_Cuts.append(len(rights[0]))
                        rights = [[], [], []]
                if cutLabel.lower() != prevLabel and cutLabel.lower() == "left":
                    if len(lefts[0])>0:
                        plt.plot(lefts[0], lefts[1], label="left",color="r")
                        len_Cuts.append(len(lefts[0]))
                        lefts = [[], [], []]
                if cutLabel.lower() != prevLabel and cutLabel.lower() == "posterior":
                    if len(posteriors[0])>0:
                        plt.plot(posteriors[0], posteriors[1], label="posterior",color="r")
                        len_Cuts.append(len(posteriors[0]))
                        posteriors = [[], [], []]
                if cutLabel.lower() != prevLabel and cutLabel.lower() == "surgery":
                    if len(noCuts[0])>0:
                        plt.plot(noCuts[0], noCuts[1], label="noCuts", color="c")
                        len_nocuts.append(len(noCuts[0]))
                        noCuts = [[], [], []]
                if cutLabel.lower() == "right":
                    rights[0].append(normalizedPoint[0])
                    rights[1].append(normalizedPoint[1])
                    rights[2].append(timestamp)
                    prevLabel = "right"
                elif cutLabel.lower() == "left":
                    lefts[0].append(normalizedPoint[0])
                    lefts[1].append(normalizedPoint[1])
                    lefts[2].append(timestamp)
                    prevLabel = "left"
                elif cutLabel.lower() == "posterior":
                    posteriors[0].append(normalizedPoint[0])
                    posteriors[1].append(normalizedPoint[1])
                    posteriors[2].append(timestamp)
                    prevLabel = "posterior"
                elif cutLabel.lower() == "surgery":
                    noCuts[0].append(normalizedPoint[0])
                    noCuts[1].append(normalizedPoint[1])
                    noCuts[2].append(timestamp)
                    prevLabel = "surgery"
                else:
                    prevLabel = cutLabel.lower()


    #plt.plot(lefts[0], lefts[1], label="left")
    #plt.plot(posteriors[0], posteriors[1], label="posterior")
    #plt.scatter(lefts[0],lefts[1],label="Left")
    #plt.plot(noCuts[0],noCuts[1],label="No cuts")
    #plt.legend()
    plt.show()
    df = pandas.DataFrame({"x":rights[0]+lefts[0]+posteriors[0],
                           "y":rights[1]+lefts[1]+posteriors[1],
                           "times":rights[2]+lefts[2]+posteriors[2],
                           "labels":["right" for i in rights[0]]+["left" for i in lefts[0]]+["posterior" for i in posteriors[0]]})
    avgFramesPerCut = sum(len_Cuts)/len(len_Cuts)
    avgFramePerNoCut = sum(len_nocuts) / len(len_nocuts)

    print("Average num frames in cuts: {}".format(sum(len_Cuts)/len(len_Cuts)))
    print("Average num frames in non-cuts: {}".format(sum(len_nocuts) / len(len_nocuts)))
    #avgDifferences = [numpy.mean(difference[i:i+5]) for i in range(len(difference))]
    avgRights = [difference[i] for i in range(len(difference)) if rightTimes[i]==-100]
    print("Average right variance: {}".format(numpy.var(avgRights)))
    avgLefts = [difference[i] for i in range(len(difference)) if leftTimes[i] == -100]
    print("Average left variance: {}".format(numpy.var(avgLefts)))
    avgPosts = [difference[i] for i in range(len(difference)) if postTimes[i] == -100]
    print("Average posterior variance: {}".format(numpy.var(avgPosts)))
    avgNones = [difference[i] for i in range(len(difference)) if noneTimes[i] == -100]
    print("Average no cut variance: {}".format(numpy.var(avgNones)))
    avgCuts = avgRights+avgLefts+avgPosts
    avgCuts = numpy.var(avgCuts)
    avgNoCuts = numpy.var(avgNones)
    fiftyFrameVariances = []
    for i in range(len(difference)):
        if i<100:
            fiftyFrameVariances.append(numpy.var(difference[:i+1]))
        else:
            fiftyFrameVariances.append(numpy.var(difference[i-100:i+1]))
    avgDifferences = [numpy.mean(fiftyFrameVariances[i:i + 5]) for i in range(len(fiftyFrameVariances))]
    '''avgRights = [fiftyFrameVariances[i] for i in range(len(fiftyFrameVariances)) if rightTimes[i] == -100]
    print("Average right variance: {}".format(max(avgRights)))
    avgLefts = [fiftyFrameVariances[i] for i in range(len(fiftyFrameVariances)) if leftTimes[i] == -100]
    print("Average left variance: {}".format(max(avgLefts)))
    avgPosts = [fiftyFrameVariances[i] for i in range(len(fiftyFrameVariances)) if postTimes[i] == -100]
    print("Average posterior variance: {}".format(max(avgPosts)))
    avgNones = [fiftyFrameVariances[i] for i in range(len(fiftyFrameVariances)) if noneTimes[i] == -100 and fiftyFrameVariances[i]>0]
    print("Average no cut variance: {}".format(min(avgNones)))'''
    avgTimeStamps = [numpy.mean(timeStamps[i:i+5]) for i in range(len(timeStamps))]
    '''fig2 = plt.figure()
    plt.plot(avgTimeStamps,avgDifferences,color='c')
    plt.plot(timeStamps,rightTimes,color="r")
    plt.plot(timeStamps,leftTimes,color='b')
    plt.plot(timeStamps,postTimes,color='g')
    plt.show()'''
    return df,avgCuts,avgNoCuts

def getAvgResectionMargin(dataEntries):
    resectionXmins = []
    resectionXmaxs = []
    resectionYmins = []
    resectionYmaxs = []
    for i in dataEntries.index:
        boundingBoxes = eval(dataEntries["Tool bounding box"][i])
        resectionBBox = [x for x in boundingBoxes if x["class"]=="resection"]
        if resectionBBox!= []:
            if len(resectionBBox) > 1:
                bestConf = -1
                for bbox in resectionBBox:
                    if bbox["conf"] >= bestConf:
                        bestResection = bbox
                        bestConf = bbox["conf"]
            else:
                bestResection = resectionBBox[0]
            resectionBBox = bestResection
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
    csvFile = "C:\\Users\\Lucas\\dev\\aigt\\DeepLearnLive\\Datasets\\Step_Detection_withConf.csv"
    textDir = "D:/Lucas"
    dataCSV = pandas.read_csv(csvFile)
    numFolds = len(dataCSV["Fold"].unique())
    accuracies, recalls = [], []
    for fold in range(numFolds):
        print(fold)
        folddataCSV = dataCSV.loc[dataCSV["Fold"]==fold]
        cutFrames = []
        noCutFrames = []
        trainData = folddataCSV.loc[folddataCSV["Set"]=="Train"]
        testData = folddataCSV.loc[folddataCSV["Set"]=="Test"]
        TraindifferenceDF = pandas.DataFrame(columns=["difference","labels"])
        TestdifferenceDF = pandas.DataFrame(columns=["difference", "labels"])
        '''if not "Tool bounding box" in dataCSV.columns:
            dataCSV["Tool bounding box"] = formatBoundingBoxes(dataCSV,textDir)
            dataCSV.to_csv(csvFile,index=False)'''
        trainvideos = sorted(trainData["Folder"].unique())
        avgVarcut = []
        avgvarnoncut = []
        for video in trainvideos:
            print(str(video))
            videoName = os.path.basename(video)
            entries = trainData.loc[trainData["Folder"] == video]
            df,cutVar,nocutVar = plotCuts(entries)
            avgVarcut.append(cutVar)
            
            avgvarnoncut.append(nocutVar)
            print("Non-Cut Variance Training videos: " + str(nocutVar))
            differences,labels = getDifferences(entries)
            TraindifferenceDF = TraindifferenceDF.append(pandas.DataFrame({"difference":differences,"labels":labels}),ignore_index=True)
            
        print("Average Cut Variance Training videos: " + str(numpy.mean(avgVarcut)))
        print("Average non-Cut Variance Training videos: " + str(numpy.mean(avgvarnoncut)))
        threshold = getThreshold(TraindifferenceDF)
        testVideos = sorted(testData["Folder"].unique())
        print("Training Threshold: " + str(threshold))

        for video in testVideos:
            videoName = os.path.basename(video)
            entries = testData.loc[testData["Folder"] == video]
            #df,avgFramesPerCut,avgFramesPerNocut = plotCuts(entries)
            differences, labels = getDifferences(entries)
            TestdifferenceDF = TestdifferenceDF.append(pandas.DataFrame({"difference": differences, "labels": labels}),
                                                    ignore_index=True)
        pred, accuracy,recall = getPredictions(threshold,TestdifferenceDF)
        accuracies.append(accuracy)
        recalls.append(recall)

    print("Average accuracy: {}    Average recall: {}".format(numpy.mean(accuracies),numpy.mean(recalls)))

main()