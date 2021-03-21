import json
import subprocess

def OVH_get_zonerecord(client, zone, type, subdomain):
    result = client.get(f"/domain/zone/{zone}/record", fieldType=type, subDomain=subdomain)
    return result[0]

def OVH_set_zonerecord(client, zone, type, subdomain, target, ttl):
    id = get_zonerecord(client=client, zone=zone, type=type, subdomain=subdomain)
    result = client.put(f'/domain/zone/{zone}/record/{id}', 
        subDomain=subdomain, target=target, ttl=ttl
    )
    client.post(f'/domain/zone/{zone}/refresh')
