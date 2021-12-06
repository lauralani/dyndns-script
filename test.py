#!/usr/bin/env python3
import ipaddress
import os
import json
import argparse
import logging
import requests
import ovh
from config import *


domain = "cutielasura.eu"
subdomain = "a.test.gone"
recordtype = "AAAA"

ovh_dns_client = ovh.Client(
            endpoint=secrets['ovh']['endpoint'],
            application_key=secrets['ovh']['application_key'],
            application_secret=secrets['ovh']['application_secret'],
            consumer_key=secrets['ovh']['consumer_key']
        )


zone       = ovh_dns_client.get(f"/domain/zone/{domain}")
zonerecord = ovh_dns_client.get(f"/domain/zone/{domain}/record", fieldType=recordtype, subDomain=subdomain)

print("*")
