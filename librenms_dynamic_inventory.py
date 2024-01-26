#!/usr/bin/env python
import requests
import json
import sys

# LibreNMS API settings
LIBRENMS_API_URL = "https://ny5-pr-netlibre-01.prod.schonfeld.com/api/v0/"
LIBRENMS_API_TOKEN = "019efefd4c7290aaf1b48c7d7f5c4a10"

# Ansible dynamic inventory dictionary
ansible_inventory = {"all": {"hosts": [], "vars": {}}, "_meta": {"hostvars": {}}}

def get_librenms_devices():
    try:
        headers = {"Authorization": f"Bearer {LIBRENMS_API_TOKEN}"}
        response = requests.get(f"{LIBRENMS_API_URL}devices", headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        print response.json()
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
        region = device.get("region", "Unknown")
        device_type = device.get("type", "Unknown")
        site = device.get("site", "Unknown")
        vendor = device.get("vendor", "Unknown")
        model = device.get("hardware", "Unknown")

        # Add the host to the 'all' group
        ansible_inventory["all"]["hosts"].append(hostname)

        # Populate hostvars with additional information
        ansible_inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": ip_address,
            "groups": device_groups,
            "region": region,
            "type": device_type,
            "site": site,
            "vendor": vendor,
            "model": model,
        }

        # Add the host to specific groups based on device attributes
        for group in device_groups:
            if group not in ansible_inventory:
                ansible_inventory[group] = {"hosts": []}
            ansible_inventory[group]["hosts"].append(hostname)

        # Add the host to region-based groups
        if region not in ansible_inventory:
            ansible_inventory[region] = {"hosts": []}
        ansible_inventory[region]["hosts"].append(hostname)

        # Add the host to type-based groups
        if device_type not in ansible_inventory:
            ansible_inventory[device_type] = {"hosts": []}
        ansible_inventory[device_type]["hosts"].append(hostname)

        # Add the host to site-based groups
        if site not in ansible_inventory:
            ansible_inventory[site] = {"hosts": []}
        ansible_inventory[site]["hosts"].append(hostname)

        # Add the host to vendor-based groups
        if vendor not in ansible_inventory:
            ansible_inventory[vendor] = {"hosts": []}
        ansible_inventory[vendor]["hosts"].append(hostname)

        # Add the host to model-based groups
        if model not in ansible_inventory:
            ansible_inventory[model] = {"hosts": []}
        ansible_inventory[model]["hosts"].append(hostname)

if __name__ == "__main__":
    librenms_devices = get_librenms_devices()
    populate_ansible_inventory(librenms_devices)

    print(json.dumps(ansible_inventory, indent=2))