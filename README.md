USB Backup Service
A Python-based automated backup service that monitors for USB device connections and automatically creates backups of mounted USB storage devices.

Features
Automatic Detection: Continuously monitors for newly mounted USB devices

Smart Filtering: Excludes system directories and specified folders from backup

Reliable Identification: Uses lsblk with JSON parsing and udevadm for accurate USB device detection

Incremental Processing: Tracks processed devices to avoid duplicate backups

Comprehensive Logging: Detailed logging to both file and console output

Configurable: Easy to modify target directories, exclusions, and scan intervals

How It Works
Device Monitoring: Scans for mounted USB devices every 15 seconds (configurable)

USB Verification: Uses udev properties to confirm USB connection and avoid system partitions

Backup Creation: Creates complete copies of USB device contents to the target directory

Clean Management: Removes existing backups before creating new ones to prevent conflicts

Configuration
TARGET_FOLDER: Backup destination directory (/home/carlos/USB_Backup/)

EXCLUDED_FOLDERS: Folders to skip during backup (Backup_drv, data)

SLEEP_INTERVAL: Seconds between device scans (15)

Usage
bash
python3 usb_backup_service.py
The service runs continuously, automatically backing up any USB storage devices when they're connected.

Requirements
Python 3.6+

Linux system with lsblk and udevadm utilities

Appropriate permissions for device monitoring and file operations

Use Cases
Automated backup solutions for removable media

Data preservation for photography, document transfer, or device migration

Archival systems for frequently connected USB devices

Perfect for users who regularly work with USB drives and need reliable, automated backup without manual intervention.
