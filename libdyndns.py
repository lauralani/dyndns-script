import json
import subprocess
import ipaddress
import time
import datetime
import pytz
import requests
import logging



# def get_currentips():
#     url4 = "https://api.ipify.org"
#     url6 = "https://api6.ipify.org"
#     ipv6_new = str(subprocess.run(['/usr/bin/curl', '-6', "-s", url6], stdout=subprocess.PIPE).stdout, encoding="utf-8").strip()
#     try:
#         ipaddress.ip_address(ipv6_new)
#     except:
#         ipv6_new = ""

#     ipv4_new = str(subprocess.run(['/usr/bin/curl', '-4', "-s", url4], stdout=subprocess.PIPE).stdout, encoding="utf-8").strip()
#     try:
#         ipaddress.ip_address(ipv4_new)
#     except:
#         ipv4_new = ""
#     return Cache(ipv4=ipv4_new, ipv6=ipv6_new)

def write_currentips(obj):
    with open('cache.json', 'w') as outfile:
        outfile.write(json.dumps(obj, default=convert_to_dict))

def ts():
    return f"{datetime.datetime.now(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')}: "
