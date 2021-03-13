# hackio
A Python script that searches for matching code functions in the Korean and US SMG1 DOL files, also finding the matching Korean symbol.

This project is not directly affiliated with [Super Hackio](https://github.com/SuperHackio/), it is simply named after him out of fondness and thankfulness. (Specifically, he used to look up symbol names for cheat codes I made).

# Setup

Requires the DOL files for RMGE01 and RMGK01 in the script's directory, named `RMGE01.dol` and `RMGK01.dol`, respectively.

Also requires the Korean symbol map for Super Mario Galaxy in the script's directory under the name `RMGK01.map`.



# Usage

Syntax:

`python hackio.py`
 - Runs the program in "interactive mode"
 - It will ask which region your code address is from (`us` or `kor`).
 - After this, it will ask you for the memory address of the code line.
   - This will be the same address of the "Address" column in the "Code" tab of Dolphin Emulator.

Additional syntax: 
 - `python hackio.py -codefrom:us`
   - Automatically uses the US dol as the source for the code.
 - `python hackio.py -codefrom:kor`
   - Automatically uses the Korean dol as the source for the code.

Example:
```
$ python hackio.py -codefrom:us
us memory address of code line:802b1d20
entered address 0x802b1d20
instruction bytes there are 0x807c0380

symbol is 65 lines long, this is the 15th line of the function
match at 0x2ad844 in RMGK01.dol (0x802b2304 in memory)! incLife__10MarioActorFUl 	Player.a MarioActor.o
us address 0x5e4 less than kor
```

# Strategies
 - If you are just looking for a specific function, don't start at the first line of the function! You will end up with a lot of false positives. Instead, start somewhere in the middle. Look for any assembly lines you find unusual or anything that seems unique in the function.
 - Branch statements to other functions tend to be completely different across regions. Avoiding these in your search might be useful, but including them will not necessarily be harmful. 


---
If you have any questions, message me on Discord! [EPICHICKENSOUP#9337](https://discord.com/channels/@me/589615524695113731)
