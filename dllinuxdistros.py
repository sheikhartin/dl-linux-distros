#!/usr/bin/env python

from pathlib import Path
import subprocess
import sys
import csv
import hashlib

distros_dataset_filepath = Path('data/distros.csv')
distros_dataset_url = 'https://raw.githubusercontent.com/sheikhartin/dl-linux-distros/master/data/distros.csv'
# Download the distros data file if it doesn't exist or is empty.
if not distros_dataset_filepath.exists() or \
   distros_dataset_filepath.stat().st_size == 0:
    print('The distros data file does not exist. We will download it now...\n')
    distros_dataset_filepath.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['wget', '-q', '-O', str(distros_dataset_filepath),
                    distros_dataset_url])

# Show a list of available distros, if the user asked for it.
if len(sys.argv) > 1:
    if sys.argv[1] == '-l' or sys.argv[1] == '--list':
        print('distro | version | arch')
        for row in csv.DictReader(distros_dataset_filepath.open()):
            print(f'{row["distro"]} | {row["version"]} | {row["arch"]}')
        sys.exit(1)

required_distro = input('Enter the distribution name: ').lower().strip()
required_version = input('What version of the distribution? ').lower().strip()
required_arch = input('And the architecture? ').lower().strip()

# X86_64 is the same as AMD64.
if required_arch == 'x86_64':
    required_arch = 'amd64'

for record in csv.DictReader(distros_dataset_filepath.open()):
    if record['distro'] == required_distro and \
       record['version'] == required_version and \
       record['arch'] == required_arch:
        print('\nDownloading the ISO file... Press Ctrl+C to abort.')
        subprocess.run(['wget', '-c', '-O', f'{required_distro}-{required_version}-{required_arch}.iso',
                        record['url']])

        print('Verifying checksum...')
        filehash = getattr(hashlib, f'sha{record["shatype"]}')(
            Path(f'{required_distro}-{required_version}-{required_arch}.iso').read_bytes()
        ).hexdigest()

        if record['checksum'] == filehash:
            print('Checksum verified and the ISO file is ready.')
            sys.exit(0)
        else:
            print("Checksum verification failed! Please download the ISO file"
                  f"manually from {record['url']}.")
            sys.exit(1)
