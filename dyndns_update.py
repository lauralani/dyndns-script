#!/usr/bin/env python3
import ipaddress
import os
import json
import argparse
import logging
import requests


from config import *

class Cache:
    ipv4 = ""
    ipv6 = ""

    def __init__(self,ipv4, ipv6):
        self.ipv4=ipv4
        self.ipv6=ipv6

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger("dyndns_update")




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





def get_ipv4():
    url = "https://api.ipify.org"
    response = None

    try:
        response = requests.get(url).text.strip()
    except:
        log.info(f"Can't get IPv4 address from {url}")
    
    if response:
        try:
            ipaddress.ip_address(response)
            log.info(f"IPv4 address from {url}: {response}")
        except:
            response = None
    return response


def get_ipv6():
    url = "https://api6.ipify.org"
    response = None

    try:
        response = requests.get(url).text.strip()
    except:
        log.info(f"Can't get IPv6 address from {url}")
    
    if response:
        try:
            ipaddress.ip_address(response)
            log.info(f"IPv6 address from {url}: {response}")
        except:
            response = None
    return response



def get_cache():
    try:
        with open('cache.json', 'r') as file:
            return json.loads(file.read())
    except:
        return {"ipv4": None, "ipv6": None}

def cache_isdifferent(old, new):
    changed = False
    if old["ipv4"] != new["ipv4"]:
        changed = True

    if old["ipv6"] != new["ipv6"]:
        changed = True
    
    return changed


def convert_to_dict(obj):
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    obj_dict.update(obj.__dict__)
    return obj_dict


def dict_to_obj(our_dict):
    if "__class__" in our_dict:
        class_name = our_dict.pop("__class__")
        module_name = our_dict.pop("__module__")
        module = __import__(module_name)
        class_ = getattr(module,class_name)
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj

def write_cache(obj):
    with open('cache.json', 'w') as outfile:
        outfile.write(json.dumps(obj))


def main():
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nocache', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    cached_ips = None

    if args.quiet:
        log.setLevel(logging.CRITICAL)
    log.info("dyndns_update.py started")

    os.chdir(basedir)
    fresh_ips = {"ipv4": get_ipv4(), "ipv6": get_ipv6()}

    if not args.nocache:
        log.info("getting cached IPs from cache.json")
        cached_ips = get_cache()
        log.info(f"cached IPv4: {cached_ips['ipv4']}")
        log.info(f"cached IPv6: {cached_ips['ipv6']}")
        if cache_isdifferent(cached_ips, fresh_ips):
            log.info("cached IPs differ from current ones. Updating cache")
            write_cache(fresh_ips)
        else:
            log.info("current IPs are already live, exiting.")
            if args.dry_run:
                log.info("DRY RUN: script would exit with code 0 here")
            else:
                exit(0)
    else:
        log.info("skipping cache due to '--nocache'.")
    
    log.info("Now the DNS records would be set ")
    if args.dry_run:
        log.info("EXCEPT for when --dry-run is set ;)")


        
        
    
    
    # if not args.nocache:
    #     try:
    #         cached_ips = get_cache()
    #     except:
    #         ""


if __name__ == "__main__":
    main()
