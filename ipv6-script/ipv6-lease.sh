#!/bin/bash

sleep 20

/usr/sbin/dhclient -6 -r &>/dev/null 
/usr/sbin/dhclient -6 &>/dev/null
