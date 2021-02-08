#!/usr/bin/env python3

import subprocess
import ovh
import json
from libdyndns import *

domain = "r33x7yrdm1do6s0hqmt4.ovh"
subdomain = "mx00"

with open('config.json', 'r') as file:
    config = json.load(file)

cached_ips = get_cache()
new_ips = get_currentips()


if not cache_isdifferent(cached_ips, new_ips):
    exit()
else:
    write_currentips(new_ips)


client = ovh.Client(
    endpoint='ovh-eu',               # Endpoint of API OVH Europe (List of available endpoints)
    application_key=f'{config["ovh"]["appkey"]}',    # Application Key
    application_secret=f'{config["ovh"]["appsecret"]}', # Application Secret
    consumer_key=f'{config["ovh"]["consumerkey"]}',       # Consumer Key
)


set_zonerecord(client, domain, "AAAA", subdomain, new_ips.ipv6, 60)
set_zonerecord(client, domain, "A", subdomain, new_ips.ipv4, 60)
