#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
import logging


from libazure import *
from config import *
from datetime import datetime

# https://docs.python.org/3/library/argparse.html
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--nocache', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.WARNING)
log = logging.getLogger("dyndns_update")

if args.verbose:
    log.setLevel(logging.DEBUG)
log.debug("dyndns_update.py started")

if args.nocache:
    log.info("skipping cache due to '--no-cache'.")

log.info("Info-Message")

#os.chdir(basedir)
#
#
#new_ips = get_currentips()
#
#if (not new_ips.ipv4):
#    print(f"{ts()}IPv4 from public check not valid. Aborting!")
#    exit(1)
#if (not new_ips.ipv6):
#    print(f"{ts()}IPv6 from public check not valid. Aborting!")
#    exit(1)
#
#empty_cache = False
#if "-nocache" in sys.argv:
#    cached_ips = new_ips
#else:
#    try:
#        cached_ips = get_cache()
#    except:
#        empty_cache = True
#        print(f"{ts()}cache.json doesn't exist. Populating from known IPs")
#        cached_ips = new_ips
#
#    # wenn kein Cache existiert und ist nicht different: (not false and not true)
#    if not cache_isdifferent(cached_ips, new_ips) and not empty_cache:
#        exit()
#    else:
#        print(f"{ts()}IPs different!")
#        print(f"{ts()}old IPs: 4={cached_ips.ipv4} 6={cached_ips.ipv6}")
#        print(f"{ts()}new IPs: 4={new_ips.ipv4} 6={new_ips.ipv6}")
#        write_currentips(new_ips)
#
#result = True
#
#if (not "-4" in sys.argv) and (not "-6" in sys.argv):
#    print("no IP versions selected. Use either -4 or -6 or both")
#    exit(1);
#
#azurerequest = AZURE_DYNDNS()
#
#if "-4" in sys.argv:
#    azurerequest.IPv4 = new_ips.ipv4
#    print(f"{ts()}adding {new_ips.ipv4} to request via https://api.lauka.space/dyndns")
#
#if "-6" in sys.argv:
#    azurerequest.IPv6 = new_ips.ipv6
#    print(f"{ts()}adding {new_ips.ipv6} to request via https://api.lauka.space/dyndns")
#
#requestbody = json.dumps(azurerequest.__dict__)
##result = AZURE_update_zonerecord(domain=domain, apikey=apikey, ipaddress=new_ips.ipv6)
#print(f"Body: {requestbody}")
#headers = {
#  'x-api-key': apikey ,
#  'Content-Type': 'application/json'
#}
#result = requests.request("PUT", f"https://api.lauka.app/dyndns/records/{domain}", headers=headers, data=requestbody)
#
#if result == False:
#    print(f"{ts()}Error setting IPs. Deleting cache.")
#    os.remove("cache.json")
#
