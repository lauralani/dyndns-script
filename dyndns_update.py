#!/usr/bin/env python3
import os
import sys
import subprocess
import json

from libdyndns import *
from libazure import *
from config import *

os.chdir(basedir)

new_ips = get_currentips()

if (not new_ips.ipv4):
    print(f"{ts()}IPv4 from public check not valid. Aborting!")
    exit(1)
if (not new_ips.ipv6):
    print(f"{ts()}IPv6 from public check not valid. Aborting!")
    exit(1)

empty_cache = False

try:
    cached_ips = get_cache()
except:
    empty_cache = True
    print(f"{ts()}cache.json doesn't exist. Populating from known IPs")
    cached_ips = new_ips
    
# wenn kein Cache existiert und ist nicht different: (not false and not true)
if not cache_isdifferent(cached_ips, new_ips) and not empty_cache:
    exit()
else:
    print(f"{ts()}IPs different!")
    print(f"{ts()}old IPs: 4={cached_ips.ipv4} 6={cached_ips.ipv6}")
    print(f"{ts()}new IPs: 4={new_ips.ipv4} 6={new_ips.ipv6}")
    write_currentips(new_ips)

result = True

if (not "-4" in sys.argv) and (not "-6" in sys.argv):
    print("no IP versions selected. Use either -4 or -6 or both")
    exit(1);

if "-4" in sys.argv:
    result = AZURE_update_zonerecord(domain=domain, apikey=apikey, ipaddress=new_ips.ipv4)
    print(f"{ts()}setting {new_ips.ipv4} via https://api.lauka.space/dyndns")

if "-6" in sys.argv:
    result = AZURE_update_zonerecord(domain=domain, apikey=apikey, ipaddress=new_ips.ipv6)
    print(f"{ts()}setting {new_ips.ipv6} via https://api.lauka.space/dyndns")

if result == False:
    print(f"{ts()}Error setting IPs. Deleting cache.")
    os.remove("cache.json")
