#!/usr/bin/env python3
import ipaddress
import os
import json
import argparse
import logging
import requests


from config import *
from azure.mgmt.dns import DnsManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.identity import ClientSecretCredential


class Cache:
    ipv4 = ""
    ipv6 = ""

    def __init__(self, ipv4, ipv6):
        self.ipv4 = ipv4
        self.ipv6 = ipv6


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger("dyndns_update")
log.setLevel(logging.INFO)


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


def split_fqdn(fqdn):
    split = fqdn.rsplit('.', 2)
    return {
        "fqdn": fqdn,
        "record": split[0],
        "zone": '.'.join(split[1:3])
    }

def write_cache(obj):
    with open('cache.json', 'w') as outfile:
        outfile.write(json.dumps(obj))


def main():
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nocache', action='store_true', help="Disable checking the cache and just update the records.")
    parser.add_argument('-d', '--dry-run', action='store_true', help="Just simulate the script, dont actually change records. NOT IMPLEMENTED YET!")
    parser.add_argument('-q', '--quiet', action='store_true', help="Run without logging/output. (useful for cron, etc...)")
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

    # azureidentity = {
    #     "subscriptionid":  "",
    #     "tenantid":  "",
    #     "clientid":  "",
    #     "clientsecret":  ""
    # }
    log.info("Trying to authenticate with Azure credentials...")
    az_credentials = ClientSecretCredential(
        tenant_id=azureidentity["tenantid"], client_id=azureidentity["clientid"], client_secret=azureidentity["clientsecret"])
    az_dns_client = DnsManagementClient(
        az_credentials, azureidentity["subscriptionid"])
    log.info("Authentication: Success")

    for domain in domains:
        fqdn = split_fqdn(domain)
        az_domain = None
        log.info(f"{domain} wants {domains[domain]}")

        log.info(f"Requesting Domain {fqdn['fqdn']} from Azure")
        try:
            az_domain = az_dns_client.zones.get(
                azureidentity['dns_rg_name'], fqdn['zone'])
        except:
            log.info(
                f"Domain {fqdn['zone']} doesn't exist in RG {azureidentity['dns_rg_name']} or I can't access it!")
            log.info(f"skipping {fqdn['fqdn']} due to previous errors!")
            continue
        if domains[domain] == "ipv4" or domains[domain] == "both":
            if fresh_ips['ipv4']:
                log.info(f"Add record: {fqdn['fqdn']} 300 IN A {fresh_ips['ipv4']}")
                az_dns_client.record_sets.create_or_update(
                    resource_group_name=azureidentity['dns_rg_name'],
                    zone_name=fqdn['zone'],
                    relative_record_set_name=fqdn['record'],
                    record_type="A",
                    parameters={
                        "ttl": 300,
                        "arecords": [
                            {"ipv4_address": fresh_ips['ipv4']}
                        ]
                    }
                )
            else:
                log.info(f"Can't change/add IPv4 for {fqdn['fqdn']}: no IPv4!")

        if domains[domain] == "ipv6" or domains[domain] == "both":
            if fresh_ips['ipv6']:
                log.info(f"Add record: {fqdn['fqdn']} 300 IN AAAA {fresh_ips['ipv6']}")
                az_dns_client.record_sets.create_or_update(
                    resource_group_name=azureidentity['dns_rg_name'],
                    zone_name=fqdn['zone'],
                    relative_record_set_name=fqdn['record'],
                    record_type="AAAA",
                    parameters={
                        "ttl": 300,
                        "aaaarecords": [
                            {"ipv6_address": fresh_ips['ipv6']}
                        ]
                    }
                )
            else:
                log.info(f"Can't change/add IPv6 for {fqdn['fqdn']}: no IPv6!")


if __name__ == "__main__":
    main()
