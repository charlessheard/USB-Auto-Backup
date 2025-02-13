#!/usr/bin/env python3
import subprocess
import time
import shutil
import logging
import os
from typing import List, Tuple, Optional
from pathlib import Path

# Configuration
TARGET_FOLDER = Path("Enter/location/to/store/backups")
EXCLUDED_FOLDERS = {"Backup", "data"}  # Using a set for O(1) lookup
SLEEP_INTERVAL = 15  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('usb_backup.log'),
        logging.StreamHandler()
    ]
)

def get_mountedlist() -> List[Tuple[str, str]]:
    """Get list of mounted devices and their mount points."""
    try:
        output = subprocess.run(
            ["lsblk"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout
        return [
            (
                item.split()[0].replace("├─", "").replace("└─", ""),
                item[item.find("/"):]
            )
            for item in output.split("\n")
            if "/" in item
        ]
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get mounted devices: {e}")
        return []

def identify(disk: str) -> bool:
    """Check if the given disk is a USB device."""
    try:
        command = f"find /dev/disk -ls | grep /{disk}"
        output = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        ).stdout
        return "usb" in output.lower()
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to identify disk {disk}: {e}")
        return False

def backup_device(source: Path, target: Path) -> None:
    """Backup a device to the target location."""
    try:
        if target.exists():
            shutil.rmtree(target)
        
        logging.info(f"Starting backup from {source} to {target}")
        shutil.copytree(source, target)
        logging.info(f"Backup completed successfully: {target}")
    
    except Exception as e:
        logging.error(f"Backup failed for {source}: {e}")

def main():
    """Main backup routine."""
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    done = []
    
    while True:
        try:
            mounted = get_mountedlist()
            new_paths = [
                dev for dev in mounted 
                if dev not in done and dev[1] != "/"
            ]
            
            valid = [
                dev for dev in new_paths
                if identify(dev[0]) and dev[1].split("/")[-1] not in EXCLUDED_FOLDERS
            ]
            
            for device in valid:
                source = Path(device[1])
                target = TARGET_FOLDER / source.name
                backup_device(source, target)
            
            done = mounted
            
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
        
        finally:
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    logging.info("USB Backup Service Started")
    main()
