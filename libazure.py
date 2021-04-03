import requests

def AZURE_update_zonerecord(domain, apikey, ipaddress):
    response = requests.get(f'https://api.lauka.space/dyndns/{ipaddress}', auth=(domain, apikey))
    
    if not response.text == f"200 {ipaddress}":
        print(f"Error setting IP address {ipaddress} for domain {domain}")
        return(False)
    else:
        #print(response.text)
        return(True)

class AZURE_DYNDNS:
    IPv4 = ""
    IPv6 = ""
