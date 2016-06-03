import os
import sys

def do_one(fname_base,directory):
    os.chdir(directory)
    os.system("pwd")
    os.system("pdflatex " + fname_base + ".tex")
    os.system("pdflatex " + fname_base + ".tex")
    print("cp  " + fname_base + ".pdf ../compiled/")
    os.system("cp  " + fname_base + ".pdf ../compiled/")
    os.system("rm " + fname_base + "*.log")
    os.system("rm " + fname_base + "*.aux")
    os.chdir("..")

import glob

files = glob.glob("./note*")
print files

def find_dir(name):
    for string in files:
        if name in string:
            return string

if (len(sys.argv) == 1):
    os.system("mkdir compiled")
    for x in xrange(0,24):
        fname_base = "n" + str(x)
        lookup_name = "./note" + str(x)
        directory = find_dir(lookup_name)
        do_one(fname_base, str(directory))

else:
    do_one(sys.argv[1],sys.argv[2])

#print sys.argv[1],sys.argv[2]
