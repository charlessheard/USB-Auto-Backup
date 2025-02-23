#!/usr/bin/env python3
import subprocess
import time
import logging
import os
from pathlib import Path
import psutil
from typing import List, Tuple

TARGET_FOLDER = Path("/home/user/USB_Backup/")
EXCLUDED_FOLDERS = {"Backup_drv", "data"}
SLEEP_INTERVAL = 15

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/usb_backup.log'),
        logging.StreamHandler()
    ]
)

def get_mountedlist() -> List[Tuple[str, str]]:
    try:
        partitions = psutil.disk_partitions()
        devices = [(p.device, p.mountpoint) for p in partitions if p.mountpoint]
        logging.info(f"Detected devices: {devices}")
        return devices
    except Exception as e:
        logging.error(f"Failed to get mounted devices: {e}")
        return []

def is_removable(device: str) -> bool:
    """Check if a device is removable using lsblk."""
    try:
        result = subprocess.run(
            ["lsblk", "-dno", "RM", device],
            capture_output=True, text=True, check=True
        )
        removable = result.stdout.strip() == "1"
        logging.debug(f"Device {device} removable status: {removable}")
        return removable
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check if {device} is removable: {e}")
        return False

def identify(device: str, mountpoint: str) -> bool:
    """Identify if a device is a USB drive."""
    try:
        # Must be under /run/media/ (KDE default for removable media)
        if not mountpoint.startswith("/run/media/"):
            logging.info(f"Device {device} at {mountpoint} identified as USB: False (not under /run/media/)")
            return False

        # Exclude NVMe devices (internal drives)
        if device.startswith("/dev/nvme"):
            logging.info(f"Device {device} at {mountpoint} identified as USB: False (NVMe excluded)")
            return False

        # Check if the device is removable (USB drives typically are)
        is_usb = is_removable(device)
        logging.info(f"Device {device} at {mountpoint} identified as USB: {is_usb}")
        return is_usb
    except Exception as e:
        logging.error(f"Failed to identify device {device}: {e}")
        return False

def backup_device(source: Path, target: Path) -> None:
    try:
        if target.exists():
            logging.info(f"Target {target} exists; performing incremental backup.")
        else:
            target.mkdir(parents=True)

        logging.info(f"Starting backup from {source} to {target}")
        subprocess.run(
            ["rsync", "-av", "--delete", f"{source}/", f"{target}/"],
            check=True
        )
        logging.info(f"Backup completed successfully: {target}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Backup failed for {source}: rsync error - {e}")
    except Exception as e:
        logging.error(f"Unexpected error during backup: {e}")

def main():
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    processed_devices = set()

    while True:
        try:
            mounted = get_mountedlist()
            new_devices = [
                (dev, mnt) for dev, mnt in mounted
                if (dev, mnt) not in processed_devices and mnt != "/"
            ]

            for device, mountpoint in new_devices:
                if identify(device, mountpoint) and mountpoint.split("/")[-1] not in EXCLUDED_FOLDERS:
                    source = Path(mountpoint)
                    target = TARGET_FOLDER / source.name
                    backup_device(source, target)
                    processed_devices.add((device, mountpoint))

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    logging.info("USB Backup Service Started")
    main()
