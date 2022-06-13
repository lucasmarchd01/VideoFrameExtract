import csv
import argparse
import os
import glob



# Read text files in folder
def start():
    os.chdir(FLAGS.directory)
    myFiles = glob.glob("*.txt")
    for item in myFiles:
        with open(item, "rt") as f:
            lines = f.readlines()
            for line in lines:
                print(line)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--directory',
        type=str,
        default="",
        help="Name of the directory where .txt files are saved")

    FLAGS = parser.parse_args()
    start()