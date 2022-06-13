import csv
import argparse
import os
import glob
import math
from natsort import natsorted



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
                objects.append(temp_dict)
    
            return objects


def find_corners(object):
    """Adds 'corners' entry to object dictionary"""

    x_cen = object['x_center']
    y_cen = object['y_center']
    w = object['width']
    h = object['height']
    upper_left = (x_cen - 0.5*w, y_cen + 0.5*h)
    upper_right = (x_cen + 0.5*w, y_cen + 0.5*h)
    lower_left = (x_cen - 0.5*w, y_cen - 0.5*h)
    lower_right = (x_cen + 0.5*w, y_cen - 0.5*h)
    corners = [upper_left, upper_right, lower_left, lower_right]
    object['corners'] = corners
    return object 
    

def find_midpoints(object):
    """Adds 'midpoints' entry to object dictionary"""

    x_cen = object['x_center']
    y_cen = object['y_center']
    w = object['width']
    h = object['height']
    upper = (x_cen, y_cen + 0.5*h)
    lower = (x_cen, y_cen - 0.5*h)
    left = (x_cen - 0.5*w, y_cen)
    right = (x_cen + 0.5*w, y_cen)
    midpoints = [upper, lower, left, right]
    object['midpoints'] = midpoints
    return object


def find_min(objects):
    """Calculate shortest distance from cautery corner to resection
    margin midpoint"""
    cautery = []
    resection = []
    for obj in objects:
        if obj['cls'] == '0':
            cautery.append(obj)
        elif obj['cls'] == '1':
            resection.append(obj)
    for c in cautery:
        find_corners(c)
    for r in resection:
        find_midpoints(r)
    if len(cautery) != 1:
        print("There must be only one cautery tool in frame. Discarding...")
        return None
    elif len(resection) != 1:
        print("There must be only one resection margin in frame. Discarding...")
        return None
    else:
 
        cautery = cautery[0]
        resection = resection[0]
        corner_count = 0
        min = -1
        for cor in cautery['corners']:
            midpoint_count = 0
            for mid in resection['midpoints']:
                #calculate distance
                d = math.dist(cor, mid)
                if d > min:
                    min_cor = corner_count
                    min_mid = midpoint_count
                    min = d
                midpoint_count += 1
            corner_count += 1
        
        return (min_cor, min_mid)


def identify_point(p):
    corners = ['upper_left', 'upper_right', 'lower_left', 'lower_right']
    midpoints = ['upper', 'lower', 'left', 'right']
    print(p)
    location = (corners[p[0]], midpoints[p[1]])
    print("Cautery: " + location[0] + "\nResection Margin: " + location[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--directory',
        type=str,
        default="",
        help="Name of the directory where .txt files are saved")

    FLAGS = parser.parse_args()

    os.chdir(FLAGS.directory)
    #os.chdir("C:\\Users\\Lucas\\OneDrive - Queen's University\\Summer Research 2022\\Imagelabelling\\Images")
    myFiles = natsorted(glob.glob("*.txt"))


    for text_file in myFiles:
        print("working in file: " + text_file)
        obj = object_info(text_file)
        if obj:
            min = find_min(obj)
            if min:
                identify_point(min)
            
