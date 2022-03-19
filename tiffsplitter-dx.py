# recreation of Nicholas N. Pakidko's TiffSplitter
# will also output a .fnt


import sys
from PIL import Image
import os

# For usage, check BionicleFont.info :stuck_out_tongue:

class FNTEntry:
    def __init__(self, c, w, h, k, b, m):
        self.code = c
        self.width = w
        self.height = h
        self.kerning = k
        self.baseline = b
        self.manual = m


def find_right_edge(image):
    pixels = image.load()
    rows = image.size[1]
    columns = image.size[0]
    record = 0
    for i in range(rows):
        for l1 in range(columns-1, -1, -1):
            if pixels[l1, i][3] == 0:
                continue
            else:
                if l1 > record:
                    # print("Record!", l1, i)
                    # print(pixels[l1, i])
                    record = l1
        # print("Passed a row!")
    return record

def find_left_edge(image):
    pixels = image.load()
    rows = image.size[1]
    columns = image.size[0]
    record = 9999
    for i in range(rows):
        for l1 in range(columns):
            if pixels[l1,i][3] == 0:
                continue
            else:
                if l1 < record:
                    # print("Record!",l1,i)
                    # print(pixels[l1,i])
                    record = l1
        # print("Passed a row!")
    return record


def find_top_edge(image):
    pixels = image.load()
    rows = image.size[1]
    columns = image.size[0]
    record = 9999
    for i in range(rows):
        for l1 in range(columns):
            if pixels[l1, i][3] == 0:
                continue
            else:
                if i < record:
                    # print("Record!", l1, i)
                    # print(pixels[l1, i])
                    record = i
        # print("Passed a row!")
    return record

def find_bottom_edge(image):
    pixels = image.load()
    rows = image.size[1]
    columns = image.size[0]
    record = 0
    for i in range(rows-1, -1, -1):
        for l1 in range(columns):
            if pixels[l1, i][3] == 0:
                continue
            else:
                if i > record:
                    # print("Record!", l1, i)
                    # print(pixels[l1, i])
                    record = i
        # print("Passed a row!")
    return record


def split_up(image, w, h):
    print("Width: ", image.size[0])
    print("Height: ", image.size[1])
    print("Tile width: ", w)
    print("Tile height: ", h)
    pixels = image.load()
    if image.size[0] % w != 0:
        print("The program can't split your file into equally sized segments! Please remake your TGA!")
        input()
        exit()
    if image.size[1] % h != 0:
        print("The program can't split your file into equally sized segments! Please remake your TGA!")
        input()
        exit()
    rows = image.size[1] // h
    columns = image.size[0] // w
    splitfiles = []
    count = 0
    # print(columns)
    for i in range(rows):
        for l1 in range(columns):
            splitfiles.append(Image.new('RGBA', size=(w, h)))
            for l2 in range(h):
                for l3 in range(w):
                    newpixels = splitfiles[-1].load()
                    newpixels[l3, l2] = pixels[(l1 * w) + l3, (i * h) + l2]
            count += 1
    # print(count)
    # print(len(splitfiles))
    return splitfiles



def get_args(ifile):
    with open(ifile, 'r') as the_file:
        lines = [line.rstrip() for line in the_file if line[:2] != "//"]
    return lines

def convert(var):
    return list(var.to_bytes(4, byteorder='little'))

def do_things(image, args):
    # Setup for arguments
    tile_width = int(args[0])  # used for splitting
    tile_height = int(args[1])  # used for splitting
    kerning = int(args[2])  # maybe used?
    baseline = int(args[3])  # might be tossed
    space_size = int(args[4])  # for the header
    if args[5] != "0 0 0 0":
        color = int(args[5])
    else:
        color = 1
    chars = args[6]  # needed
    mkerning = [int(i) for i in args[7]]

    # print(chars)
    bchars = []
    i = 0
    while i < len(chars):
        try:
            if chars[i] != "\\":
                bchars.append(ord(chars[i]))
            else:
                high = chars[i+2]
                low = chars[i+3]
                bchars.append(int(high+low, 16))
                i += 3
                # input()
            # print(chars[i])
            i += 1
        except IndexError:
            pass
    # Arguments set up
    # now to try parsing this
    im = Image.open(image)
    splitfiles = split_up(im, tile_width, tile_height)
    entries = []
    for i in range(len(splitfiles)):
        left = find_left_edge(splitfiles[i])
        right = find_right_edge(splitfiles[i])
        top = find_top_edge(splitfiles[i])
        bottom = find_bottom_edge(splitfiles[i])
        # print("Inferences:")
        charwidth = right - left
        # charwidth = right
        charheight = bottom - top
        ckerning = left + 1
        cbase = tile_height - (bottom + 1)
        """print("Width:", charwidth)
        print("Height:", charheight)
        print("Kerning:", ckerning)
        print("Baseline:", cbase)"""
        # if mkerning[i] != 0:
            #print(bchars[i],"has manual kerning!",mkerning[i])
        entries.append(FNTEntry(bchars[i], charwidth, charheight, ckerning, cbase, mkerning[i]))

    print(len(entries))
    print(len(mkerning))
    # FILE OUTPUT
    fnt = []
    fnt.extend(convert(1))
    fnt.extend(convert(len(entries)))
    fnt.extend(convert(len(entries)))
    fnt.extend(convert(tile_width//color))
    fnt.extend(convert(tile_height//color))
    fnt.extend(convert(kerning//color))
    fnt.extend(convert(baseline//color))
    fnt.extend(convert(space_size//color))

    for entry in entries:
        fnt.append(entry.code)
        fnt.append(0)
        # fnt.extend(convert(int(round(entry.width/color)) - entry.manual))
        fnt.extend(convert((entry.width//color) - entry.manual))
        fnt.extend(convert(int(round(entry.height/color))))
        fnt.extend(convert((entry.kerning//color) + entry.manual))
        # fnt.extend(convert(int(round(entry.kerning/color)) + entry.manual))
        fnt.extend(convert(int(round(entry.baseline/color))))
    # print(fnt)
    if not os.path.exists(image[:-4]+"/"):
        print("Creating directory!")
        os.makedirs(image[:-4]+"/")
    for i in range(len(splitfiles)):
        splitfiles[i].save(image[:-4]+"/"+image[:-4]+"0_"+str(i)+".tga", "TGA")
        # print("Save",i)
        # input()

    with open(image[:-4]+"/"+image[:-3]+"fnt", 'wb') as the_file:
        the_file.write(bytearray(fnt))




        

if len(sys.argv) <= 2:
    print("Too few arguments")
    print("Usage: tiffsplitter-dx.py <image>.tga <fontinfofile>")
    input()
    exit()

if len(sys.argv) >= 4:
    print("Too many arguments")
    print("Usage: tiffsplitter-dx.py <image>.tga <fontinfofile>")
    input()
    exit()
    

arguments = get_args(sys.argv[2])
do_things(sys.argv[1],arguments)