#!/bin/python
import struct # for literally any stuff with bytes
import sys # for command line args

codefrom = ''
frommemaddr = 0
branchsearch = False
funcstart = -1
funcend = -1
funcline = -1
funclen = -1
threshold = -1
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg == '--codefrom:us':
            codefrom = 'us' # this was the original behaviour
        elif arg == '--codefrom:kor':
            codefrom = 'kor'
        elif arg == '--branchsearch':
            branchsearch = True
        elif arg == '--funcstart:': # for branch search
            funcstart = int(arg[12:], 16)
        elif arg == '--funcend:': # for branch search
            funcend = int(arg[10:], 16)
        elif arg.startswith('--funcline:'): # arg for filtering by what line of the function it is (only works with codefrom:us)
            funcline = int(arg[11:])
        elif arg.startswith('--funclen:'): # arg for filtering by function length (only works with codefrom:us)
            funclen = int(arg[10:])
        elif arg.startswith('--address:'):
            frommemaddr = int(arg[10:], 16)
        elif arg.startswith('--threshold:'): # input a hex value to be the maximum distance from the found function
            threshold = int(arg[12:], 16)

if codefrom == '': # if you didn't set it
    codefrom = input('which dol is your code from? (us or kor):')

if codefrom == 'us':
    fromdolpath = 'RMGE01.dol' # the dol the user supplied some code from
    finddolpath = 'RMGK01.dol' # the dol to find the code in
else: #codefrom = 'kor'
    fromdolpath = 'RMGK01.dol'
    finddolpath = 'RMGE01.dol'


def findsymbol(address, map):
    map.seek(0)
    linenum = 0
    textsection = False
    for line in map:
        linenum += 1 # starts at 1 because my text editor does
        if not textsection:
            textsection = (line == '.text section layout\n') # start at the '.text section layout' string
        else:
            linesplit = line.split()
            symbollength = int(linesplit[1], 16)
            symbolmemaddr = int(linesplit[2], 16)
            if (address > symbolmemaddr) and (address < (symbolmemaddr + symbollength)):
                intofunction = address - symbolmemaddr
                if funcline > -1:
                    if funcline != (int(intofunction / 4) + 1): # if the specified funcline is not the line in the found function
                        return None
                if funclen > -1:
                    if funclen != int(symbollength / 4): # if the specified funclen is not the length of the function
                        return None # stop and return nothing
                print(f'symbol is {int(symbollength / 4)} lines long, this is the {int(intofunction / 4) + 1}th line of the function') # how to output this? maybe just output the whole linesplit array, or a tuple with just the length and name? Also, we need the offset into the symbol map?
                return line[39:-1] #.join(linesplit[5:]) to get just the symbol; symbol name will always start at the 39th character
    return 'Symbol not found'

def findsymbolbyname(symbolname):
    map.seek(0)
    linenum = 0
    textsection = False # starts like findsymbol, but we're looking for name only this time
    for line in map:
        linenum += 1
        if not textsection:
            textsection = (line == '.text section layout\n')
        else:
            linesplit = line.split()
            if linesplit[5] == symbolname:
                symbolmemaddr = int(linesplit[2], 16)
                symbolENDmemaddr = int(linesplit[1], 16) + symbolmemaddr
                return (symbolmemaddr, symbolENDmemaddr, line[39:-1]) # a tuple of start mem address, end mem address, full name
    return None


# begin main program logic
with open('RMGK01.map') as map:
    if branchsearch:
        if codefrom == 'kor':
            symbolname = input('Input symbol name:')
            # __vt__10MarioFaint testing
            symbol = findsymbolbyname(symbolname)
            if symbol == None:
                print('Symbol not found')
                quit()
            startdoladdr = symbol[0] - 0x80004AC0
            enddoladdr = symbol[1] - 0x80004AC0
            print(f'from {hex(symbol[0])} to {hex(symbol[1])} (KOR addresses), symbol {symbol[2]}')
        elif codefrom == 'us':
            if funcstart > -1:
                startdoladdr = funcstart - 0x80004AC0
            else:
                startdoladdr = int(input('Start memory address of function:'), 16) - 0x80004AC0
            
            if funcend > -1:
                enddoladdr = funcend - 0x80004AC0
            else:
                enddoladdr = int(input('End memory address of function:'), 16) - 0x80004AC0
        
        with open(fromdolpath,'rb') as fromdol:
            curdoladdr = 0x100
            fromdol.seek(curdoladdr)
            while True: # loop through every line of the dol
                try:
                    inst = struct.unpack('>I', fromdol.read(4))[0]
                except:
                    break # end of file, stop reading it
                opcode = (0xfc000000 & inst) >> (32 - 6)
                if opcode == 16: # branch b-form
                    branchdist = (0x0000fffc & inst) # no bit shift needed, but it'll need to become signed somehow I think
                    if branchdist > 0x7fff: # signed short limit 32767
                        branchdist = branchdist - 0xfffc
                    branchdest = curdoladdr + branchdist
                    if startdoladdr < branchdest and branchdest < enddoladdr:
                        curmemaddr = 0x80004AC0 + curdoladdr
                        if codefrom == 'kor':
                            print(f'B-form branch at {hex(curdoladdr)} in {fromdolpath} ({hex(curmemaddr)} in memory)! {findsymbol(curmemaddr, map)}')
                        else:
                            print(f'B-form branch at {hex(curdoladdr)} in {fromdolpath} ({hex(curmemaddr)} in memory)!')
                elif opcode == 18: # branch i-form
                    branchdist = (0x03fffffc & inst)
                    if branchdist > 0x01ffffff: # should be negative!
                        branchdist = branchdist - 0x03fffffc
                    #branchdist = branchdist - 4 # for some reason
                    branchdest = curdoladdr + branchdist
                    if startdoladdr < branchdest and branchdest < enddoladdr:
                        curmemaddr = 0x80004AC0 + curdoladdr
                        if codefrom == 'kor':
                            print(f'I-form branch at {hex(curdoladdr)} in {fromdolpath} ({hex(curmemaddr)} in memory)! {findsymbol(curmemaddr, map)}')
                        else:
                            print(f'I-form branch at {hex(curdoladdr)} in {fromdolpath} ({hex(curmemaddr)} in memory)!')
                curdoladdr += 4 # finally, update the current dol address (remember, this is a loop through every code line)
            

    else: # if not branchsearch
        if frommemaddr == 0: # only get if not passed as a parameter
            frommemaddr = int(input(f"{codefrom} memory address of code line:"), 16) # 801c79f8 testing
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
                        absdist = abs(frommemaddr - findmemaddr)
                        if threshold > -1:
                            if absdist > threshold: # if the distance exceeds the threshold, ignore symbol
                                symbol = None # a bit hacky but it works 
                            else:
                                symbol = findsymbol(findmemaddr, map)
                        else:
                            symbol = findsymbol(findmemaddr, map)
                        if symbol != None: # if it returns none, this symbol is to be ignored
                            print(f'match at {hex(finddoladdr - 4)} in {finddolpath} ({hex(findmemaddr)} in memory)! {symbol}')
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
        