#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
- - - - - - - CODENAME - - - - - - -
 :::  === ::: :::====  :::===== :::====
 :::  === ::: :::  === :::      :::  ===
 ===  === === =======  ======   =======
  ======  === ===      ===      === ===
	==    === ===      ======== ===  ===

Developer: Chris Maddalena
"""

import sys
import os
from colors import *
from lib import *
import click
import time

# Create drectory for client reports and report
def setupReports(client):
	if not os.path.exists("reports/{}".format(client)):
		try:
			os.makedirs("reports/{}".format(client))
		except:
			print(red("[!] Could not create reports directory!"))


class AliasedGroup(click.Group):
	"""Allows commands to be called by their first unique character
	"""

	def get_command(self, ctx, cmd_name):
		"""
		Allows commands to be called by thier first unique character
		:param ctx: Context information from click
		:param cmd_name: Calling command name
		:return:
		"""
		rv = click.Group.get_command(self, ctx, cmd_name)
		if rv is not None:
			return rv
		matches = [x for x in self.list_commands(ctx)
			if x.startswith(cmd_name)]
		if not matches:
			return None
		elif len(matches) == 1:
			return click.Group.get_command(self, ctx, matches[0])
		ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def viper():
	"""
	- - - - - - - CODENAME - - - - - - -\n
	 :::  === ::: :::====  :::===== :::====\n
	 :::  === ::: :::  === :::      :::  ===\n
	 ===  === === =======  ======   =======\n
	  ======  === ===      ===      === ===\n
	    ==    === ===      ======== ===  ===\n
	Welcome to Viper! To use Viper, select a module you wish to run. Functions are split into modules for flexibility.\n
	Run MODULE --help for more information on a speicifc module.\n
	Warning: Some functions will require running Viper with sudo (e.g. nmap SYN scans)!
	"""
	# Everything starts here
	pass


@viper.command(name='osint', short_help='The full OSINT suite of tools will be run (domain, people, Shodan).')
@click.option('-c', '--client', help='The target client, such as ABC Company. This will be used for report titles.', required=True)
@click.option('-d', '--domain', help='The email domain, such as example.com. Do not include @.', required=True)
@click.option('-sf', '--scope-file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--dns', is_flag=True, help='Set option if you do or do not want to brute force DNS. Defaults to no DNS.')
@click.option('--google', is_flag=True, help='Set option if you do or do not want to Google for index pages and admin pages for the domain. Defaults to no Google.')
@click.option('--files', is_flag=True, help='Set option if you do or do not want to Google for files on the domain. Defaults to no Google.')
@click.option('-v', '--verbose', is_flag=True, help='With verbose enabled, more domain information is collected.')
@click.option('-b', '--brute', is_flag=True, help='With brute enabled, Viper will use DNSRecon/Fierce to brute force DNS.')
@click.pass_context

def osint(self, client, domain, dns, google, files, scope_file, verbose, brute):
	"""
	The Shadow-Viper intelligence gathering toolkit:\n
	This module runs all OSINT modules together. Viper uses TheHarvester to locate email addresses and social media profiles.
	Profiles are cross-referenced with HaveIBeenPwned, Twitter's API, and LinkedIn.\n
	Viper uses various tools and APIs are used to collect domain/IP information on the provided IP addresses and/or domains.\n
	Several API keys are required for all of the look-ups: Twitter, URLVoid, Cymon, and Shodan
	"""

	asciis.printArt()
	print(green("[+] OSINT Module Selected: Viper will run all recon modules."))
	setupReports(client)
	f = "reports/{}/Domain_Report.txt".format(client)
	report = open(f, 'w')

	email_tools.harvest(client, domain)
	domain_tools.goCrazy(client, domain)

	try:
		report.write("### Domain Report for {} ###\n".format(client))
	except Exception  as e:
		print(red("[!] Failed to create new report file!"))
		print(red("[!] Error: {}".format(e)))

	if scope_file:
		scope = domain_tools.genScope(scope_file)
		# Just in case you forget the domain in your scope file, it's added here
		scope.append(domain)
		for i in scope:
			domain_tools.collectDomainInfo(i, report, verbose)
	else:
		domain_tools.collectDomainInfo(domain, report, verbose)

	if dns:
		print(green("[+] DNS recon was selected: Viper will brute force DNS with Fierce and DNSRecon."))
		if scope_file:
			for ip in scope:
				if not domain_tools.isip(ip):
					domain_tools.dnsRecon(ip, client, brute)
		else:
			domain_tools.dnsRecon(domain, client, brute)
	else:
		print(yellow("[+] DNS recon was NOT selected: Viper skipped DNS brute forcing."))

	if files:
		print(green("[+] File discovery was selected: Viper will perform Google searches to find files for the provided domain."))
		file_discovery.discover(client, domain)
	else:
		print(yellow("[+] File discovery was NOT selected: Viper skipped Googling for files."))

	if google:
		print(green("[+] Google discovery was selected: Viper will perform Google searches to find admin and index pages."))
		domain_tools.googleFu(client, domain)
	else:
		print(yellow("[+] Google discovery was NOT selected: Viper skipped Googling for admin and index pages."))

	report.close()


@viper.command(name='people',
	short_help='Only email addresses and social media profile recon (email, Twitter, and LinkedIn). Provide an email @domain.')
@click.option('-c', '--client', help='The target client, such as ABC Company. This will be used for naming reports.', required=True)
@click.option('-d', '--domain', help='The email domain, such as example.com. Do not include @.', required=True)

def people(client,domain):
	"""
	This module uses TheHarvester to locate email addresses and social media profiles. Profiles are cross-referenced with
	HaveIBeenPwned, Twitter's API, and LinkedIn.\n
	A Twitter app key is necessary for the Twitter API integration.
	"""

	asciis.printArt()
	print(green("[+] People Module Selected: Viper will run only modules for email addresses and social media."))
	setupReports(client)

	email_tools.harvest(client, domain)


@viper.command(name='domain', short_help='Only domain-related recon will be performed (DNS, Shodan, rep data). Provide a list of IPs and domains.')
@click.option('-c', '--client', help='The target client, such as ABC Company. This will be used for report titles.', required=True)
@click.option('-d', '--domain', help='The email domain, such as example.com. Do not include @.', required=True)
@click.option('-sf', '--scope-file', type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--dns', is_flag=True, help='Set option if you do or do not want to brute force DNS. Defaults to no DNS.')
@click.option('--google', is_flag=True, help='Set option if you do or do not want to Google for index pages and admin pages for the domain. Defaults to no Google.')
@click.option('--files', is_flag=True, help='Set option if you do or do not want to Google for files on the domain. Defaults to no Google.')
@click.option('-v', '--verbose', is_flag=True, help='With verbose enabled, more domain information is collected.')
@click.option('-b', '--brute', is_flag=True, help='With brute enabled, Viper will use DNSRecon/Fierce to brute force DNS.')

def domain(client, domain, dns, google, files, scope_file, verbose, brute):
	"""
	This module uses various tools and APIs to collect information on the provided IP addresses and/or domains.\n
	Several API keys are required for all of the look-ups: URLVoid, Cymon, and Shodan
	"""

	asciis.printArt()
	print(green("[+] Domain Module Selected: Viper will run only domain and IP-related modules."))
	setupReports(client)
	f = "reports/{}/Domain_Report.txt".format(client)
	report = open(f, 'w')

	domain_tools.goCrazy(client, domain)

	try:
		report.write("### Domain Report for {} ###\n".format(client))
	except Exception  as e:
		print(red("[!] Failed to create new report file!"))
		print(red("[!] Error: {}".format(e)))

	if scope_file:
		scope = domain_tools.genScope(scope_file)
		# Just in case you forget the domain in your scope file, it's added here
		scope.append(domain)
		for i in scope:
			domain_tools.collectDomainInfo(i, report, verbose)
	else:
		domain_tools.collectDomainInfo(domain, report, verbose)

	if dns:
		print(green("[+] DNS recon was selected: Viper will brute force DNS with Fierce and DNSRecon."))
		if scope_file:
			for ip in scope:
				if not domain_tools.isip(ip):
					domain_tools.dnsRecon(ip, client, brute)
		else:
			domain_tools.dnsRecon(domain, client, brute)
	else:
		print(yellow("[+] DNS recon was NOT selected: Viper skipped DNS brute forcing."))

	if files:
		print(green("[+] File discovery was selected: Viper will perform Google searches to find files for the provided domain."))
		file_discovery.discover(client, domain)
	else:
		print(yellow("[+] File discovery was NOT selected: Viper skipped Googling for files."))

	if google:
		print(green("[+] Google discovery was selected: Viper will perform Google searches to find admin and index pages."))
		domain_tools.googleFu(client, domain)
	else:
		print(yellow("[+] Google discovery was NOT selected: Viper skipped Googling for admin and index pages."))

	report.close()


@viper.command(name='shodan', short_help='Look-up IPs and domains on Shodan using the Shodan API and your API key.')
@click.option('-sf', '--scope-file', help='Name fo the file with your IP addresses.', type = click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-s', '--scope-ips', help='Provide individual IP addresses. Multiple IPs can be provided and this can be used instead of a scoping file. (Ex: -s IP -s IP -s IP)', multiple=True)
@click.option('-o', '--output', default='Shodan_Report.txt', help='Name of the output file for the information.')

def shodan(scope_file, scope_ips, output):
	"""
	The Range-Viper network data toolkit:\n
	Look-up information on IP addresses using Shodan's API and your API key.\n
	You must have a Shodan API key!
	"""

	report = open(output, 'w')

	asciis.printArt()
	print(green("[+] Shodan Module Selected: Viper will check Shodan for the provided domains and IPs."))
	if scope_ips == () and scope_file is None:
		print(red("[!] No targets provided! Use -s or -sf"))
	try:
		report.write("---SHODAN Results as of {}---\n\n".format(time.strftime("%m/%d/%Y")))
		if scope_file:
			scope = domain_tools.genScope(scope_file)
			for i in scope:
				report.write("---Shodan shows this for {}---\n".format(i))
				domain_tools.shodanSearch(i, report)

		if scope_ips:
			for i in scope_ips:
				report.write("---Shodan shows this for {}---\n".format(i))
				domain_tools.shodanSearch(i, report)
		print(green("[+] The Shodan search has completed!"))
	except Exception as e:
		print(red("[!] The Shodan search could not be completed!"))
		print(red("[!] Error: {}").format(e))

	report.close()


@viper.command(name='scan', short_help='Scan IPs and domains using nmap or MassScan - This is noisy!')
@click.option('-sf', '--scope-file', help='Name fo the file with your IP addresses.', type = click.Path(exists=True, readable=True, resolve_path=True))
@click.option('-s', '--scope-ips', help='Scoped IP addresses. Can be used instead of a scoping file.', multiple=True)
@click.option('-o', '--output', default='Scan_Report.csv', help='Name of the CSV output file for the scan results.')
@click.option('-p','--ports', help='The ports to be included in your scan, e.g. 80 or 0-65535', required=True)
@click.option('-a','--args', help='The scan arguments for the selected scanner (e.g. "-sSV -T4 --open"). Do not use -oA for nmap.', required=True)

def scan(ports, args, scope_file, scope_ips, output):
	"""
	The Pit-Viper penetration testing toolkit:\n
	Viper can run nmap scans for you. Provide your scope and arguments and Viper will take care of the rest.
	Viper will flag web ports and output a text file that can be used with tools like EyeWitness for screenshots.
	You can edit the web ports Viper looks for by editing ~/Web_Ports.txt.\n
	SYN scans require sudo! Start Viper with sudo if you plan to run a SYN scan.
	"""

	report = open(output, 'w')

	asciis.printArt()
	print(green("[+] Scan Module Selected: Viper will run your scan against the provided domains and IPs."))
	if scope_ips == () and scope_file is None:
		print(red("[!] No targets provided! Use -s or -sf"))

	if scope_file:
		with open(scope_file, 'r') as scope:
			for i in scope:
				print(green("[+] Running nmap againts {}".format(i.rstrip())))
				scan_tools.runNMAP(i.rstrip(), ports, args, report)

	if scope_ips:
		for ip in scope_ips:
			print(green("[+] Running nmap againts {}".format(ip)))
			scan_tools.runNMAP(ip, ports, args, report)

	report.close()


@viper.command(name='verify', short_help='Verify an external pen test scope. This returns a csv file with SSL cert, whois, and other data for verification.')
@click.option('-c', '--client', help='The target client, such as ABC Company. This will be used for report titles.', required=True)
@click.option('-sf', '--scope-file', help='Name fo the file with your IP addresses.', type = click.Path(exists=True, readable=True, resolve_path=True), required=True)
#@click.option('-s', '--scope-ips', help='Scoped IP addresses. Can be used instead of a scoping file.', multiple=True)
@click.option('-o', '--output', default='Verification.csv', help='Output file (CSV) for the findings.')
@click.option('--cidr', is_flag=True, help='Use if the scoped IPs include any CIDRs.')

def verify(scope_file, output, cidr, client):
	"""
	This module will use reverse DNS, ARIN, and SSL certificate information to try to verify testing scope.
	"""

	asciis.printArt()
	print(green("[+] Scope Verification Module Selected: Viper will attempt to verify who owns the provided IP addresses."))
	setupReports(client)
	report = "reports/{}/{}".format(client, output)

	# initialize our array for IP address storage
	ips = []
	# initialize our dict for info storage
	out = {}

	try:
		verification.infile(scope_file, ips, cidr)
		verification.who(ips, out)
		verification.outfile(out, report)
	except Exception as e:
		print(red("[!] Verification failed!"))
		print(red("[!] Error: %s" % e))


@viper.command(name='ssl', short_help='Check SSL cert for provided IP or domain.')
@click.option('-t', '--target', help='IP address with the certificate. Include the port if it is not 443, e.g. IP:8080', required=True)
@click.option('--labs', is_flag=True, help='Query Qualys SSL Labs in addition to pulling the certificate.')

def ssl(target, labs):
	"""
	This module can be used to quickly pull an SSL certificate's information for easy reference.
	It can also be used to run an SSLLabs scan on the target (coming soon).
	"""

	asciis.printArt()
	print(green("[+] SSL Module Selected: Viper will pull SSL certificate information for the provided IP and port."))
	scan_tools.checkSSL(target)
	if labs:
		ssllabsscanner.getResults(target, 1)


@viper.command(name='rep', short_help='Check reputation of provided IP or domain.')
@click.option('-t', '--target', help='The target IP address or domain.', required=True)
@click.option('-o', '--output', default='Reputation_Report.txt', help='Name of the output file for the search results.')

def rep(target, output):
	"""
	This module can be used to quickly collect reputation data for the provided IP address. Viper will query URLVoid and eSentire's Cymon.\n
	API keys for URLVoid and Cymon are required!
	"""

	report = open(output, 'w')

	asciis.printArt()
	print(green("[+] Reputation Module Selected: Viper will reputation data for the provided IP address or domain name."))
	domain_tools.searchCymon(target, report)
	domain_tools.urlVoidLookup(target, report)


@viper.command(name='knowing', short_help='Saturday Morning Cartoons are a thing I miss.')

def knowing():
	print("...is half the battle...")
	print(red("G.") + "I." + blue(" Jooooe!"))


if __name__ == "__main__":
	viper()
