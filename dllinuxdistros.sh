#!/bin/bash

dataset_filepath="data/distros.csv"
dataset_url="https://raw.githubusercontent.com/sheikhartin/dl-linux-distros/master/data/distros.csv"
# If the data file doesn't exist or is empty, it will be downloaded.
if [[ ! -e "${dataset_filepath}" ]] || [[ ! -s "${dataset_filepath}" ]]; then
  echo -e "The distros data file does not exist. We will download it now...\n"
  mkdir -p "$(dirname $dataset_filepath)"
  wget -q -O "${dataset_filepath}" "${dataset_url}"
fi

# Show a list of available distros if the user asked for it.
if [[ "${1}" =~ ^(-l|--list)$ ]]; then
  echo "distro | version | arch"
  tail -n +2 "${dataset_filepath}" | cut -d, -f1,2,3 \
    | while IFS="," read -r distro version arch; do
    echo "${distro} | ${version} | ${arch}"
  done
  exit 1
fi

input_distro="$(read -r -p "Distribution: "; echo "${REPLY,,}" | tr -d ' ')"
input_version="$(read -r -p "Version: "; echo "${REPLY,,}" | tr -d ' ')"
input_arch="$(read -r -p "Architecture: "; echo "${REPLY,,}" | tr -d ' ')"

# X86-64 is the same as AMD64. Read about the difference at:
# https://www.quora.com/what-is-the-difference-between-x86_64-and-amd64
if [[ "${input_arch}" == "x86-64" || "${input_arch}" == "x86_64" ]]; then
  input_arch="amd64"
fi

tail -n +2 "${dataset_filepath}" \
  | while IFS="," read -r distro version arch url checksum shatype; do
  if [[ "${distro}" == "${input_distro}" ]] \
    && [[ "${version}" == "${input_version}" ]] \
    && [[ "${arch}" == "${input_arch}" ]]; then
    echo -e "\nDownloading the ISO file... Press Ctrl+C to abort."
    wget -c -O "${distro}-${version}-${arch}.iso" "${url}"

    echo "Verifying checksum..."
    if [[ "${checksum}" == "$(shasum -a ${shatype} ${distro}-${version}-${arch}.iso \
      | cut -d ' ' -f 1)" ]]; then
      echo "Checksum verified and the ISO file is ready."
      exit 0
    else
      echo "Checksum verification failed! Download the ISO file manually from ${url}."
      exit 1
    fi
  fi
done
