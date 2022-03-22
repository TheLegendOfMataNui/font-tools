import os
import sys


if "--help" in sys.argv:
    print("Run the --compress argument to also compress the COL file")
    print("Too lazy to print more for now.")
    exit()



if len(sys.argv) <= 1:
    print("Too few arguments")
    print("Usage: generator.py <font>")
    print("Use generator.py --help for help")
    input()
    exit()

if len(sys.argv) >= 4:
    print("Too many arguments")
    print("Usage: generator.py <font>")
    print("Use generator.py --help for help")
    input()
    exit()



print("python tiffsplitter-dx.py "+sys.argv[1]+".tga "+sys.argv[1]+".txt")

os.system("python tiffsplitter-dx.py "+sys.argv[1]+".tga "+sys.argv[1]+".txt")


if "--compress" in sys.argv:
    print("python colfile.py --full-compression "+sys.argv[1])
    os.system("python colfile.py --full-compression "+sys.argv[1])
else:
    print("python colfile.py "+sys.argv[1])
    os.system("python colfile.py "+sys.argv[1])