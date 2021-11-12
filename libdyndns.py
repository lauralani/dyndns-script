import json
import subprocess
import ipaddress
import time
import datetime
import pytz
import requests

class Cache:
    ipv4 = ""
    ipv6 = ""

    def __init__(self,ipv4, ipv6):
        self.ipv4=ipv4
        self.ipv6=ipv6

def get_cache():
    with open('cache.json', 'r') as file:
        return json.loads(file.read(), object_hook=dict_to_obj)

def cache_isdifferent(old, new):
    changed = False
    if old.ipv4 != new.ipv4:
        changed = True

    if old.ipv6 != new.ipv6:
        changed = True
    
    return changed


def convert_to_dict(obj):
  """
  A function takes in a custom object and returns a dictionary representation of the object.
  This dict representation includes meta data such as the object's module and class names.
  """
  
  #  Populate the dictionary with object meta data 
  obj_dict = {
    "__class__": obj.__class__.__name__,
    "__module__": obj.__module__
  }
  
  #  Populate the dictionary with object properties
  obj_dict.update(obj.__dict__)
  
  return obj_dict


def dict_to_obj(our_dict):
    """
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.
    """
    if "__class__" in our_dict:
        # Pop ensures we remove metadata from the dict to leave only the instance arguments
        class_name = our_dict.pop("__class__")
        
        # Get the module name from the dict and import it
        module_name = our_dict.pop("__module__")
        
        # We use the built in __import__ function since the module name is not yet known at runtime
        module = __import__(module_name)
        
        # Get the class from the module
        class_ = getattr(module,class_name)
        
        # Use dictionary unpacking to initialize the object
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj

# def get_currentips():
#     url4 = "https://api.ipify.org"
#     url6 = "https://api6.ipify.org"
#     ipv6_new = str(subprocess.run(['/usr/bin/curl', '-6', "-s", url6], stdout=subprocess.PIPE).stdout, encoding="utf-8").strip()
#     try:
#         ipaddress.ip_address(ipv6_new)
#     except:
#         ipv6_new = ""

#     ipv4_new = str(subprocess.run(['/usr/bin/curl', '-4', "-s", url4], stdout=subprocess.PIPE).stdout, encoding="utf-8").strip()
#     try:
#         ipaddress.ip_address(ipv4_new)
#     except:
#         ipv4_new = ""
#     return Cache(ipv4=ipv4_new, ipv6=ipv6_new)

def write_currentips(obj):
    with open('cache.json', 'w') as outfile:
        outfile.write(json.dumps(obj, default=convert_to_dict))

def ts():
    return f"{datetime.datetime.now(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S')}: "

def get_ipv4():
    url4 = "https://api.ipify.org"

    ipv4 = requests.get(url4).text.strip()
    response = ""
    try:
        response = ipaddress.ip_address(ipv4)
    except:
        response = ""
    return response

def get_ipv6():
    url6 = "https://api6.ipify.org"

    ipv6 = requests.get(url6).text.strip()
    response = ""
    try:
        response = ipaddress.ip_address(ipv6)
    except:
        response = ""
    return response
