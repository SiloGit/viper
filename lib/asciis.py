#!/usr/bin/env python2

import random

def printArt():
	r1 = """
- - - - - - - CODENAME - - - - - - -
 :::  === ::: :::====  :::===== :::====
 :::  === ::: :::  === :::      :::  ===
 ===  === === =======  ======   =======
  ======  === ===      ===      === ===
    ==    === ===      ======== ===  ===
"""


	r2 = """
- - - - - - - CODENAME - - - - - - -
VV     VV IIIII PPPPPP  EEEEEEE RRRRRR
VV     VV  III  PP   PP EE      RR   RR
 VV   VV   III  PPPPPP  EEEEE   RRRRRR
  VV VV    III  PP      EE      RR  RR
   VVV    IIIII PP      EEEEEEE RR   RR
"""

	r3 = """
- - - - - - - - - CODENAME - - - - - - - - -
____    ____  __  .______    _______ .______
\   \  /   / |  | |   _  \  |   ____||   _  \\
 \   \/   /  |  | |  |_)  | |  |__   |  |_)  |
  \      /   |  | |   ___/  |   __|  |      /
   \    /    |  | |  |      |  |____ |  |\  \----.
    \__/     |__| | _|      |_______|| _| `._____|
"""

	r4 = """
- - - - - - - - - CODENAME - - - - - - - - -
____   ____.__________________________________
\   \ /   /|   \______   \_   _____/\______   \\
 \   Y   / |   ||     ___/|    __)_  |       _/
  \     /  |   ||    |    |        \ |    |   \\
   \___/   |___||____|   /_______  / |____|_  /
                                 \/         \/
"""

	art = [r1,r2,r3,r4]
	print (random.choice(art))
