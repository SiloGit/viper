#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random
from colors import *

# Ingest a list of names and email addresses to output a comma delimited version
def parseName(file):
	outputFile = "ParsedNames.txt"
	# Read all of the names line by line
	with open(file,"r") as f:
		print(green("[+] Parsing names and outputting to %s" % outputFile))
		names = [line.rstrip('\n').split(" ") for line in f]
		output = open(outputFile,"w")
		for name in names:
			output.write(str(name).replace("]","").replace("[","").replace("'","") + '\n')
		output.close()
		f.close()

# Ingest a list of names/emails and return a randomized version
def randomList(listA):
	print(green("[+] Creating a random list of targets..."))
	listB = []
	for i in range(len(listA)):
		element = random.choice(listA)
		listA.remove(element)
		listB.append(element)
	return listB

def getURLs(domain):
	print(green("[+] Running urlcrazy on %s" % domain))
	try:
		cmd = "urlcrazy %s -f csv | sed 1d | cut -d , -f 2-5" % domain
		result = subprocess.check_output(cmd,shell=True)
		print(result)
	except:
		print(red("[!] Execution of urlcrazy failed!"))


#The Swamp-Viper phishing toolkit:
# file = raw_input("Enter name of file with the names: ")
# phish_tools.parseName(file)

# # Randomize the list of targets
# elif option == "2":
# 	file = raw_input("Enter the location of file of targets: ")
# 	output = raw_input("Enter a name for the output file (txt): ")
# 	try:
# 		print(green ("[+] Attempting to read %s" % file))
# 		with open (file, 'r') as file:
# 			names = file.readlines()
# 		with open(output, "w") as file:
# 			temp = []
# 			temp = phish_tools.randomList(names)
# 			file.write(''.join(str(i) for i in temp))
# 		print(green("[+] Successfully created a random list of targets written to %s" % output))
# 		phishingMenu()
# 	except Exception as e:
# 		print(red("[!] Failed to open the file!"))
# 		print(red("[!] Error: %s" % e))
# 		phishingMenu()
