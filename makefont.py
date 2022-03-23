# FINAL VERSION OF THIS PROGRAM THIS IS THE DUMBEST THING EVER
# by ondrik
# go yell at me when this breaks (when, not if)

# OBLIGATORY IMPORTS
import os
import blkfile
import sys
from PIL import Image
import io
import on_split

compress = False

input_folder = sys.argv[1]

output_folder = sys.argv[2]

if "--help" in sys.argv:
    print("Final font tool")
    print("Coded by Ondrik, with help from JMMB")
    print("Usage: colfile.py <input folder> <output folder> FONTS [-c]")
    print("Options:")
    print("    --help               Show this screen")
    print("    -c, --compression    Compress everything (must be at the end)")
    exit()

class FNTEntry:
    def __init__(self, c, w, h, k, b, m):
        self.code = c
        self.width = w
        self.height = h
        self.kerning = k
        self.baseline = b
        self.manual = m


def BKDRHash(istr):  # thank you jmmb
    seed = 131
    ohash = 0
    for char in istr:
        ohash = (ohash*seed)+ord(char)
    return ohash & 0xFFFFFFFF

def convert(var, byteorder='little', s=True):
    return list(var.to_bytes(4, byteorder=byteorder, signed=s))

def image_to_ints(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, "TGA")
    img_bytes = img_bytes.getvalue()
    return list(img_bytes)


def do_the_thing(font):
    global input_folder
    global output_folder
    imagefile = input_folder+font
    infofile = input_folder+font+".txt"
    args = on_split.get_args(infofile)
    tile_width = int(args[0])  # used for splitting
    tile_height = int(args[1])  # used for splitting
    kerning = int(args[2])  # indeed it's used
    baseline = int(args[3])  # loading bar
    space_size = int(args[4])  # for the header
    if args[5] != "0 0 0 0":
        color = int(args[5])
    else:
        color = 1
    chars = args[6]  # needed

    bchars = []
    i = 0
    while i < len(chars):
        try:
            if chars[i] != "\\":
                bchars.append(ord(chars[i]))
            else:
                high = chars[i + 2]
                low = chars[i + 3]
                bchars.append(int(high + low, 16))
                i += 3
                # input()
            # print(chars[i])
            i += 1
        except IndexError:
            pass

    try:
        manual_table = on_split.kerntable(args[7], bchars)
        # print("Manual table generated!")
    except:
        # print("No manual table!")
        # print(args[7])
        manual_table = {}
        pass

    try:
        im = Image.open(imagefile+".tif")
    except:
        try:
            print("TIF not found - Falling back to TGA")
            im = Image.open(imagefile+".tga")
        except:
            print("TGA not found - falling back to PNG")
            try:
                im = Image.open(imagefile+".png")
            except:
                print("PNG not found")
                exit()
    splitfiles = on_split.split_up(im, tile_width, tile_height)

    entries = []
    for i in range(len(splitfiles)):
        down = splitfiles[i].resize((tile_width // color, tile_height // color), resample=Image.BICUBIC)
        left = on_split.find_left_edge(down)
        right = on_split.find_right_edge(down)
        top = on_split.find_top_edge(splitfiles[i])
        bottom = on_split.find_bottom_edge(splitfiles[i])
        charwidth = (right - left) + 1
        # charwidth = right
        charheight = bottom - top
        ckerning = left
        cbase = tile_height - (bottom + 1)
        """print("Inferences:")
        print("Width:", charwidth)
        print("Height:", charheight)
        print("Kerning:", ckerning)
        print("Baseline:", cbase)"""
        # print("Adding entry:", i)
        try:
            # print("Manual kerning found!", manual_table[bchars[i]])
            entries.append(FNTEntry(bchars[i], charwidth, charheight, ckerning, cbase, manual_table[bchars[i]]))
        except KeyError:
            # print("No manual kerning found!")
            entries.append(FNTEntry(bchars[i], charwidth, charheight, ckerning, cbase, 0))

    fnt = []
    fnt.extend(convert(1))
    fnt.extend(convert(len(entries)))
    fnt.extend(convert(len(entries)))
    fnt.extend(convert(tile_width//color))
    fnt.extend(convert(tile_height//color))
    fnt.extend(convert(kerning//color))
    fnt.extend(convert(baseline))
    fnt.extend(convert(space_size//color))

    for entry in entries:
        fnt.append(entry.code)
        fnt.append(0)
        fnt.extend(convert(entry.width - entry.manual))
        fnt.extend(convert(entry.height//color))
        fnt.extend(convert(entry.kerning + entry.manual))
        fnt.extend(convert(int(round(entry.baseline/color))))

    # fnt is now a list of ints
    all_files = [image_to_ints(f) for f in splitfiles]

    all_files.append(fnt)

    all_names = [font+"0_"+str(i)+".tga" for i in range(len(splitfiles))]+[font+".fnt"]
    # yay now it's all done
    all_hashes = {BKDRHash(all_names[i]): i for i in range(len(all_names))}
    sorted_list = {i: all_hashes[i] for i in sorted(all_hashes)}
    # the index we need is for all_files
    # all_hashes

    # sorted_list[i] = index into the files
    # all_names[sorted_list[i]] = name
    # all_files[sorted_list[i]] = file

    full_col_file = convert(2, 'big')
    full_col_file.extend(convert(len(sorted_list), 'big'))
    full_col_file.extend(convert(4, 'big'))
    getback = [len(full_col_file)]
    full_col_file.extend(convert(0, 'big'))  # FILE SIZE - GET BACK TO THIS
    full_col_file.extend([255] * 20)


    """for i in sorted_list:
        print(i)
        print(sorted_list[i])
        print(all_names[sorted_list[i]])
        print(all_files[sorted_list[i]][:100])
        input()"""


    compflag = {}

    for i in sorted_list:
        the_hash = convert(i, 'big', False)
        full_col_file.extend(the_hash)
        if compress and all_names[sorted_list[i]][-3:] == "tga":
            full_col_file.extend(convert(17, 'big'))
            compflag[i] = True
        elif compress and all_names[sorted_list[i]][-3:] != "tga":
            full_col_file.extend(convert(1, 'big'))
            compflag[i] = False
        else:
            full_col_file.extend(convert(1, 'big'))
            compflag[i] = False
        getback.append(len(full_col_file))
        full_col_file.extend(convert(0, 'big'))
        full_col_file.extend(convert(len(all_files[sorted_list[i]]), 'big'))
    # indices done
    gb2 = []
    for i in sorted_list:
        data = all_files[sorted_list[i]]
        if compflag[i]:
            lzss = blkfile.BLKLZSS()
            data = lzss.encode(data)
        gb2.append(len(full_col_file))
        # print(hex(len(full_col_file)))
        full_col_file.extend(list(data))
        # print("Packing", sorted_list[i])
        while (len(full_col_file) % 2 != 0):
            full_col_file.append(0)
        # input()
    gb2.append(len(full_col_file))
    # print(hex(len(full_col_file)))
    # clever use of python
    getback.append(getback.pop(0))
    getback_values = [list(convert(var, 'big')) for var in gb2]
    # input()
    for i in range(len(getback)):
        for l1 in range(4):
            full_col_file[getback[i] + l1] = getback_values[i][l1]
    with open(output_folder+font + ".col", 'wb') as the_file:
        the_file.write(bytearray(full_col_file))
    print("Complete!")



















fonts = sys.argv[3:]

if "-c" in fonts or "--compression" in fonts:
    fonts.pop(-1)
    compress = True

for font in fonts:
    print("Creating",font)
    do_the_thing(font)

