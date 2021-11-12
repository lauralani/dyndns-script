# dyndns-script
## Prerequisites
```
dnf module -y install python39
python3 python3-pip

pip3 install --upgrade pip
pip3 install pytz requests azure-mgmt-dns azure-identity
```


## config.py
`config.py`:


```python
azureidentity = {
    "subscriptionid":  "",
    "tenantid":  "",
    "clientid":  "",
    "clientsecret":  ""
}

# valid entries: ipv6, ipv4, both
domains = {
    'subdomain.example.com': 'ipv6',
}

basedir = "/root/dyndns-script"
```

## crontab
```
*/10 * * * * /root/dyndns-script/dyndns_update.py -4 -6 >> /var/log/dyndns.log
```

## references
https://docs.microsoft.com/en-us/python/api/overview/azure/dns?view=azure-python

https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?view=azure-python
