#!/usr/bin/env python
# Credit to the original creator of this cript, Ninjasl0th!
# https://github.com/NinjaSl0th/IP-Check

from time import sleep
import os
import sys
import requests
from netaddr import *
from socket import socket
import OpenSSL
import ssl
import csv
import _thread

def upprogress(progress):
	sys.stdout.write('\r[{0}] {1}%'.format('#' * (progress / 10), progress))
	sys.stdout.flush()


def infile(ifile, ips, breakrange):
	"""Get the IPs from the file and put them in our array
	"""
	# Open the file and readlines so each line is separate
	preParse = open(ifile, 'r').readlines()
	# Start iterating through each line
	for i in preParse:
		# Check is a range consists of a -
		# eExample 192.168.1.1-50 becomes 192.168.1.1,192.168.1.50
		if "-" in i:
			i = i.rstrip()
			a = i.split("-")
			startrange = a[0]
			b = a[0]
			dotSplit = b.split(".")
			j = "."
			# Join the values using a "." so it makes a valid IP
			combine = dotSplit[0], dotSplit[1], dotSplit[2], a[1]
			endrange = j.join(combine)
			# Calculate the IP range
			ip_list = list(iter_iprange(startrange, endrange))
			# Iterate through the range and remove the IPList
			for i in ip_list:
				a = str(i)
				# Append the ips
				ips.append(a)
		# Check is a range consists of a "_"
		# Ranges like 192.168.1.2_192.168.1.155 will have all IPs between it and append it.
		elif "_" in i:
			i = i.rstrip()
			a = i.split("_")
			startrange = a[0]
			endrange = a[1]
			ip_list = list(iter_iprange(startrange, endrange))
			for i in ip_list:
				a = str(i)
				# Append the IPs to the array
				ips.append(a)
		elif breakrange:
			if "/" in i:
				i = i.rstrip()
				ip_list = list(IPNetwork(i))
				for e in sorted(ip_list):
					st = str(e)
					ips.append(st)
			else:
				 ips.append(i.rstrip())
		else:
			ips.append(i.rstrip())


def reverse(z):
	"""Get reverse DNS information
	"""
	# Check if the IP is a CIDR value because we can't navigate to a CIDR value
	if "/" in z:
		# Return None so that we at least fill some data to see there is nothing.
		return None
	else:
		ip = z
		# Try to resolve.
		try:
			# Try and get the hostname via sockets :D
			chk = socket.gethostbyaddr(ip)
			return chk[0]
		except Exception as e:
			return None


def getcert(a):
	"""Get SSL certificate information"""
	# Return None becasue we can't navigate to a CIDR for SSL
	if "/" in a:
		return None
	else:
		next
	try:
		# Connect over port 443
		cert = ssl.get_server_certificate((a, 443))
	except Exception as e:
		# If it can't connect, return nothing/fail
		return None
	try:
		# Use OpenSSL to pull cert information
		c = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
		subj = c.get_subject()
		comp = subj.get_components()
		for i in comp:
			if 'CN' in i:
				return i[1]
			elif 'CN' not in i:
				continue
			else:
				return None
	except Exception as e:
		# If OpenSSL fails to get information, return nothing/fail
		return None

def who(ips, out):
	"""Lookup IP or CIDR in ARIN DB
	"""
	#upprogress(0)
	total = len(ips)
	prog = 0.0
	for i in ips:
		if "/" in i:
			try:
				r = requests.get("http://whois.arin.net/rest/cidr/"+i+".json")
				if str(r.status_code) == '404':
					# IF ARIN gives us a 4 oh 4, then try the next cidr value.
					continue
				else:
					pass
			except:
				# Die, because we can't connect
				exit('Cannot connect to ARIN!')
			tmp = r.json()
			if "orgRef" not in tmp:
				name = 'None'
			else:
				name = tmp['net']['orgRef']['@name']
			start = tmp['net']['netBlocks']['netBlock']['startAddress']['$']
			end = tmp['net']['netBlocks']['netBlock']['endAddress']['$']
			hostname = reverse(i)
			cn = getcert(i)
			out[i] = i, name, start, end, hostname, cn

		else:
			try:
				# Send GET request to the ARIN RESTFUL API for IP vals
				r = requests.get("http://whois.arin.net/rest/ip/"+i+".json")
			except:
				exit('Cannot connect to ARIN!')
			tmp = r.json()
			try:
				name = tmp['net']['customerRef']['@name']
				start = tmp['net']['netBlocks']['netBlock']['startAddress']['$']
				end = tmp['net']['netBlocks']['netBlock']['endAddress']['$']
				hostname = reverse(i)
				cn = getcert(i)
				out[i] = i, name, start, end, hostname, cn
			except:
				# Sometimes the formatting of ARIN data changes if there is a customer or org as the contact info.
				name = tmp['net']['orgRef']['@name']
				start = tmp['net']['netBlocks']['netBlock']['startAddress']['$']
				end = tmp['net']['netBlocks']['netBlock']['endAddress']['$']
				hostname = reverse(i)
				cn = getcert(i)
				out[i] = i, name, start, end, hostname, cn
			prog = prog + 1
			#upprogress(int(prog / total * 100))
		# Pause for just a sec to not destroy ARIN with requests
		sleep(1)


def outfile(out, ofile):
	"""Output dict to csv
	"""
	writer = csv.writer(open(ofile, 'w'))
	a = list(out.values())
	for i in a:
		writer.writerow(i)
