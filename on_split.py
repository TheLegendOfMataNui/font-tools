from PIL import Image

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
    """print("Width: ", image.size[0])
    print("Height: ", image.size[1])
    print("Tile width: ", w)
    print("Tile height: ", h)"""
    pixels = image.load()
    if image.size[0] % w != 0:
        print("The program can't split your file into equally sized segments! Please remake your image!")
        input()
        exit()
    if image.size[1] % h != 0:
        print("The program can't split your file into equally sized segments! Please remake your image!")
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
    with open(ifile, 'r', encoding="UTF-8") as the_file:
        lines = [line.rstrip() for line in the_file if line[:2] != "//"]
    return lines

def old_kerntable(raw, chars):
    # this will just assume single-digit numbers
    kerndict = {}
    for i in range(len(raw)):
        if raw[i] != "0":
            kerndict[chars[i]] = int(raw[i])
    return kerndict


def kerntable(raw, chars):
    imustgo = False
    i = 0
    kerndict = {}
    if raw[0] != "\\":
        # print("Falling back to old kerning table!")
        kerndict = old_kerntable(raw[3:], chars)
        imustgo = True
    while imustgo is not True:
        if raw[i] == "\\":  # start of new entry
            # print("Recognized start of new entry!")
            if raw[i+1] == "\\":  # end is with double backslash
                # print("I must go!")
                imustgo = True
                break
            elif raw[i+1] == "x":  # hex representation
                high = raw[i+2]
                low = raw[i+3]
                newrep = int(high + low, 16)
                l1 = i+4
            elif raw[i+1] == "c":  # normal representation
                newrep = ord(raw[i+2])
                l1 = i+3
            newnum = ""
            # print("Hello?")
            while raw[l1] != "\\":  # until start of another entry
                newnum += raw[l1]
                # print("Parsing number!")
                l1 += 1
            kerndict[newrep] = int(newnum)
            # print(kerndict)
            # print("New entry added!")
        i += 1
    # print(kerndict)
    return kerndict
