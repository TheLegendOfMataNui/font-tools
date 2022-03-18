import os
import sys






if len(sys.argv) <= 1:
    print("Too few arguments")
    print("Usage: generator.py <font>")
    input()
    exit()

if len(sys.argv) >= 3:
    print("Too many arguments")
    print("Usage: generator.py <font>")
    input()
    exit()

print("python tiffsplitter-dx.py "+sys.argv[1]+".tga "+sys.argv[1]+".txt")

os.system("python tiffsplitter-dx.py "+sys.argv[1]+".tga "+sys.argv[1]+".txt")

print("python colfile.py "+sys.argv[1])

os.system("python colfile.py "+sys.argv[1])