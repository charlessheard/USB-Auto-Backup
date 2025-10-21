#!/usr/bin/env python3
import subprocess
import time
import shutil
import logging
import os
import json
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
    """Get list of mounted USB devices using reliable method."""
    try:
        # Method 1: Use lsblk with transport filter (more reliable)
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,MOUNTPOINT,TRAN"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        devices_data = json.loads(result.stdout)
        usb_devices = []

        for device in devices_data.get('blockdevices', []):
            # Check if device is USB by transport type
            if device.get('tran') == 'usb':
                # Get all mount points from this device and its children
                mount_points = get_mount_points_from_device(device)
                usb_devices.extend([(device['name'], mp) for mp in mount_points])
            elif 'children' in device:
                # Check children devices
                for child in device['children']:
                    if child.get('tran') == 'usb' and child.get('mountpoint'):
                        usb_devices.append((child['name'], child['mountpoint']))

        # Method 2: Alternative approach using df and udev
        if not usb_devices:
            usb_devices = get_usb_devices_alternative()

        logging.debug(f"Found USB devices: {usb_devices}")
        return usb_devices

    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, subprocess.TimeoutExpired) as e:
        logging.error(f"Failed to get mounted devices: {e}")
        return []

def get_usb_devices_alternative() -> List[Tuple[str, str]]:
    """Alternative method to find USB devices."""
    usb_devices = []
    try:
        # Get all mounted filesystems
        result = subprocess.run(
            ["df", "--output=source,target"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        for line in result.stdout.splitlines()[1:]:  # Skip header
            parts = line.split()
            if len(parts) == 2:
                device, mountpoint = parts
                # Check if device is USB
                if is_usb_device(device):
                    usb_devices.append((device.split('/')[-1], mountpoint))

    except Exception as e:
        logging.error(f"Alternative USB detection failed: {e}")

    return usb_devices

def is_usb_device(device_path: str) -> bool:
    """Check if a device is USB using udev with timeout."""
    try:
        # Extract device name (e.g., /dev/sdb1 -> sdb1)
        device_name = device_path.split('/')[-1]

        # Check if it's a USB device using udev
        cmd = f"udevadm info -q property -n /dev/{device_name}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        return "ID_BUS=usb" in result.stdout

    except Exception as e:
        logging.debug(f"Could not check USB status for {device_path}: {e}")
        return False

def get_mount_points_from_device(device) -> List[str]:
    """Extract mount points from device structure."""
    mount_points = []

    def extract_mounts(dev):
        if dev.get('mountpoint') and dev['mountpoint']:
            # Skip system mount points
            if dev['mountpoint'] not in ['/', '/boot', '/home', '/var', '/tmp']:
                mount_points.append(dev['mountpoint'])
        if 'children' in dev:
            for child in dev['children']:
                extract_mounts(child)

    extract_mounts(device)
    return mount_points

def backup_device(source: Path, target: Path) -> bool:
    """Backup a device to the target location."""
    try:
        if not source.exists():
            logging.error(f"Source path does not exist: {source}")
            return False

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

    logging.info("USB Backup Service Started - Fixed Version")
    logging.info(f"Target folder: {TARGET_FOLDER}")
    logging.info(f"Excluded folders: {EXCLUDED_FOLDERS}")

    while True:
        try:
            current_devices = get_mounted_usb_devices()
            logging.info(f"Current USB devices found: {len(current_devices)}")

            # Find new devices that haven't been processed
            new_devices = [
                dev for dev in current_devices
                if dev not in processed_devices
                and Path(dev[1]).name not in EXCLUDED_FOLDERS
            ]

            if new_devices:
                logging.info(f"New USB devices to process: {new_devices}")

            for device_name, mount_point in new_devices:
                source = Path(mount_point)
                target = TARGET_FOLDER / source.name

                if backup_device(source, target):
                    processed_devices.add((device_name, mount_point))
                    logging.info(f"Successfully processed {device_name} at {mount_point}")
                else:
                    logging.error(f"Failed to process {device_name} at {mount_point}")

            # Update processed devices to only include currently mounted ones
            processed_devices = {dev for dev in processed_devices if dev in current_devices}

        except KeyboardInterrupt:
            logging.info("Service stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")

        finally:
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
