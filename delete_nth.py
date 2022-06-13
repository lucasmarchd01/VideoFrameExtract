import csv

myfile = "C:\\Users\\Lucas\\Video Images\\Training\\Phase_Detection_New.csv"
newfile= "C:\\Users\\Lucas\\Video Images\\Training\\Phase_Detection_5FPS.csv"

with open(myfile, 'r') as f:
    reader = csv.reader(f)
    with open(newfile, 'w', newline="") as nf:
        writer = csv.writer(nf)
        linecount = 0
        index = 0
        for line in reader:
            
            if line[0] == '':
                continue
            
            if int(line[0]) % 3 == 0:
                  writer.writerow([index] + line[1:])
                  index += 1
        
