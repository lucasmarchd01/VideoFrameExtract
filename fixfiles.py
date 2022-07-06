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
    labelspath = "C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\yolov5\\runs\\detect\\exp26\\labels\\"
    imagespath = "C:\\Users\\Lucas\\Video Images\\Testing"
    os.chdir(imagespath)
    for image in natsorted(os.listdir(imagespath)):
        if not os.path.exists(labelspath + image.replace(".jpg", ".txt")) and image.endswith(".jpg"):
            print("adding file: " + image.replace(".jpg", ".txt"))
            f = open(labelspath + image.replace(".jpg", ".txt"), 'a')
            f.close()

def fun3():
    file1 = "C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Labels.csv"
    file2 = "C:\\Users\\Lucas\\Video Images\\Data\\localization_results_withdist.csv"
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    df3 = pd.DataFrame()
    df3["imageFile"] = df1["FileName"]
    df3["textFile"] = df2["file"]
    df3["Step"] = df1["Step"]
    df3["Localization"] = df2["cautery/resection"]
    df3["Distance"] = df2["distance"]
    #df4 = pd.crosstab(df3["Step"], df3["Localization"], margins=True, normalize=True)
    df3.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Compare_withdist.csv")
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
    csv = "C:\\Users\\Lucas\\Video Images\\Data\\AllVideo_Compare_withdist.csv"
    compare = pd.read_csv(csv)
    compare = compare[(compare.Step != "Transition") & (compare.Step != "iKnife") & (compare.Localization != "None/None")]
    #df4 = pd.crosstab(compare["Step"], compare["Localization"], margins=True, normalize=True)
    compare.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\NoNone_Compare_withdist.csv")
    #df4.to_csv("C:\\Users\\Lucas\\Video Images\\Data\\NoNone_Table.csv")


if __name__ == "__main__":
    fun5()