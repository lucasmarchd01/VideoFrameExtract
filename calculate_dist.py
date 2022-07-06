import csv
import argparse
from itertools import count
import os
import glob
import math
import pandas
from natsort import natsorted



def __init__(self):
    self.txtdir = None
    self.savecsv = False

def object_info(txt_file):
    """Read text files in folder and extract object information """

    with open(txt_file, "rt") as f:
        if os.path.getsize(txt_file) == 0:
            return None
        else:
            linelist = [line.rstrip() for line in f]
            objects = []
            for line in linelist: 
                temp_dict = {}
                properties = line.split()
                temp_dict["cls"] = properties[0]
                temp_dict["x_center"] = float(properties[1])
                temp_dict["y_center"] = float(properties[2])
                temp_dict["width"] = float(properties[3])
                temp_dict["height"] = float(properties[4])
                temp_dict["confidence"] = float(properties[5])
                objects.append(temp_dict)
    
    return objects


def find_corners(object):
    """Adds 'corners' entry to object dictionary"""

    x_cen = object['x_center']
    y_cen = object['y_center']
    w = object['width']
    h = object['height']
    upper_left = (x_cen - 0.5*w, y_cen - 0.5*h)
    upper_right = (x_cen + 0.5*w, y_cen - 0.5*h)
    lower_left = (x_cen - 0.5*w, y_cen + 0.5*h)
    lower_right = (x_cen + 0.5*w, y_cen + 0.5*h)
    corners = (upper_left, upper_right, lower_left, lower_right)
    object['corners'] = corners
    return object 
    

def find_midpoints(object):
    """Adds 'midpoints' entry to object dictionary"""

    x_cen = object['x_center']
    y_cen = object['y_center']
    w = object['width']
    h = object['height']
    upper = (x_cen, y_cen - 0.5*h)
    lower = (x_cen, y_cen + 0.5*h)
    left = (x_cen - 0.5*w, y_cen)
    right = (x_cen + 0.5*w, y_cen)
    midpoints = (upper, lower, left, right)
    object['midpoints'] = midpoints
    return object


def find_min(objects):
    """Calculate shortest distance from cautery corner to resection
    margin midpoint"""
    cauteries = []
    resections = []
    for obj in objects:
        if obj['cls'] == '0':
            cauteries.append(obj)
        elif obj['cls'] == '1':
            resections.append(obj)
    if len(cauteries) > 1: # if more than one cautery use one  with highest confidence
        max = 0
        for c in cauteries:
            n = c["confidence"]
            if n >= max:
                max = n
                cautery = c
    elif len(cauteries) == 0:
        return None
    else:
        cautery = cauteries[0]
    if len(resections) > 1: # if more than one resection use one with highest confidence
        max = 0
        for r in resections:
            n = r["confidence"]
            if n >= max:
                max = n
                resection = r
    elif len(resections) == 0:
        return None
    else:
        resection = resections[0]
    
    resection = find_midpoints(resection)
    cautery = find_corners(cautery)

    corner_count = 0
    min = 9999999
    for cor in cautery['corners']:
        midpoint_count = 0
        for mid in resection['midpoints']:
            #calculate distance
            d = math.dist(cor, mid)
            if d < min:
                min_cor = corner_count
                min_mid = midpoint_count
                min = d
            midpoint_count += 1
        corner_count += 1
    
    return (min_cor, min_mid, min)


def identify_point(p):
    corners = ['upper_left', 'upper_right', 'lower_left', 'lower_right']
    midpoints = ['upper', 'lower', 'left', 'right']
    location = (corners[p[0]], midpoints[p[1]])
    return location

def save_results(textfile, loc, dist):
    os.chdir(FLAGS.save_results)
    with open("localization_results_withdist.csv", 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([textfile, loc[0], loc[1], loc[0]+'/'+loc[1], dist])
    os.chdir(FLAGS.directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--directory',
        type=str,
        default="",
        help="Name of the directory where .txt files are saved")

    parser.add_argument(
        '--save_results',
        type=str,
        default='',
        help='save results to csv'
    )

    FLAGS = parser.parse_args()

    os.chdir(FLAGS.directory)
    #os.chdir("C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\yolov5\\runs\\detect\\exp19\\labels")
    myFiles = natsorted(glob.glob("*.txt"))
    
    
    if FLAGS.save_results != '':
        os.chdir(FLAGS.save_results)
        if not os.path.exists("localization_results_withdist.csv"):
            with open("localization_results_withdist.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['file', 'cautery', 'resection margin', 'cautery/resection', 'distance'])

    
    os.chdir(FLAGS.directory)
    counter = 0
    save = [[],[]]
    for text_file in myFiles:
        print("working in file: " + text_file)
        obj = object_info(text_file)
        if obj:
            min = find_min(obj)
            if min:
                location = identify_point(min)
                print("Cautery: " + location[0] + "\nResection Margin: " + location[1])
                if FLAGS.save_results != '':
                    save_results(text_file, location, min[2])

                save[0].append(location[0])
                save[1].append(location[1])
            else:
                save_results(text_file, ['None', 'None'], "None")
        else:
            save_results(text_file, ['None', 'None'], "None")
        if counter % 5 == 0 and counter != 0:
            if len(save[0]) != 0 and len(save[1]) != 0:
                print("\nat file " + text_file)
                print("Highest occurence (corner): " + str(max(save[0], key=save[0].count)))
                print("Highest occurence (edge): " + str(max(save[1], key=save[1].count)))
                save = [[],[]]
        counter += 1