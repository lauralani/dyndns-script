# dyndns-script
## Prerequisites
```
python3 python3-pip

pip3 install --upgrade pip
pip3 install pytz requests
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
