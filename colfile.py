# FONT DECOMPILER
# YAY

# utilizes JMMB's BLKLZSS code because the MPL apparently allows for this
# LZSS code based on LZSS.C 4/6/1989 Haruhiko Okumura

# Imports
import os
import blkfile
import sys

# it's a surprise tool that will help us later
complevel = 0


# CLASSES

class Frankenstein:
    def __init__(self,ID,path,size_c,size_u,flags,contents):
        self.id = ID
        self.path = path
        self.size_c = size_c
        self.size_u = size_u
        self.flags = flags
        self.contents = contents


# COL file

class COLEntry:
    def __init__(self,name,fm,offset,uncsize):
        self.name = name
        self.flags = fm
        self.offset = offset
        self.size_un = uncsize
        self.size_c = 0
        self.contents = []


class COLFile:
    def __init__(self,newfile):
        self.unk1 = conversion(0,newfile)
        self.count = conversion(4,newfile)
        self.unk2 = conversion(8,newfile)
        self.size = conversion(12,newfile)
        self.entries = []


#DB file

class DBEntry:
    def __init__(self,name,path):
        self.name = name
        self.path = path


class DBFile:
    def __init__(self,newfile):
        self.unk1 = conversion(0,newfile)
        self.count = conversion(4,newfile)
        self.unk2 = conversion(8,newfile)
        self.unk3 = conversion(12,newfile)
        self.entries = []



# NOT STRICTLY RELEVANT FUNCTIONS
def hscreen():
    print("COL File tool")
    print("Coded by Ondrik, with help from JMMB")
    print("Usage: colfile.py [OPTIONS] [FILES]")
    print("Options:")
    print("    --help                   Show this screen")
    print("    --saffire-compression    Compress only the TGAs")
    print("    --full-compression       Compress everything")


def sort_args(arguments):
    todo = {}
    for argument in arguments:
        if "--" in argument: # skip the options
            continue
        if argument[-3:] == "col":
            dbexist = os.path.exists(argument+".db")
            if not dbexist:
                print("DB file does not exist!")
                input()
                exit()
            else:
                todo[argument] = 'u'
        elif argument[-3:] == ".db":
            colexist = os.path.exists(argument[:-3])
            if not colexist:
                print("COL file does not exist!")
                input()
                exit()
            else:
                todo[argument[:-3]] = 'u'
        else:
            todo[argument] = 'p'
    return todo
            




def check_exist(fontname):
    cexist = os.path.exists(fontname+".col")
    dbexist = os.path.exists(fontname+".col.db")
    if not cexist:
        print("COL file does not exist! Import will be assumed.")
        input()
        return False
    if not dbexist:
        print("DB file does not exist! Import will be assumed.")
        input()
        return False
    return True
    

# STRICTLY RELEVANT FUNCTIONS

def conversion(pointer,array):   # this is big-endian
    a = 0
    for i in range(4):
        a += (array[pointer+3-i]*(256**i))
    return a

def basename(fpath):  # thank you jmmb
    return fpath.split('/').pop().split('\\').pop()

def BKDRHash(istr):  # thank you jmmb, again
    seed = 131
    ohash = 0
    for char in istr:
        ohash = (ohash*seed)+ord(char)
    return ohash & 0xFFFFFFFF

def deconversion(var,byteorder):  #from decimal number to four-byte little/big endian number
    s = var.to_bytes(4,byteorder=byteorder)
    return list(s)

# decompression is handled in blkfile.BLKLZSS

# COL-RELATED FUNCTIONS
def parseCOL(fname,db):
    intlist = []
    with open(fname,'rb') as the_file:
        intlist = list(the_file.read())
    fcol = COLFile(intlist)
    pointer = 36
    for i in range(fcol.count):
        name = intlist[pointer:pointer+4]
        # print([hex(i) for i in name])
        pointer += 4
        fmb = conversion(pointer,intlist)
        # print(fmb)
        pointer += 4
        off = conversion(pointer,intlist)
        # print(off, hex(off))
        pointer += 4
        su = conversion(pointer,intlist)
        # print(su, hex(su))
        pointer += 4
        fcol.entries.append(COLEntry(name,fmb,off,su))
    trueoffs = [entry.offset for entry in fcol.entries]+[fcol.size]
    truesizes = [trueoffs[i+1]-trueoffs[i] for i in range(len(trueoffs)-1)]

    
    # print([hex(i) for i in trueoffs])
    # print(truesizes)
    for i in range(len(truesizes)):
        fcol.entries[i].size_c = truesizes[i]
        fcol.entries[i].contents = intlist[fcol.entries[i].offset:fcol.entries[i].offset+truesizes[i]]
    return fcol
    


# DB-RELATED FUNCTIONS
def parseDB(fname):
    intlist = []
    with open(fname,'rb') as the_file:
        intlist = list(the_file.read())
    fdb = DBFile(intlist)
    pointer = 36
    for i in range(fdb.count): # all entries in the DB
        name = intlist[pointer:pointer+4]
        # print([hex(i) for i in name])
        pointer += 8
        strlen = intlist[pointer]
        fstr = intlist[pointer+1:pointer+strlen+1]
        # print(''.join([chr(n) for n in fstr]))
        fdb.entries.append(DBEntry(name,''.join([chr(n) for n in fstr])))
        pointer += strlen+1
        #print(hex(intlist[pointer]))
    #for entry in fdb.entries:
        # print(entry.path)
    return fdb





# the input

def decompile(fontname):  # This is to *unpack*
    colfile = fontname+".col"
    dbfile = colfile+".db"
    DBDone = parseDB(dbfile)
    COLDone = parseCOL(colfile,DBDone)
    # print(DBDone.count)
    # print(COLDone.count)
    if DBDone.count != COLDone.count:
        print("Something must have gone terribly wrong!")
    match = True
    all_needed = []
    full_size = 0
    for i in range(DBDone.count):
        match = [hex(c) for c in DBDone.entries[i].name[::-1]] == [hex(c) for c in COLDone.entries[i].name]
        all_needed.append(Frankenstein(COLDone.entries[i].name,DBDone.entries[i].path,COLDone.entries[i].size_c,COLDone.entries[i].size_un,COLDone.entries[i].flags,COLDone.entries[i].contents))
        if match is not True:
            print("Files do not match")
            break
    # print("All is well!")
    """if not os.path.exists(fontname+"/"):
        print("Creating directory!")
        os.makedirs(fontname+"/")"""
    for thing in all_needed:
        compressed = thing.flags & 0x10
        if bool(compressed) is True:
            lzss = blkfile.BLKLZSS()
            data = lzss.decode(bytearray(thing.contents))
        else:
            data = bytearray(thing.contents)
        full_size += len(data)
        match = len(data) == thing.size_u
        if match is not True:
            print("Unexpected uncompressed size in",basename(thing.path))
        # altered_path = thing.path.replace(".","")
        altered_path = thing.path.replace("\\","/")
        while altered_path != altered_path.replace("//","/"):
            altered_path = altered_path.replace("//","/")
        altered_path = list(altered_path)
        # altered_path.insert(-3,".")
        new_path = fontname+"".join(altered_path)
        new_data = list(data)
        # print(new_path)
        if not os.path.exists(new_path[0:new_path.rfind("/")+1]):
            os.makedirs(new_path[0:new_path.rfind("/")+1])
        if new_path[-3:] == "tga":
            # print("TGA - altering")
            new_data[0x10] = 0x20 # whyever this needs to be done but hey
        # print(new_path)
        with open(new_path, 'wb') as the_file:
            the_file.write(bytearray(new_data))
    print("Full uncompressed size:",full_size)
    print("Unpacked!")
    """
    print(COLDone.entries[0].contents)
    lzss = blkfile.BLKLZSS()
    data = lzss.decode(bytearray(COLDone.entries[0].contents))
    print(COLDone.entries[0].size_un)
    print(len(data))"""

# repacking

def recompile(fontname):
    flist = os.listdir(fontname)
    hlist = {BKDRHash(i):i for i in flist}
    sorted_list = {i:hlist[i] for i in sorted(hlist)}
    
    # DB file creation
    full_db_file = deconversion(2,'big')
    full_db_file.extend(deconversion(len(sorted_list),'big'))
    full_db_file.extend(deconversion(6,'big'))
    full_db_file.extend(deconversion(0,'big'))
    full_db_file.extend([255]*20)  
    
    for i in sorted_list:
        the_hash = deconversion(i,'little')
        full_db_file.extend(the_hash)
        full_db_file.extend(deconversion(0,'little'))
        # length byte
        full_db_file.extend([len(sorted_list[i])+2,46,92])
        for char in sorted_list[i]:
            full_db_file.append(ord(char))
        # print([hex(c) for c in full_db_file])
    
    with open(fontname+".col.db",'wb') as the_file:
        the_file.write(bytearray(full_db_file))
    
    #print("Mimick Saffire's packing program? (Y/N)")
    #safcomp = input("Y will only compress TGAs and nothing else - ")
    
    #if safcomp == "N":
    #    allcomp = input("Compress everything? (Y/N)")
    
    full_col_file = deconversion(2,'big')
    full_col_file.extend(deconversion(len(sorted_list),'big'))
    full_col_file.extend(deconversion(4,'big'))
    getback = [len(full_col_file)]
    full_col_file.extend(deconversion(0,'big')) # FILE SIZE - GET BACK TO THIS
    full_col_file.extend([255]*20)
    
    compflag = {}
    
    for i in sorted_list:
        the_hash = deconversion(i,'big')
        full_col_file.extend(the_hash)
        if complevel == 1 and sorted_list[i][-3:] == "tga":
            full_col_file.extend(deconversion(17,'big'))
            compflag[i] = True
        elif complevel == 1 and sorted_list[i][-3:] != "tga":
            full_col_file.extend(deconversion(1,'big'))
            compflag[i] = False
        elif complevel == 2:
            full_col_file.extend(deconversion(17,'big'))
            compflag[i] = True
        else:
            full_col_file.extend(deconversion(1,'big'))
            compflag[i] = False
        getback.append(len(full_col_file))
        full_col_file.extend(deconversion(0,'big'))
        full_col_file.extend(deconversion(os.path.getsize(fontname+"/"+sorted_list[i]),'big'))
    # indices done
    gb2 = []
    for i in sorted_list:
        with open(fontname+"/"+sorted_list[i],'rb') as the_file:
            data = the_file.read()
        alter = list(data)
        # alter.append(0)
        if sorted_list[i][-3:] == "tga":
            # print("TGA - altering")
            # alter[0x10] = 0x30 # whyever this needs to be done but hey
            pass
        backup_data = bytearray(alter)
        old_data = bytearray(alter)
        if compflag[i] is True:
            lzss = blkfile.BLKLZSS()
            data = lzss.encode(old_data)
            """if (list(lzss.decode(data)) != list(backup_data)):
                print("FUCK FUCK FUCK")
                input()"""
        gb2.append(len(full_col_file))
        # print(hex(len(full_col_file)))
        full_col_file.extend(list(data))
        while (len(full_col_file) % 2 != 0):
            full_col_file.append(0)
        # input()
    gb2.append(len(full_col_file))
    # print(hex(len(full_col_file)))
    # clever use of python
    getback.append(getback.pop(0))
    getback_values = [list(deconversion(var,'big')) for var in gb2]
    # input()
    for i in range(len(getback)):
        for l1 in range(4):
            full_col_file[getback[i]+l1] = getback_values[i][l1]
    with open(fontname+".col", 'wb') as the_file:
        the_file.write(bytearray(full_col_file))
    print("Complete!")
    
        


# the actual input

arguments = sys.argv[1:]

if "--help" in sys.argv or len(sys.argv) == 1:
    hscreen()
    exit()

if "--saffire-compresssion" in sys.argv:
    complevel = 1

elif "--full-compression" in sys.argv:
    complevel = 2


things_to_do = sort_args(arguments)

for thing in things_to_do:
    if things_to_do[thing] == 'u': # unpack
        print("Unpacking",thing)
        decompile(thing[:-4])
    if things_to_do[thing] == 'p': # pack
        print("Packing",thing)
        recompile(thing)