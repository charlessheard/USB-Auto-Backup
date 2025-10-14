#!/usr/bin/env python3
import subprocess
import time
import shutil
import logging
import os
from typing import List, Tuple
from pathlib import Path

# Configuration
TARGET_FOLDER = Path("/home/carlos/USB_Backup/")
EXCLUDED_FOLDERS = {"Backup_drv", "data"}
SLEEP_INTERVAL = 15  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/carlos/USB_Backup/usb_backup.log'),
        logging.StreamHandler()
    ]
)

def get_mounted_usb_devices() -> List[Tuple[str, str]]:
    """Get list of mounted USB devices using lsblk with reliable filtering."""
    try:
        # Use lsblk with JSON output for more reliable parsing
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,MOUNTPOINT"],
            capture_output=True,
            text=True,
            check=True
        )

        import json
        devices = json.loads(result.stdout)

        usb_devices = []
        for device in devices['blockdevices']:
            # Check if this is a USB device and has mount points
            if device_has_usb_connection(device):
                usb_devices.extend(get_mount_points_from_device(device))

        return usb_devices

    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Failed to get mounted devices: {e}")
        return []

def device_has_usb_connection(device) -> bool:
    """Check if device is connected via USB."""
    try:
        if 'children' in device:
            for child in device['children']:
                if device_has_usb_connection(child):
                    return True

        # Check this device's USB status
        if device['name'].startswith(('sd', 'mmcblk')):
            check_cmd = f"udevadm info -q property -n /dev/{device['name']}"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            return "ID_BUS=usb" in result.stdout
        return False

    except Exception as e:
        logging.debug(f"Could not check USB status for {device.get('name', 'unknown')}: {e}")
        return False

def get_mount_points_from_device(device) -> List[Tuple[str, str]]:
    """Extract mount points from device structure."""
    mount_points = []

    def extract_mounts(dev, prefix=""):
        if dev.get('mountpoint') and dev['mountpoint'] not in ['/', '/boot']:
            mount_points.append((prefix + dev['name'], dev['mountpoint']))
        if 'children' in dev:
            for child in dev['children']:
                extract_mounts(child, prefix)

    extract_mounts(device)
    return mount_points

def backup_device(source: Path, target: Path) -> bool:
    """Backup a device to the target location."""
    try:
        if target.exists():
            logging.info(f"Removing existing backup: {target}")
            shutil.rmtree(target)

        logging.info(f"Starting backup from {source} to {target}")
        shutil.copytree(source, target)
        logging.info(f"Backup completed successfully: {target}")
        return True

    except Exception as e:
        logging.error(f"Backup failed for {source}: {e}")
        return False

def main():
    """Main backup routine."""
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    processed_devices = set()

    logging.info("USB Backup Service Started - Improved Version")

    while True:
        try:
            current_devices = get_mounted_usb_devices()

            # Find new devices that haven't been processed
            new_devices = [
                dev for dev in current_devices
                if dev not in processed_devices
                and Path(dev[1]).name not in EXCLUDED_FOLDERS
            ]

            for device_name, mount_point in new_devices:
                source = Path(mount_point)
                target = TARGET_FOLDER / source.name

                if backup_device(source, target):
                    processed_devices.add((device_name, mount_point))
                    logging.info(f"Successfully processed {device_name} at {mount_point}")

            # Update processed devices to only include currently mounted ones
            processed_devices = {dev for dev in processed_devices if dev in current_devices}

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")

        finally:
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
