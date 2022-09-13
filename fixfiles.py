import os
from natsort import natsorted
import pandas as pd
import numpy


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
    labelspath = "C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\yolov5\\runs\\detect\\exp28\\labels\\"
    imagespath = "C:\\Users\\Lucas\\Video Images\\Training\\All"
    os.chdir(imagespath)
    for image in natsorted(os.listdir(imagespath)):
        if not os.path.exists(labelspath + image.replace(".jpg", ".txt")) and image.endswith(".jpg"):
            print("adding file: " + image.replace(".jpg", ".txt"))
            f = open(labelspath + image.replace(".jpg", ".txt"), 'a')
            f.close()

def fun3():
    file1 = "C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Labels.csv"
    file2 = "C:\\Users\\Lucas\\Video Images\\Data\\localization_results_withnegdist.csv"
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.DataFrame()
    df3["imageFile"] = df1["FileName"]
    df3["textFile"] = df2["file"]
    df3["Step"] = df1["Step"]
    df3["Localization"] = df2["cautery/resection"]
    df3["Distance"] = df2["distance"]
    #df4 = pd.crosstab(df3["Step"], df3["Localization"], margins=True, normalize=True)
    df3.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Compare_withnegdist.csv")
    #df4.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Table.csv")

def fun4():
    path = "C:\\Users\\Lucas\\Video Images\\Data"
    os.chdir(path)
    newdf = pd.DataFrame(columns=["FileName", "Time Recorded", "Step", "Phase", "Folder"])
    for file in natsorted(os.listdir(path)):
        df = pd.read_csv(file)
        newdf = pd.concat([newdf, df], axis=0, ignore_index=True)
    newdf.to_csv(path + "AllVideo_Labels.csv")

def fun5():
    csv = "C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Compare_withnegdist.csv"
    compare = pd.read_csv(csv)
    compare = compare[(compare.Step != "Transition") & (compare.Step != "iKnife") & (compare.Localization != "None/None")]
    #df4 = pd.crosstab(compare["Step"], compare["Localization"], margins=True, normalize=True)
    compare.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\NoNone_Compare_withnegdist.csv")
    #df4.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\NoNone_Table.csv")


def readLabels():
    dataCSVFile = pd.read_csv("C:\\Users\\Lucas\\dev\\aigt\\DeepLearnLive\\Datasets\\Step_Detection_Contact.csv")
    files = [dataCSVFile["Tool bounding box"][x] for x in dataCSVFile.index]
    allInputs = []
    #print(dataCSVFile.info(verbose=True))
    #newdataCSVFile = pd.DataFrame()
    for i in range(len(files)):
        strBoundBox = files[i]
        strBoundBox = strBoundBox.replace(" ","")
        strBoundBox = strBoundBox.replace("'", "")
        strBoundBox = strBoundBox.replace("[", "")
        strBoundBox = strBoundBox.replace("]", "")
        boundingBoxes = []
        if strBoundBox != "":
            listBoundBox = strBoundBox.split("},{")
            for boundingBox in listBoundBox:
                boundingBox = boundingBox.replace("{", "")
                boundingBox = boundingBox.replace("}", "")
                keyEntryPairs = boundingBox.split(",")
                boundingBoxDict = {}
                for pair in keyEntryPairs:
                    key, entry = pair.split(":")
                    if entry.isnumeric():
                        boundingBoxDict[key] = int(entry)
                    else:
                        boundingBoxDict[key] = entry
                x1 = boundingBoxDict["xmin"]
                x2 = boundingBoxDict["xmax"]
                y1 = boundingBoxDict["ymin"]
                y2 = boundingBoxDict["ymax"]
                try:
                    boundingBoxDict["xmin"] = min(x1,x2)
                    boundingBoxDict["xmax"] = max(x1,x2)
                    boundingBoxDict["ymin"] = min(y1,y2)
                    boundingBoxDict["ymax"] = max(y1,y2)
                    boundingBoxes.append(boundingBoxDict)
                    allInputs.append(boundingBoxes)
                    #newdataCSVFile = newdataCSVFile.append(dataCSVFile.iloc[i])

                except TypeError:
                    print("Incompatible types for bounding box: {}".format(boundingBoxDict))

    boundingBoxes = numpy.array([])
    numLoaded = 0
    allOutputs = numpy.array([])
    #finaldataCSVFile = pd.DataFrame()
    for i in range(len(allInputs)):
        if len(allInputs[i]) == 2:
            both = numpy.array([])
            for dict in allInputs[i]:
                bbox = numpy.array(list(dict.values()))
                bbox = numpy.delete(bbox, 0)
                both = numpy.append(both, bbox, axis=0)
            boundingBoxes = numpy.append(boundingBoxes, both, axis=0)
            #finaldataCSVFile = finaldataCSVFile.append(dataCSVFile.iloc[i])
            numLoaded += 1
            if numLoaded % 500 == 0 or i == (len(allInputs) - 1):
                    print("loaded " + str(numLoaded) + ' / ' + str(len(files)) + ' images')
    
    #print(finaldataCSVFile.info(verbose=True))
    return boundingBoxes

def fun6():
    allInputs = []
    dataCSV = "C:\\Users\\Lucas\\dev\\aigt\\DeepLearnLive\\Datasets\\Step_Detection.csv"
    df = pd.read_csv(dataCSV)
    #print(dataCSVFile.info(verbose=True))
    #newdataCSVFile = pd.DataFrame()
    numProcessed = 0
    numToProcess = len(files)
    for i in range(len(files)):
        numProcessed += 1
        if numProcessed % 1000 == 0:
            print("Processed rows {} / {}".format(numProcessed,numToProcess))
        strBoundBox = files[i]
        strBoundBox = strBoundBox.replace(" ","")
        strBoundBox = strBoundBox.replace("'", "")
        strBoundBox = strBoundBox.replace("[", "")
        strBoundBox = strBoundBox.replace("]", "")
        boundingBoxes = []
        if strBoundBox != "":
            listBoundBox = strBoundBox.split("},{")
            for boundingBox in listBoundBox:
                boundingBox = boundingBox.replace("{", "")
                boundingBox = boundingBox.replace("}", "")
                keyEntryPairs = boundingBox.split(",")
                boundingBoxDict = {}
                for pair in keyEntryPairs:
                    key, entry = pair.split(":")
                    if entry.isnumeric():
                        boundingBoxDict[key] = int(entry)
                    else:
                        try:
                            boundingBoxDict[key] = float(entry)
                        except:
                            boundingBoxDict[key] = entry
                x1 = boundingBoxDict["xmin"]
                x2 = boundingBoxDict["xmax"]
                y1 = boundingBoxDict["ymin"]
                y2 = boundingBoxDict["ymax"]
                conf = boundingBoxDict["conf"]
                try:
                    boundingBoxDict["xmin"] = min(x1,x2)
                    boundingBoxDict["xmax"] = max(x1,x2)
                    boundingBoxDict["ymin"] = min(y1,y2)
                    boundingBoxDict["ymax"] = max(y1,y2)
                    boundingBoxes.append(boundingBoxDict)
                    
                    #newdataCSVFile = newdataCSVFile.append(dataCSVFile.iloc[i])

                except TypeError:
                    print("Incompatible types for bounding box: {}".format(boundingBoxDict))
            allInputs.append(boundingBoxes)

    boundingBoxes = []
    numLoaded = 0
    memoryResection = {'class': 'resection', 'xmin': 0, 'ymin': 0, 'xmax': 0, 'ymax': 0, 'conf': 0}
    memoryCautery = {'class': 'cautery', 'xmin': 0, 'ymin': 0, 'xmax': 0, 'ymax': 0, 'conf': 0}
    for i in range(len(allInputs)):
        both = []
        resectionCount = 0
        cauteryCount = 0
        bestResectionConf = -1
        bestCauteryConf = -1
        for bboxDict in allInputs[i]:
            keys = list(bboxDict.keys())
            tool = bboxDict.get('class')
            if tool == 'resection':
                resectionCount += 1
                if bboxDict["conf"] >= bestResectionConf:
                    bestResectionConf = bboxDict["conf"]
                    bestResectionBbox = bboxDict
            else:
                cauteryCount += 1
                if bboxDict["conf"] >= bestCauteryConf:
                    bestCauteryConf = bboxDict["conf"]
                    bestCauteryBbox = bboxDict
        newBoxes = []
        if cauteryCount == 0:
            newBoxes.append(bestResectionBbox)
            newBoxes.append({'class': 0, 'xmin': 0, 'ymin': 0, 'xmax': 0, 'ymax': 0, 'conf': 0})
        elif resectionCount == 0:
            newBoxes.append(memoryResection)
            newBoxes.append(bestCauteryBbox)
        else:
            newBoxes.append(bestResectionBbox)
            newBoxes.append(bestCauteryBbox)
        allInputs[i] = newBoxes
        
        for bboxDict in allInputs[i]:
            bbox = list(bboxDict.values())
            tool = bboxDict.get('class')
            bbox.pop(0)
            bbox.pop(-1)
            if tool == 'resection':
                memoryResection = bboxDict
                res = bbox
            else:
                memoryCautery = bboxDict
                caut = bbox
        both += res
        both += caut
        toNorm = numpy.linalg.norm(self.images[i])
        normImage = (self.images[i]) / (toNorm)
        both = numpy.concatenate([both, normImage])
        boundingBoxes.append(both)
        numLoaded += 1
        if numLoaded % 500 == 0 or i == (len(allInputs) - 1):
            print("loaded " + str(numLoaded) + ' / ' + str(len(files)) + ' images')   

    boundingBoxes = numpy.asarray(boundingBoxes)
    return boundingBoxes


if __name__ == "__main__":
    fun2()