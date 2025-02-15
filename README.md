# USB Auto-Backup

A Python daemon that automatically backs up USB drives when they're connected to your system. The script monitors for newly connected USB devices and creates a backup copy of their contents to a specified target folder, excluding designated directories.

## Features

- Automatic detection of newly connected USB devices
- Configurable backup destination
- Exclusion list for specific folders
- Comprehensive logging system
- Error handling and recovery
- Safe file operations using pathlib
- Type hints for better code maintainability

## Requirements

- Python 3.6+
- Linux-based system with `lsblk` command
- Read/write permissions for target backup directory

## Installation

1. Clone this repository:
```bash
git clone https://github.com/charlessheard/usb-auto-backup.git
cd usb-auto-backup
```

2. Make the script executable:
```bash
chmod +x usb_backup.py
```

## Configuration

Edit the following variables at the top of the script:

- `TARGET_FOLDER`: Directory where backups will be stored
- `EXCLUDED_FOLDERS`: Set of folder names to exclude from backup
- `SLEEP_INTERVAL`: Time between checks for new devices (in seconds)

## Usage

Run the script:
```bash
./usb_backup.py
```

The script will:
1. Start monitoring for new USB devices
2. Create backups automatically when devices are connected
3. Log all operations to both console and `usb_backup.log`

## Logging

Logs are written to:
- Console output
- `usb_backup.log` in the script directory

The log includes:
- Device connection events
- Backup operations
- Errors and warnings
- Script status updates

## License

MIT

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
