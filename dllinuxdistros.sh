#!/bin/bash

distros_dataset_filepath="data/distros.csv"
distros_dataset_url="https://raw.githubusercontent.com/sheikhartin/dl-linux-distros/master/data/distros.csv"
# Download the distros data file if it doesn't exist or is empty.
if [[ ! -e "${distros_dataset_filepath}" ]] \
  || [[ ! -s "${distros_dataset_filepath}" ]]; then
  echo -e "The distros data file does not exist. We will download it now...\n"
  mkdir -p "$(dirname $distros_dataset_filepath)"
  wget -q -O "${distros_dataset_filepath}" "${distros_dataset_url}"
fi

# Show a list of available distros, if the user asked for it.
if [[ "${1}" =~ ^(-l|--list)$ ]]; then
  echo "distro | version | arch"
  tail -n +2 "${distros_dataset_filepath}" | cut -d, -f1,2,3 \
    | while IFS="," read -r distro version arch; do
    echo "${distro} | ${version} | ${arch}"
  done
  exit 1
fi

required_distro="$(read -r -p "Enter the distribution name: "; echo "${REPLY,,}" | tr -d ' ')"
required_version="$(read -r -p "What version of the distribution? "; echo "${REPLY,,}" | tr -d ' ')"
required_arch="$(read -r -p "And the architecture? "; echo "${REPLY,,}" | tr -d ' ')"

# X86_64 is the same as AMD64.
if [[ "${required_arch}" == "x86_64" ]]; then
  required_arch="amd64"
fi

tail -n +2 "${distros_dataset_filepath}" \
  | while IFS="," read -r distro version arch url checksum shatype; do
  if [[ "${distro}" == "${required_distro}" ]] \
    && [[ "${version}" == "${required_version}" ]] \
    && [[ "${arch}" == "${required_arch}" ]]; then
    echo -e "\nDownloading the ISO file... Press Ctrl+C to abort."
    wget -c -O "${distro}-${version}-${arch}.iso" "${url}"

    echo "Verifying checksum..."
    if [[ "${checksum}" == "$(shasum -a ${shatype} ${distro}-${version}-${arch}.iso \
      | cut -d ' ' -f 1)" ]]; then
      echo "Checksum verified and the ISO file is ready."
      exit 0
    else
      echo "Checksum verification failed! Please download the ISO file manually from ${url}."
      exit 1
    fi
  fi
done
