import os
import sys

def do_one(fname_base,directory):
    os.chdir(directory)
    os.system("pwd")
    os.system("pdflatex " + fname_base + ".tex")
    os.system("pdflatex " + fname_base + ".tex")
    print("scp  " + fname_base + ".pdf cs70@hive20.cs.berkeley.edu:public_html/sp16/notes/")
    os.chdir("..")

import glob

files = glob.glob("./note*")

def find_dir(name):
    for string in files:
        if name in string:
            return string

if (len(sys.argv) == 1):
    for x in xrange(1,23):
        fname_base = "n" + str(x)
        lookup_name = "note" + str(x) + " "
        directory = find_dir(lookup_name)
        do_one(fname_base, directory)

    do_one('n0', 'note0')
else:

    do_one(sys.argv[1],sys.argv[2])

#print sys.argv[1],sys.argv[2]
