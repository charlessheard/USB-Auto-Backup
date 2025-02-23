# USB Backup Script

A Python script that automatically detects and backs up USB drives to a specified folder on Arch Linux (or similar systems) using `rsync`. Designed to run continuously, it monitors for new USB insertions and performs incremental backups, excluding internal drives like NVMe or HDDs.

## Features
- Detects removable USB drives using `psutil` and `lsblk`.
- Backs up USB contents to `/home/carlos/USB_Backup/` with `rsync`.
- Excludes internal drives (e.g., NVMe, HDDs) and specified folders.
- Logs actions to `/home/carlos/usb_backup.log` and the terminal.

## Prerequisites
- Python 3.x
- Required Python packages: `psutil` (`pip install psutil`)
- System tools: `rsync`, `lsblk`
- Arch Linux (or similar Linux distro) with KDE (for `/run/media/` mounts)

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/charlessheard/usb-backup-script.git
   cd usb-backup-script
Install Dependencies:
bash
pip install psutil
sudo pacman -S rsync  # If not already installed
Make Executable:
bash
chmod +x usb_backup.py
Run the Script:
bash
./usb_backup.py
Logs will appear in /home/carlos/usb_backup.log.
Backups will go to /home/carlos/USB_Backup/.
Configuration
Target Folder: Edit TARGET_FOLDER in the script (default: /home/carlos/USB_Backup/).
Excluded Folders: Modify EXCLUDED_FOLDERS (default: {"Backup_drv", "data"}).
Sleep Interval: Adjust SLEEP_INTERVAL (default: 15 seconds).
Usage
Run manually in a terminal to monitor USB insertions.
Plug in a USB drive; it will back up to /home/carlos/USB_Backup/[USB_NAME]/.
Check logs in /home/carlos/usb_backup.log for details.
Running as a Service (Optional)
Create a systemd service:
bash
sudo nano /etc/systemd/system/usb-backup.service
ini
[Unit]
Description=USB Backup Service
After=network.target

[Service]
ExecStart=/path/to/usb_backup.py
User=carlos
WorkingDirectory=/path/to/script/dir
Restart=on-failure
StandardOutput=journal

[Install]
WantedBy=multi-user.target
Enable and start:
bash
sudo systemctl daemon-reload
sudo systemctl enable usb-backup.service
sudo systemctl start usb-backup.service
Changelog
Initial Version
Used psutil.disk_partitions() to detect mounted devices.
Identified USBs with "removable" in partition.opts (unreliable).
Backed up to /home/carlos/USB_Backup/ with rsync.
No logs appeared; USB detection inconsistent.
Updates (Feb 23, 2025)
Logging Fix: Added absolute log path (/home/carlos/usb_backup.log) to ensure logs are written.
Detection Debug: Added logging.info to get_mountedlist() to list detected devices.
USB Identification: Replaced "removable" check with mountpoint.startswith("/run/media/"), but this copied internal drives (e.g., NVMe).
Final Version
Improved Identification:
Added is_removable() using lsblk -dno RM to check removability (RM=1 for USBs, RM=0 for internal).
Excluded NVMe devices (/dev/nvme*) explicitly.
Kept /run/media/ filter for KDE compatibility.
Result: Only backs up removable USBs (e.g., /dev/sdd1), ignoring internal drives (e.g., /dev/nvme0n1p1, /dev/sdb1).
Tested: Successfully backed up a USB drive on Arch Linux with KDE.
Troubleshooting
No Backup Happens: Check logs (/home/carlos/usb_backup.log) and ensure USB mounts under /run/media/ (KDE automount must be enabled).
Wrong Drives Backed Up: Verify lsblk -o NAME,RM output matches script logic.
Permissions: Ensure /home/carlos/USB_Backup/ is writable (chmod u+rwx /home/carlos/USB_Backup/).
License
MIT License - feel free to use and modify!
