#!/usr/bin/env python3
import os
import sys

#os.chdir("/root/dyndns-script")
#pip3 install requests

import subprocess
import json
from libdyndns import *
from libazure import *
#import ovh
#from libovh import *

domain = "test-01.itxxxxxx.xxx" # Domain
apikey = "b11111c1-1111-1111-1115-480e1111111c" # GUID


#with open('config.json', 'r') as file:
#    config = json.load(file)

new_ips = get_currentips()
empty_cache = False

try:
    cached_ips = get_cache()
except:
    empty_cache = True
    print("cache.json doesn't exist. Populating from known IPs")
    cached_ips = new_ips
    
# wenn kein Cache existiert und ist nicht different: (not false and not true)
if not cache_isdifferent(cached_ips, new_ips) and not empty_cache:
    exit()
else:
    write_currentips(new_ips)



#client = ovh.Client(
#    endpoint='ovh-eu',               # Endpoint of API OVH Europe (List of available endpoints)
#    application_key=f'{config["ovh"]["appkey"]}',    # Application Key
#    application_secret=f'{config["ovh"]["appsecret"]}', # Application Secret
#    consumer_key=f'{config["ovh"]["consumerkey"]}',       # Consumer Key
#)


#set_zonerecord(client, domain, "AAAA", subdomain, new_ips.ipv6, 60)
#set_zonerecord(client, domain, "A", subdomain, new_ips.ipv4, 60)

result = True

if (not "-4" in sys.argv) and (not "-6" in sys.argv):
    print("no IP versions selected. Use either -4 or -6 or both")
    exit(1);

if "-4" in sys.argv:
    result = AZURE_update_zonerecord(domain=domain, apikey=apikey, ipaddress=new_ips.ipv4)



if "-6" in sys.argv:
    result = AZURE_update_zonerecord(domain=domain, apikey=apikey, ipaddress=new_ips.ipv6)

if result == False:
    print("Error setting IPs. Deleting cache.")
    os.remove("cache.json")
