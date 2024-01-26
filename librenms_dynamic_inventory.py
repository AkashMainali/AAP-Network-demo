#!/usr/bin/env python
#Script uses requests library, if not installed we can use pip install requests
import requests
import json
import sys

# LibreNMS API settings
LIBRENMS_API_URL = "https://ny5-pr-netlibre-01.prod.schonfeld.com/api/v0"
LIBRENMS_API_TOKEN = "019efefd4c7290aaf1b48c7d7f5c4a10"

# Ansible dynamic inventory dictionary
ansible_inventory = {"all": {"hosts": [], "vars": {}}, "_meta": {"hostvars": {}}}

def get_librenms_devices():
    try:
        headers = {"Authorization": f"Bearer {LIBRENMS_API_TOKEN}"}
        response = requests.get(f"{LIBRENMS_API_URL}devices", headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        devices = response.json()
        return devices
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LibreNMS API: {e}")
        sys.exit(1)

def populate_ansible_inventory(devices):
    for device in devices:
        hostname = device["hostname"]
        ip_address = device.get("ipv4", "")  # Use empty string if IPv4 is not available
        device_groups = device.get("groups", [])

        # Add the host to the 'all' group
        ansible_inventory["all"]["hosts"].append(hostname)

        # Populate hostvars with additional information (if needed)
        ansible_inventory["_meta"]["hostvars"][hostname] = {"ansible_host": ip_address, "groups": device_groups}

        # Add the host to specific groups based on device attributes (e.g., device groups in LibreNMS)
        for group in device_groups:
            if group not in ansible_inventory:
                ansible_inventory[group] = {"hosts": []}
            ansible_inventory[group]["hosts"].append(hostname)

if __name__ == "__main__":
    librenms_devices = get_librenms_devices()
    populate_ansible_inventory(librenms_devices)

    print(json.dumps(ansible_inventory, indent=2))
