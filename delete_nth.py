import csv

myfile = "C:\\Users\\Lucas\\Video Images\\Training\\Step_Detection - Copy.csv"
newfile= "C:\\Users\\Lucas\\Video Images\\Training\\Step_Detection_Reduced.csv"

with open(myfile, 'r') as f:
    reader = csv.reader(f)
    with open(newfile, 'w', newline="") as nf:
        writer = csv.writer(nf)
        linecount = 0
        index = 0
        for line in reader:
            
            if linecount == 0:
                writer.writerow(line)
                linecount += 1
                continue
            if linecount % 3 == 0:
                  writer.writerow([index] + line[1:])
                  index += 1
            linecount += 1
        
