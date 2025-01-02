#!/usr/bin/env zsh

timestamp=$(date +%Y%m%d_%H%M%S)
folder="tmp/$timestamp"

mkdir -p tmp
mkdir -p "$folder"

if git archive --format=zip HEAD -o custom.zip &>/dev/null; then
  if zip -q -r custom.zip .git &>/dev/null; then
    mv custom.zip "$folder"/
    echo "Successfully created and moved custom.zip to $folder"
  else
    echo "Error: Failed to add .git directory to zip file"
    exit 1
  fi
else
  echo "Error: Failed to create git archive"
  exit 1
fi
