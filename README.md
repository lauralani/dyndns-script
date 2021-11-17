# dyndns-script
## Prerequisites
```
dnf module -y install python39
python3 python3-pip

pip3 install --upgrade pip
pip3 install pytz requests azure-mgmt-dns azure-identity azure-mgmt-resource ovh
```


## config.py
`config.py`:


```python
secrets = {
    'azure': {
        "subscriptionid":  "",
        "tenantid":  "",
        "clientid":  "",
        "clientsecret":  ""
    }, 
    'ovh': {
        'endpoint' : 'ovh-eu',
        'application_key' : '',
        'application_secret' : '',
        'consumer_key' : ''
    }
}

# valid entries: ipv6, ipv4, both
domains = {
    'azure': {
        'ipv4.dyndns..example.com': 'ipv4',
        'ipv6.dyndns.example.com': 'ipv6',
        '@.example.com': 'both',
    },
    'ovh': {}
}

basedir = "/root/dyndns-script"
```

## crontab
```
*/10 * * * * /root/dyndns-script/dyndns_update.py --quiet
```

## references
https://docs.microsoft.com/en-us/python/api/overview/azure/dns?view=azure-python

https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?view=azure-python
