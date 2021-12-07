#!/usr/bin/env python3
import ipaddress
import os
import json
import argparse
import logging
import requests
import ovh

from config import *
from azure.mgmt.dns import DnsManagementClient
from azure.identity import ClientSecretCredential
from enum import Enum


class IPVariant(Enum):
    ipv4 = 1
    ipv6 = 2
    both = 3


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger("dyndns_update")
log.setLevel(logging.INFO)


def get_ip(version : IPVariant):
    url = None
    response = None

    if version == IPVariant['ipv4']:
        url = "https://api.ipify.org"
    elif version == IPVariant['ipv6']:
        url = "https://api6.ipify.org"

    try:
        response = requests.get(url).text.strip()
    except:
        log.info(f"Can't get {version.name} address from {url}")

    if response:
        try:
            ipaddress.ip_address(response)
            log.info(f"{version.name} address from {url}: {response}")
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


def update_dns_azure(dnsclient: DnsManagementClient, fqdn: str, ipaddress: str, ipvariant: IPVariant, resourcegroup : str):
    splitfqdn = split_fqdn(fqdn)
    az_domain, recordtype, recordarray = None, None, None

    if ipvariant == IPVariant['ipv4']:
        recordtype = 'A'
        recordarray = 'arecords'
    elif ipvariant == IPVariant['ipv6']:
        recordtype = 'AAAA'
        recordarray = 'aaaarecords'
    else:
        log.error(f"AZURE: weird parameter {ipvariant} in update_dns_azure(), aborting this fqdn")
        return 1


    try:
        az_domain = dnsclient.zones.get(
            resource_group_name=resourcegroup,
            zone_name=splitfqdn['zone']
        )
    except:
        log.error(
            f"AZURE: Domain {splitfqdn['zone']} doesn't exist in RG {resourcegroup} or I can't access it!"
        )
        log.info(f"AZURE: skipping {splitfqdn['fqdn']} due to previous errors!")
        return 1

    log.info(f"AZURE: Add record: {splitfqdn['fqdn']} 300 IN {recordtype} {ipaddress}")
    dnsclient.record_sets.create_or_update(
        resource_group_name=resourcegroup,
        zone_name=splitfqdn['zone'],
        relative_record_set_name=splitfqdn['record'],
        record_type=recordtype,
        parameters={
            "ttl": 300,
            f"{recordarray}" : [
                {f"{ipvariant.name}_address": ipaddress}
            ]
        }
    )

def update_dns_ovh(dnsclient: ovh.Client, fqdn: str, ipaddress: str, ipvariant: IPVariant):
    splitfqdn = split_fqdn(fqdn)
    recordtype = None

    if ipvariant == IPVariant['ipv4']:
        recordtype = 'A'
    elif ipvariant == IPVariant['ipv6']:
        recordtype = 'AAAA'
    else:
        log.error(f"OVH: weird parameter {ipvariant} in update_dns_ovh(), aborting this fqdn")
        return 1

    try:
        dnsclient.get(f"/domain/zone/{splitfqdn['zone']}")
    except:
        log.error(
            f"OVH: Domain {splitfqdn['zone']} doesn't exist in this OVH account, or I can't access it!"
        )
        log.info(f"OVH: skipping {splitfqdn['fqdn']} due to previous errors!")
        return 1
    ovhrecords = dnsclient.get(f"/domain/zone/{splitfqdn['zone']}/record", fieldType=recordtype, subDomain=splitfqdn['record'])

    if len(ovhrecords) > 1:
        log.error(f"OVH: please fix DNS config for {splitfqdn['zone']}, there is more than one record for {splitfqdn['fqdn']}!")
        log.info(f"OVH: skipping {splitfqdn['fqdn']} due to previous errors!")
        return 1
    
    if len(ovhrecords) == 1:
        log.info(f"OVH: Modify record: {splitfqdn['fqdn']} 300 IN {recordtype} {ipaddress}")
        dnsclient.put(f"/domain/zone/{splitfqdn['zone']}/record/{ovhrecords[0]}", 
            subDomain=splitfqdn['record'], 
            target=ipaddress, 
            ttl=300
        )
    else:
        log.info(f"OVH: Add record: {splitfqdn['fqdn']} 300 IN {recordtype} {ipaddress}")

        dnsclient.post(f"/domain/zone/{splitfqdn['zone']}/record", 
            fieldType=recordtype,
            subDomain=splitfqdn['record'],
            target=ipaddress,
            ttl=300
        )
    
    
    log.info(f"OVH: Refreshing zone: {splitfqdn['zone']}")
    dnsclient.post(f"/domain/zone/{splitfqdn['zone']}/refresh")

def send_info(provider: str, ip4: str, ip6: str, fqdn: str):
    try:
        info
    except:
        return 1

    import socket
    payload = {
        "provider" : provider,
        "ip4" : ip4,
        "ip6" : ip6,
        "fqdn" : fqdn,
        "hostname" : socket.gethostname()
    }
    headers = {
        'X-ApiKey': info['apikey'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", info['endpoint'], headers=headers, data=json.dumps(payload))



def main():
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nocache', action='store_true',
                        help="Disable checking the cache and just update the records.")
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help="Just simulate the script, dont actually change records. NOT IMPLEMENTED YET!")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run without logging/output. (useful for cron, etc...)")
    args = parser.parse_args()

    cached_ips = None

    if args.quiet:
        log.setLevel(logging.CRITICAL)
    log.info("dyndns_update.py started")

    os.chdir(basedir)
    fresh_ips = {"ipv4": get_ip(IPVariant['ipv4']), "ipv6": get_ip(IPVariant['ipv6'])}

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

    if args.dry_run:
        log.info("EXCEPT for when --dry-run is set ;)")

    if domains['azure']:
        log.info("Trying to authenticate with Azure credentials...")
        az_dns_client = DnsManagementClient(
            credential=ClientSecretCredential(
                tenant_id=secrets['azure']["tenantid"], 
                client_id=secrets['azure']["clientid"], 
                client_secret=secrets['azure']["clientsecret"]
            ), 
            subscription_id=secrets['azure']["subscriptionid"]
        )
        log.info("Authentication: Success")
        for domain in domains['azure']:
            domain_wants = IPVariant[domains['azure'][domain].lower()]
            log.info(f"AZURE: {domain} wants {domains['azure'][domain]}")

            if domain_wants == IPVariant['both']:
                update_dns_azure(
                    dnsclient=az_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips["ipv4"],
                    ipvariant=IPVariant['ipv4'],
                    resourcegroup=secrets['azure']['dns_rg_name']
                )
                update_dns_azure(
                    dnsclient=az_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips["ipv6"],
                    ipvariant=IPVariant['ipv6'],
                    resourcegroup=secrets['azure']['dns_rg_name']
                )
            else:
                update_dns_azure(
                    dnsclient=az_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips[domain_wants.name],
                    ipvariant=domain_wants,
                    resourcegroup=secrets['azure']['dns_rg_name']
                )

    if domains['ovh']:
        ovh_dns_client = ovh.Client(
            endpoint=secrets['ovh']['endpoint'],
            application_key=secrets['ovh']['application_key'],
            application_secret=secrets['ovh']['application_secret'],
            consumer_key=secrets['ovh']['consumer_key']
        )
        for domain in domains['ovh']:
            domain_wants = IPVariant[domains['ovh'][domain].lower()]
            log.info(f"OVH: {domain} wants {domains['ovh'][domain]}")

            if domain_wants == IPVariant['both']:
                # To Do from here
                update_dns_ovh(
                    dnsclient=ovh_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips["ipv4"],
                    ipvariant=IPVariant['ipv4']
                )
                update_dns_ovh(
                    dnsclient=ovh_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips["ipv6"],
                    ipvariant=IPVariant['ipv6']
                )
            else:
                update_dns_ovh(
                    dnsclient=ovh_dns_client,
                    fqdn=domain,
                    ipaddress=fresh_ips[domain_wants.name],
                    ipvariant=domain_wants
                )


if __name__ == "__main__":
    main()
