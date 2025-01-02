#!/usr/bin/env zsh

timestamp=$(date +%Y%m%d_%H%M%S)
folder="tmp/$timestamp"

mkdir -p tmp
mkdir -p "$folder"

if git archive --format=zip HEAD -o dotfiles.zip &>/dev/null; then
  if zip -q -r dotfiles.zip .git &>/dev/null; then
    mv dotfiles.zip "$folder"/
    echo "Successfully created and moved dotfiles.zip to $folder"
  else
    echo "Error: Failed to add .git directory to zip file"
    exit 1
  fi
else
  echo "Error: Failed to create git archive"
  exit 1
fi
