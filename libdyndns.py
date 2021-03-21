import json
import subprocess

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

def get_currentips():
    url = "https://ifconfig.co/ip"
    ipv6_new = subprocess.run(['/usr/bin/curl', '-6', "-s", url], stdout=subprocess.PIPE).stdout
    ipv4_new = subprocess.run(['/usr/bin/curl', '-4', "-s", url], stdout=subprocess.PIPE).stdout

    return Cache(ipv4=str(ipv4_new, encoding="utf-8").strip(), ipv6=(str(ipv6_new, encoding="utf-8")).strip())

def write_currentips(obj):
    with open('cache.json', 'w') as outfile:
        outfile.write(json.dumps(obj, default=convert_to_dict))
    print("wrote cache")
