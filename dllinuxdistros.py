#!/usr/bin/env python

import subprocess
import argparse
import sys
import csv
import hashlib
from pathlib import Path

dataset_filepath = Path('data/distros.csv')
dataset_url = 'https://raw.githubusercontent.com/sheikhartin/dl-linux-distros/master/data/distros.csv'
# If the data file doesn't exist or is empty, it will be downloaded.
if not dataset_filepath.exists() or dataset_filepath.stat().st_size == 0:
    print('The distros data file does not exist. We will download it now...\n')
    dataset_filepath.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'wget', '-q', '-O', str(dataset_filepath), dataset_url
    ])

parser = argparse.ArgumentParser(description='Download GNU/Linux distributions easily with this script.')
parser.add_argument('-d', '--distro', help='the distro to download')
parser.add_argument('-v', '--version', help='the version of the distro')
parser.add_argument('-a', '--arch', help='the architecture of the distro')
parser.add_argument('-l', '--list', action='store_true', help='show the list of distros')
args = parser.parse_args()

if args.list:
    print('distro | version | arch')
    for row in csv.DictReader(dataset_filepath.open()):
        print(f'{row["distro"]} | {row["version"]} | {row["arch"]}')
    sys.exit(1)
elif not args.distro or not args.version or not args.arch:
    parser.print_help()
    sys.exit(1)

input_distro = args.distro.lower()
input_version = args.version.lower()
input_arch = args.arch.lower()
# X86-64 is the same as AMD64. Read about the difference at:
# https://www.quora.com/what-is-the-difference-between-x86_64-and-amd64
if input_arch == 'x86-64' or input_arch == 'x86_64':
    input_arch = 'amd64'

for record in csv.DictReader(dataset_filepath.open()):
    if record['distro'] == input_distro and \
       record['version'] == input_version and \
       record['arch'] == input_arch:
        print('\nDownloading the ISO file... Press Ctrl+C to abort.')
        subprocess.run([
            'wget', '-c', '-O', f'{input_distro}-{input_version}-{input_arch}.iso', record['url']
        ])

        print('Verifying checksum...')
        filebytes = Path(f'{input_distro}-{input_version}-{input_arch}.iso').read_bytes()
        filehash = hashlib.new(f'sha{record["shatype"]}', filebytes).hexdigest()
        if record['checksum'] == filehash:
            print('Checksum verified and the ISO file is ready.')
            sys.exit(0)
        else:
            print(f'Checksum verification failed! Download the ISO file manually from {record["url"]}.')
            sys.exit(1)
