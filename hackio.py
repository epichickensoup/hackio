#!/bin/python
import struct # for literally any stuff with bytes
import sys # for command line args

if len(sys.argv) == 2:
    if sys.argv[1] == '-codefrom:us':
        codefrom = 'us' # this was the original behaviour
    elif sys.argv[1] == '-codefrom:kor':
        codefrom = 'kor'
else:
    codefrom = input('which dol is your code from? (us or kor):')

if codefrom == 'us':
    fromdolpath = 'RMGE01.dol' # the dol the user supplied some code from
    finddolpath = 'RMGK01.dol' # the dol to find the code in
else: #codefrom = 'kor'
    fromdolpath = 'RMGK01.dol'
    finddolpath = 'RMGE01.dol'


def findsymbol(address, map):
    map.seek(0)
    linenum = 1
    for line in map:
        linenum += 1
        linesplit = line.split()
        if linenum > 3:
            symbollength = int(linesplit[1], 16)
            symbolmemaddr = int(linesplit[2], 16)
            if (address > symbolmemaddr) and (address < (symbolmemaddr + symbollength)):
                intofunction = address - symbolmemaddr
                print(f'symbol is {int(symbollength / 4)} lines long, this is the {int(intofunction / 4)}th line of the function') # how to output this? maybe just output the whole linesplit array, or a tuple with just the length and name? Also, we need the offset into the symbol map?
                return line[39:-1] #.join(linesplit[5:]) to get just the symbol; symbol name will always start at the 39th character
                # break #don't because idk??
    return 'Symbol not found'

with open('RMGK01.map') as map:
    # i = 0
    # while i < 20:
    #     i += 1
    #     print(map.readline())
    frommemaddr = int(input(f"{codefrom} memory address of code line:"), 16) # 801c79f8
    # 801c79f8
    print(f'entered address {hex(frommemaddr)}')
    fromdoladdr = frommemaddr - 0x80004AC0
    
    with open(fromdolpath,'rb') as fromdol:
        # usdol.seek(0x48)
        # usloadsec1codeto = struct.unpack('>I',usdol.read(4))[0]
        # usloadsec2codeto = struct.unpack('>I',usdol.read(4))[0]
        # print(f'us dol loads code (section 2) to {hex(usloadsec2codeto)}')
        # usdol.seek(0)
        # these addresses hold the same for the kor dol, so... easy

        fromdol.seek(fromdoladdr)
        index = 0
        instfindarr = [0] * 5 # init an array with 5 entries. Doesn't seem much faster than a list.
        while index < 5:
            instfindarr[index] = struct.unpack('>I', fromdol.read(4))[0]
            index += 1
        # instfind[1] = struct.unpack('>I', fromdol.read(4))[0] # (don't) throw away next instruction
        print(f'instruction bytes there are {hex(instfindarr[0])}')
    
    if codefrom == 'kor':
        print('kor symbol:')
        print(findsymbol(frommemaddr, map))
    #input()
    print('')

    with open(finddolpath,'rb') as finddol:
        # us memory address is not consistently greater or less than kor address
        # if codefrom == 'us':
        finddoladdr = 0x100 # first code starts at 0x100
        # else:
        #     finddoladdr = fromdoladdr
        broken = 0 # var to break the while loop
        instfind = 0 # let's not define this var every time
        while broken != 1:
            match = 0 # number of lines matched... could make this a parameter and use a loop!
            finddol.seek(finddoladdr) # reset so we check everything (including the "additional lines")
            finddoladdr += 4
            # index = 0
            # while index < 5: # while loop almost seemed slower, I don't know why...
            for instfind in instfindarr:
                #instfind = instfindarr[index] remenants of using a while loop
                try:
                    inst = struct.unpack('>I', finddol.read(4))[0]
                except:
                    broken = 1
                    break # reading error (end of file), break
                if inst == instfind:
                    match += 1
                #index += 1 # while loop remenant
            
            if (match > 2):
                findmemaddr = finddoladdr - 4 + 0x80004AC0
                if codefrom == 'us':
                    print(f'match at {hex(finddoladdr - 4)} in {finddolpath} ({hex(findmemaddr)} in memory)! {findsymbol(findmemaddr, map)}')
                    if frommemaddr > findmemaddr: # if us > kor
                        print(f'us address {hex(frommemaddr - findmemaddr)} greater than kor')
                    else:
                        print(f'us address {hex(findmemaddr - frommemaddr)} less than kor')
                else:
                    print(f'match at {hex(finddoladdr - 4)} in {finddolpath} ({hex(findmemaddr)} in memory)!')
                    if findmemaddr > frommemaddr: # if us > kor
                        print(f'us address {hex(findmemaddr - frommemaddr)} greater than kor')
                    else:
                        print(f'us address {hex(frommemaddr - findmemaddr)} less than kor')
    