# dyndns-script
## Prerequisites
```
dnf module -y install python39
python3 python3-pip

pip3 install --upgrade pip
pip3 install pytz requests azure-mgmt-dns
```


## config.py
`config.py`:


```python
# Domain for API call
domain =  "test-01.itxxxxxx.xxx"

# API key for API call
apikey =  "b11111c1-1111-1111-1115-480e1111111c"

# script root folder
basedir = "/root/dyndns-script"
```

## crontab
```
*/10 * * * * /root/dyndns-script/dyndns_update.py -4 -6 >> /var/log/dyndns.log
```

## references
https://docs.microsoft.com/en-us/python/api/overview/azure/dns?view=azure-python

https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?view=azure-python
